#!/usr/bin/env python3
"""D5-v2 final model (reports/D5V2_PROTOCOL.md section 4): train and predict.

  train   : one seed of the selected configuration on ALL train-side gold for E* epochs (no held data, no selection).
  predict : average the per-tag softmax of several `train` checkpoints and decode spans for any input JSONL.

Encoding, alignment and decoding are imported from d5v2_cv.py, so the final model sees inputs exactly as in CV.
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
from d5_prepare_data import bio_tags  # noqa: E402
from d5_train_transformer import TwoHead  # noqa: E402
from d5v2_cv import collate, encode, spans_from  # noqa: E402
from span_tokenizer import tokenize  # noqa: E402
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402

V_TAGS = ["O"] + sorted(f"{p}-{l}" for l in VALUE_LABELS for p in "BI")
C_TAGS = ["O"] + sorted(f"{p}-{l}" for l in CUE_LABELS for p in "BI")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def prepare(rows: list[dict], tok, history: str, max_len: int, labeled: bool) -> tuple[list[dict], int]:
    out, misses = [], 0
    for g in rows:
        r = dict(g)
        toks = tokenize(g["current_user_utterance"])
        r["_words"] = [t._asdict() for t in toks]
        if labeled:
            r["_v"], vp = bio_tags(toks, g["value_spans"], VALUE_LABELS)
            r["_c"], cp = bio_tags(toks, g["cue_spans"], CUE_LABELS)
            if vp or cp:
                raise SystemExit(f"{g['id']}: BIO problems {vp + cp}")
        else:
            r["_v"] = r["_c"] = ["O"] * len(toks)
        r["_enc"], r["_pos"], m = encode(r, tok, history, max_len)
        misses += m
        out.append(r)
    return out, misses


def train(args) -> int:
    ckpt_path = args.outdir / f"final_seed{args.seed}.pt"
    if ckpt_path.exists():
        raise SystemExit(f"ABORT: checkpoint exists: {ckpt_path}")
    args.outdir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed); torch.cuda.manual_seed_all(args.seed)

    gold = read_jsonl(args.gold)
    tok = AutoTokenizer.from_pretrained(args.model)
    max_len = 160 if args.history == "no" else 192
    rows, misses = prepare(gold, tok, args.history, max_len, labeled=True)
    if misses:
        raise SystemExit(f"alignment misses: {misses}")
    v_ix, c_ix = {t: i for i, t in enumerate(V_TAGS)}, {t: i for i, t in enumerate(C_TAGS)}
    item = lambda r: (r["_enc"], r["_pos"], [v_ix[t] for t in r["_v"]], [c_ix[t] for t in r["_c"]])

    w_v = w_c = None
    if args.loss == "weighted":
        w_v = torch.tensor([1.0] + [3.0] * (len(V_TAGS) - 1), device=device)
        w_c = torch.tensor([1.0] + [3.0] * (len(C_TAGS) - 1), device=device)
    ce_v = nn.CrossEntropyLoss(weight=w_v, ignore_index=-100)
    ce_c = nn.CrossEntropyLoss(weight=w_c, ignore_index=-100)

    model = TwoHead(args.model, len(V_TAGS), len(C_TAGS)).float().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    t0 = time.time()
    for epoch in range(1, args.epochs + 1):
        model.train()
        order = list(range(len(rows)))
        random.shuffle(order)
        for s in range(0, len(order), 16):
            ids, attn, tt, vl, cl = collate([item(rows[i]) for i in order[s:s + 16]], tok.pad_token_id or 0, device)
            v_log, c_log = model(ids, attn, tt)
            loss = ce_v(v_log.view(-1, v_log.size(-1)), vl.view(-1)) + ce_c(c_log.view(-1, c_log.size(-1)), cl.view(-1))
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
        print(f"[seed {args.seed}] epoch {epoch}/{args.epochs} done ({time.time() - t0:.0f}s)", flush=True)

    meta = {"model": args.model, "model_revision": getattr(model.encoder.config, "_commit_hash", None),
            "history": args.history, "loss": args.loss, "epochs": args.epochs, "seed": args.seed, "max_len": max_len,
            "v_tags": V_TAGS, "c_tags": C_TAGS, "gold_sha256": sha256_file(args.gold), "records": len(rows),
            "lr": 2e-5, "batch": 16, "weight_decay": 0.01, "torch": torch.__version__, "device": str(device),
            "elapsed_sec": round(time.time() - t0, 1)}
    torch.save({"state_dict": model.state_dict(), "meta": meta}, ckpt_path)
    meta["checkpoint"] = str(ckpt_path)
    meta["checkpoint_sha256"] = sha256_file(ckpt_path)
    (args.outdir / f"final_seed{args.seed}.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: meta[k] for k in ("seed", "epochs", "checkpoint_sha256", "model_revision", "elapsed_sec")}))
    return 0


def predict(args) -> int:
    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite: {args.out}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpts = [torch.load(p, map_location="cpu", weights_only=False) for p in args.checkpoints]
    metas = [c["meta"] for c in ckpts]
    keys = ("model", "history", "loss", "epochs", "max_len", "v_tags", "c_tags")
    if any(any(m[k] != metas[0][k] for k in keys) for m in metas):
        raise SystemExit("checkpoints disagree on configuration")
    m0 = metas[0]
    tok = AutoTokenizer.from_pretrained(m0["model"])
    rows, misses = prepare(read_jsonl(args.input), tok, m0["history"], m0["max_len"], labeled=False)
    if len({r["id"] for r in rows}) != len(rows):
        raise SystemExit("duplicate ids in input")

    v_sum, c_sum = {}, {}
    for ck in ckpts:
        model = TwoHead(m0["model"], len(m0["v_tags"]), len(m0["c_tags"])).float()
        model.load_state_dict(ck["state_dict"])
        model.to(device).eval()
        with torch.no_grad():
            for s in range(0, len(rows), 32):
                chunk = rows[s:s + 32]
                dummy = [(r["_enc"], r["_pos"], [0] * len(r["_pos"]), [0] * len(r["_pos"])) for r in chunk]
                ids, attn, tt, _, _ = collate(dummy, tok.pad_token_id or 0, device)
                v_log, c_log = model(ids, attn, tt)
                vp, cp = v_log.softmax(-1).cpu(), c_log.softmax(-1).cpu()
                for b, r in enumerate(chunk):
                    v_sum[r["id"]] = v_sum.get(r["id"], 0) + vp[b]
                    c_sum[r["id"]] = c_sum.get(r["id"], 0) + cp[b]
        del model
        torch.cuda.empty_cache()

    preds = [spans_from(r, r["_pos"], v_sum[r["id"]].argmax(-1).tolist(), c_sum[r["id"]].argmax(-1).tolist(),
                        m0["v_tags"], m0["c_tags"]) for r in rows]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in preds), encoding="utf-8")
    print(json.dumps({"status": "PREDICTED", "examples": len(preds), "unaligned_words": misses,
                      "checkpoint_sha256": [sha256_file(p) for p in args.checkpoints],
                      "input_sha256": sha256_file(args.input), "predictions_sha256": sha256_file(args.out),
                      "out": str(args.out)}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--gold", type=Path, required=True)
    t.add_argument("--model", required=True)
    t.add_argument("--history", choices=["no", "last_system", "tail60"], required=True)
    t.add_argument("--loss", choices=["plain", "weighted"], required=True)
    t.add_argument("--epochs", type=int, required=True)
    t.add_argument("--seed", type=int, required=True)
    t.add_argument("--outdir", type=Path, required=True)
    p = sub.add_parser("predict")
    p.add_argument("--checkpoints", type=Path, nargs="+", required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    return train(args) if args.cmd == "train" else predict(args)


if __name__ == "__main__":
    raise SystemExit(main())
