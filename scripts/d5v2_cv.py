#!/usr/bin/env python3
"""D5-v2 grouped 5-fold cross-validation (pre-registered in reports/D5V2_PROTOCOL.md).

One run = one configuration (encoder, history mode, loss). Every fold trains on the other four folds for a fixed
number of epochs; after each epoch the held fold is predicted. Out-of-fold predictions of all records are pooled and
scored per epoch with evaluate_spans.py: S(e) = mean(VALUE micro-F1, CUE micro-F1). No early stopping on held data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate_spans  # noqa: E402
from d5_prepare_data import bio_tags  # noqa: E402
from d5_train_transformer import TwoHead, decode_word_tags  # noqa: E402
from span_tokenizer import tokenize  # noqa: E402
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402

IGNORE = -100
FOLD_SALT = "20261101"


def fold_of(family: str, k: int = 5) -> int:
    return int(hashlib.sha256(f"{FOLD_SALT}::{family}".encode()).hexdigest()[:8], 16) % k


def history_text(row: dict, mode: str) -> str | None:
    hist = row.get("history") or []
    if mode == "no":
        return None
    if mode == "last_system":
        sys_turns = [h for h in hist if h.get("speaker") == "SYSTEM"]
        return f"SYSTEM: {sys_turns[-1]['utterance']}" if sys_turns else None
    if mode == "tail60":
        words = " ".join(str(h.get("utterance", "")) for h in hist).split()
        return " ".join(words[-60:]) if words else None
    raise ValueError(mode)


def encode(row: dict, tok, mode: str, max_len: int):
    """Returns (enc, word_positions, misses) with labels aligned to the first sub-token of each word."""
    utt = row["current_user_utterance"]
    words = row["_words"]
    hist = history_text(row, mode)
    if hist:
        enc = tok(hist, utt, truncation="only_first", max_length=max_len, return_offsets_mapping=True)
        utt_seq = 1
    else:
        enc = tok(utt, truncation=True, max_length=max_len, return_offsets_mapping=True)
        utt_seq = 0
    seq_ids, off = enc.sequence_ids(), enc["offset_mapping"]
    pos, misses = [None] * len(words), 0
    for wi, w in enumerate(words):
        # first sub-token that overlaps the word (SentencePiece offsets may include the leading space)
        cands = [i for i, sid in enumerate(seq_ids) if sid == utt_seq and off[i][1] > off[i][0]
                 and off[i][0] < w["end"] and off[i][1] > w["start"]]
        if cands:
            pos[wi] = cands[0]
        elif row["_v"][wi] != "O" or row["_c"][wi] != "O":
            misses += 1
    return enc, pos, misses


def collate(items, pad_id: int, device):
    n = max(len(e["input_ids"]) for e, *_ in items)
    ids = torch.full((len(items), n), pad_id, dtype=torch.long)
    attn = torch.zeros((len(items), n), dtype=torch.long)
    vl = torch.full((len(items), n), IGNORE, dtype=torch.long)
    cl = torch.full((len(items), n), IGNORE, dtype=torch.long)
    for b, (enc, pos, v_idx, c_idx) in enumerate(items):
        L = len(enc["input_ids"])
        ids[b, :L] = torch.tensor(enc["input_ids"])
        attn[b, :L] = 1
        for wi, p in enumerate(pos):
            if p is not None:
                vl[b, p], cl[b, p] = v_idx[wi], c_idx[wi]
    tt = torch.zeros_like(ids)
    return ids.to(device), attn.to(device), tt.to(device), vl.to(device), cl.to(device)


def spans_from(row, pos, v_pred, c_pred, v_tags, c_tags):
    utt, words = row["current_user_utterance"], row["_words"]
    vt = [v_tags[v_pred[p]] if p is not None else "O" for p in pos]
    ct = [c_tags[c_pred[p]] if p is not None else "O" for p in pos]
    out = {"id": row["id"], "value_spans": [], "cue_spans": []}
    for layer, tags in (("value_spans", vt), ("cue_spans", ct)):
        for s in decode_word_tags(words, tags):
            s["text"] = utt[s["start"]:s["end"]]
            out[layer].append(s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--history", choices=["no", "last_system", "tail60"], required=True)
    ap.add_argument("--loss", choices=["plain", "weighted"], required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20261029)
    ap.add_argument("--limit-folds", type=int, default=None, help="smoke test only: run this many folds")
    ap.add_argument("--extra-train", type=Path, default=None,
                    help="records added to every training fold and never scored (declared synthetic data)")
    ap.add_argument("--save-epoch", type=int, nargs="*", default=[], help="also write the OOF predictions of these epochs")
    args = ap.parse_args()
    name = f"{args.model.split('/')[-1]}__{args.history}__{args.loss}" + ("__extra" if args.extra_train else "")
    out = args.outdir / name
    if (out / "cv_result.json").exists():
        raise SystemExit(f"ABORT: result exists for {name}")
    out.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    gold = read_jsonl(args.gold)
    v_tags = ["O"] + sorted(f"{p}-{l}" for l in VALUE_LABELS for p in "BI")
    c_tags = ["O"] + sorted(f"{p}-{l}" for l in CUE_LABELS for p in "BI")
    v_ix, c_ix = {t: i for i, t in enumerate(v_tags)}, {t: i for i, t in enumerate(c_tags)}
    tok = AutoTokenizer.from_pretrained(args.model)
    max_len = 160 if args.history == "no" else 192
    extra = read_jsonl(args.extra_train) if args.extra_train else []
    extra_ids = {x["id"] for x in extra}
    if {g["id"] for g in gold} & extra_ids:
        raise SystemExit("ABORT: extra-train IDs overlap the gold")
    rows, misses, collisions = [], 0, 0
    for g in gold + extra:
        r = dict(g)
        r["_words"] = [t._asdict() for t in tokenize(g["current_user_utterance"])]
        toks = tokenize(g["current_user_utterance"])
        r["_v"], vp = bio_tags(toks, g["value_spans"], VALUE_LABELS)
        r["_c"], cp = bio_tags(toks, g["cue_spans"], CUE_LABELS)
        if vp or cp:
            raise SystemExit(f"{g['id']}: BIO problems {vp + cp}")
        enc, pos, m = encode(r, tok, args.history, max_len)
        misses += m
        shared = [p for p in pos if p is not None]
        collisions += sum(1 for wi, p in enumerate(pos) if p is not None and shared.count(p) > 1
                          and (r["_v"][wi] != "O" or r["_c"][wi] != "O"))
        r["_enc"], r["_pos"] = enc, pos
        r["_fold"] = fold_of(str(g.get("dialogue_family_id") or g["source"]["dialogue_id"]), args.folds)
        if g["id"] in extra_ids:
            r["_fold"] = -1  # always in training, never held out
        rows.append(r)
    if misses:
        raise SystemExit(f"alignment misses: {misses} (labeled words without a sub-token)")

    weight_v = weight_c = None
    if args.loss == "weighted":
        weight_v = torch.tensor([1.0] + [3.0] * (len(v_tags) - 1), device=device)
        weight_c = torch.tensor([1.0] + [3.0] * (len(c_tags) - 1), device=device)
    ce_v = nn.CrossEntropyLoss(weight=weight_v, ignore_index=IGNORE)
    ce_c = nn.CrossEntropyLoss(weight=weight_c, ignore_index=IGNORE)

    oof = {e: {} for e in range(1, args.epochs + 1)}
    t0 = time.time()
    folds = list(range(args.folds))[: args.limit_folds] if args.limit_folds else list(range(args.folds))
    for k in folds:
        seed = args.seed + k
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        train = [r for r in rows if r["_fold"] != k]
        held = [r for r in rows if r["_fold"] == k]
        item = lambda r: (r["_enc"], r["_pos"], [v_ix[t] for t in r["_v"]], [c_ix[t] for t in r["_c"]])
        model = TwoHead(args.model, len(v_tags), len(c_tags)).float().to(device)  # fp32 (some hub weights load as fp16)
        opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
        for epoch in range(1, args.epochs + 1):
            model.train()
            order = list(range(len(train)))
            random.shuffle(order)
            for s in range(0, len(order), 16):
                ids, attn, tt, vl, cl = collate([item(train[i]) for i in order[s:s + 16]], tok.pad_token_id or 0, device)
                v_log, c_log = model(ids, attn, tt)
                loss = ce_v(v_log.view(-1, v_log.size(-1)), vl.view(-1)) + ce_c(c_log.view(-1, c_log.size(-1)), cl.view(-1))
                opt.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                opt.step()
            model.eval()
            with torch.no_grad():
                for s in range(0, len(held), 32):
                    chunk = held[s:s + 32]
                    ids, attn, tt, _, _ = collate([item(r) for r in chunk], tok.pad_token_id or 0, device)
                    v_log, c_log = model(ids, attn, tt)
                    vp, cp = v_log.argmax(-1).cpu().tolist(), c_log.argmax(-1).cpu().tolist()
                    for b, r in enumerate(chunk):
                        oof[epoch][r["id"]] = spans_from(r, r["_pos"], vp[b], cp[b], v_tags, c_tags)
            print(f"[{name}] fold {k} epoch {epoch} done ({time.time() - t0:.0f}s)", flush=True)
        del model, opt
        torch.cuda.empty_cache()

    scored_ids = {r["id"] for r in rows if r["_fold"] in folds}
    gold_scored = [g for g in gold if g["id"] in scored_ids]
    per_epoch = []
    for e in range(1, args.epochs + 1):
        rep = evaluate_spans.evaluate(gold_scored, [oof[e][g["id"]] for g in gold_scored])
        v = rep["layers"]["value_spans"]["micro"]["f1"] or 0.0
        c = rep["layers"]["cue_spans"]["micro"]["f1"] or 0.0
        per_epoch.append({"epoch": e, "value_f1": round(v, 4), "cue_f1": round(c, 4), "S": round((v + c) / 2, 4),
                          "per_label": {lay: {lab: d.get("f1") for lab, d in rep["layers"][lay].get("per_label", {}).items()}
                                        for lay in ("value_spans", "cue_spans")}})
    best = max(per_epoch, key=lambda x: (x["S"], -x["epoch"]))
    for e in sorted({best["epoch"], *args.save_epoch}):
        (out / f"oof_epoch{e}.jsonl").write_text(
            "".join(json.dumps(oof[e][g["id"]], ensure_ascii=False) + "\n" for g in gold_scored), encoding="utf-8")
    result = {"config": {"model": args.model, "history": args.history, "loss": args.loss, "epochs": args.epochs,
                         "folds": args.folds, "fold_salt": FOLD_SALT, "seed": args.seed, "max_len": max_len,
                         "lr": 2e-5, "batch": 16, "weight_decay": 0.01, "scored_folds": folds,
                         "extra_train": str(args.extra_train) if args.extra_train else None,
                         "extra_train_records": len(extra)},
              "alignment": {"misses": misses, "labeled_words_sharing_a_subtoken": collisions},
              "records_scored": len(gold_scored), "per_epoch": per_epoch, "best": best,
              "gold_sha256": hashlib.sha256(args.gold.read_bytes()).hexdigest(),
              "elapsed_sec": round(time.time() - t0, 1), "device": str(device), "torch": torch.__version__}
    (out / "cv_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"config": name, "best_epoch": best["epoch"], "S": best["S"], "value_f1": best["value_f1"],
                      "cue_f1": best["cue_f1"], "elapsed_sec": result["elapsed_sec"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
