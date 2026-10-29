#!/usr/bin/env python3
"""D5 Transformer: shared pretrained encoder + two token heads (VALUE, CUE).

Frozen model-selection procedure (declared BEFORE training):
  - train split only; dev used solely for early-stopping model selection;
  - selection metric = mean(dev value micro-F1, dev cue micro-F1);
  - max 30 epochs, patience 5 evals; best weights kept; seeds recorded;
  - no hyperparameter search beyond this single fixed configuration
    (only the documented history ablation repeats the run).

Input pair (history=with):  [CLS] tail-of-history [SEP] utterance [SEP]
Input single (history=no):  [CLS] utterance [SEP]
Word->subtoken alignment is done by CHARACTER OFFSETS (never assumed), labels
on first subtoken of each word, other subtokens masked (-100).

Predictions decode to exact gold-char offsets -> scripts/evaluate_spans.py.
"""
from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402
import evaluate_spans  # noqa: E402

IGNORE = -100


class TwoHead(nn.Module):
    def __init__(self, model_name: str, n_value: int, n_cue: int):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = self.encoder.config.hidden_size
        self.v_head = nn.Linear(hidden, n_value)
        self.c_head = nn.Linear(hidden, n_cue)

    def forward(self, input_ids, attention_mask, token_type_ids):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask,
                           token_type_ids=token_type_ids)
        h = out.last_hidden_state
        return self.v_head(h), self.c_head(h)


def hist_tail(text: str, words: int) -> str:
    toks = text.split()
    return " ".join(toks[-words:]) if len(toks) > words else text


def build_example(row, tok, use_hist: bool, max_len: int, hist_words: int):
    """Returns (enc, v_labels, c_labels, word_positions) for one record."""
    utt = row["current_user_utterance"]
    words = row["_words"]  # [{'start','end','text'}...]
    v_tags, c_tags = row["_value_tags"], row["_cue_tags"]
    if use_hist:
        hist = " ".join(str(h.get("utterance", "")) for h in (row.get("history") or []))
        enc = tok(hist_tail(hist, hist_words), utt, truncation=True, max_length=max_len,
                  return_offsets_mapping=True)
        ttypes = enc.get("token_type_ids") or enc.get("type_ids")
        seg = [i for i, t in enumerate(ttypes) if t == 1]
    else:
        enc = tok(utt, truncation=True, max_length=max_len, return_offsets_mapping=True)
        seg = [i for i, (a, b) in enumerate(enc["offset_mapping"]) if b > a]
    off = enc["offset_mapping"]
    v_lab = [IGNORE] * len(enc["input_ids"])
    c_lab = [IGNORE] * len(enc["input_ids"])
    word_pos = [None] * len(words)  # subtoken index carrying each word's label
    misses = 0
    for wi, w in enumerate(words):
        cands = [i for i in seg if w["start"] <= off[i][0] < w["end"]]
        if not cands:
            if v_tags[wi] != "O" or c_tags[wi] != "O":
                misses += 1
            continue
        word_pos[wi] = cands[0]
        v_lab[cands[0]] = v_tags[wi]
        c_lab[cands[0]] = c_tags[wi]
    return enc, v_lab, c_lab, word_pos, misses


def collate(batch, pad_id):
    max_len = max(len(b[0]["input_ids"]) for b in batch)
    input_ids, attn, ttypes, vlab, clab = [], [], [], [], []
    for enc, v, c, _, _ in batch:
        n = len(enc["input_ids"])
        pad = max_len - n
        input_ids.append(enc["input_ids"] + [pad_id] * pad)
        attn.append([1] * n + [0] * pad)
        tt_src = enc.get("token_type_ids") or enc.get("type_ids") or [0] * n
        ttypes.append(list(tt_src) + [0] * pad)
        vlab.append(v + [IGNORE] * pad)
        clab.append(c + [IGNORE] * pad)
    return (torch.tensor(input_ids), torch.tensor(attn), torch.tensor(ttypes),
            torch.tensor(vlab), torch.tensor(clab))


def decode_word_tags(words, tags):
    spans, cur = [], None
    for w, tag in zip(words, tags):
        if tag.startswith("B-"):
            if cur:
                spans.append(cur)
            cur = {"start": w["start"], "end": w["end"], "label": tag[2:]}
        elif tag.startswith("I-") and cur and cur["label"] == tag[2:]:
            cur["end"] = w["end"]
        elif cur:
            spans.append(cur)
            cur = None
    if cur:
        spans.append(cur)
    return spans


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--model", default="bert-base-cased")
    ap.add_argument("--history", choices=["with", "no"], required=True)
    ap.add_argument("--seed", type=int, default=20261029)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--max-length", type=int, default=160)
    ap.add_argument("--hist-words", type=int, default=60)
    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load(p):
        return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]

    gold = {r["id"]: r for r in read_jsonl(args.gold)}
    train_raw, dev_raw = load(args.data / "train.jsonl"), load(args.data / "dev.jsonl")

    def attach(rows):
        out = []
        for r in rows:
            g = dict(gold[r["id"]])
            g["_words"] = r["tokens"]
            g["_value_tags"] = r["value_tags"]
            g["_cue_tags"] = r["cue_tags"]
            out.append(g)
        return out

    train, dev = attach(train_raw), attach(dev_raw)
    tok = AutoTokenizer.from_pretrained(args.model)

    v_tagset = sorted({t for r in train for t in r["_value_tags"]})
    c_tagset = sorted({t for r in train for t in r["_cue_tags"]})
    v_ix = {t: i for i, t in enumerate(v_tagset)}
    c_ix = {t: i for i, t in enumerate(c_tagset)}

    use_hist = args.history == "with"
    misses_total = 0
    train_ex, dev_ex = [], []
    for rows, out in ((train, train_ex), (dev, dev_ex)):
        for r in rows:
            enc, v, c, pos, miss = build_example(r, tok, use_hist, args.max_length, args.hist_words)
            misses_total += miss
            out.append((enc,
                        [v_ix.get(t, IGNORE) if isinstance(t, str) else IGNORE for t in v],
                        [c_ix.get(t, IGNORE) if isinstance(t, str) else IGNORE for t in c],
                        pos, r))
    print(f"alignment misses (labeled words without subtoken): {misses_total}")
    if misses_total:
        print("WARNING: alignment misses > 0")

    model = TwoHead(args.model, len(v_tagset), len(c_tagset)).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    ce = nn.CrossEntropyLoss(ignore_index=IGNORE)

    def run_epochs(examples):
        """One training pass over the examples; returns mean loss."""
        order = list(range(len(examples)))
        random.shuffle(order)
        total_loss, batches = 0.0, 0
        model.train()
        for k in range(0, len(order), args.batch):
            chunk = [examples[i] for i in order[k:k + args.batch]]
            ids, attn, tt, vl, cl = collate(chunk, tok.pad_token_id or 0)
            ids, attn, tt = ids.to(device), attn.to(device), tt.to(device)
            vl, cl = vl.to(device), cl.to(device)
            v_logits, c_logits = model(ids, attn, tt)
            loss = ce(v_logits.view(-1, v_logits.size(-1)), vl.view(-1)) + \
                   ce(c_logits.view(-1, c_logits.size(-1)), cl.view(-1))
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total_loss += loss.item()
            batches += 1
        return total_loss / max(batches, 1)

    def word_tags(pos, v_seq, c_seq):
        vt, ct = [], []
        for w in range(len(pos)):
            j = pos[w]
            vt.append(v_tagset[v_seq[j]] if j is not None else "O")
            ct.append(c_tagset[c_seq[j]] if j is not None else "O")
        return vt, ct

    def evaluate_dev():
        model.eval()
        out = {r["id"]: {"id": r["id"], "value_spans": [], "cue_spans": []} for r in dev}
        with torch.no_grad():
            for k in range(0, len(dev_ex), args.batch):
                chunk = dev_ex[k:k + args.batch]
                ids, attn, tt, vl, cl = collate(chunk, tok.pad_token_id or 0)
                ids, attn, tt = ids.to(device), attn.to(device), tt.to(device)
                v_logits, c_logits = model(ids, attn, tt)
                v_pred = v_logits.argmax(-1).cpu().tolist()
                c_pred = c_logits.argmax(-1).cpu().tolist()
                for bi, (_, _, _, pos, row) in enumerate(chunk):
                    utt = row["current_user_utterance"]
                    vt, ct = word_tags(pos, v_pred[bi], c_pred[bi])
                    for span in decode_word_tags(row["_words"], vt):
                        span["text"] = utt[span["start"]:span["end"]]
                        out[row["id"]]["value_spans"].append(span)
                    for span in decode_word_tags(row["_words"], ct):
                        span["text"] = utt[span["start"]:span["end"]]
                        out[row["id"]]["cue_spans"].append(span)
        dev_gold = sorted((gold[r["id"]] for r in dev_raw), key=lambda r: r["id"])
        preds = [out[r["id"]] for r in dev_gold]
        rep = evaluate_spans.evaluate(dev_gold, preds)
        vm = rep["layers"]["value_spans"]["micro"]["f1"] or 0.0
        cm = rep["layers"]["cue_spans"]["micro"]["f1"] or 0.0
        return rep, preds, (vm + cm) / 2

    t0 = time.time()
    best = {"score": -1.0, "epoch": -1, "state": None}
    stale = 0
    history_log = []
    for epoch in range(1, args.epochs + 1):
        random.shuffle(train_ex)
        tr_loss = run_epochs(train_ex)
        rep, preds, score = evaluate_dev()
        history_log.append({"epoch": epoch, "train_loss": round(tr_loss, 4),
                            "dev_value_f1": rep["layers"]["value_spans"]["micro"]["f1"],
                            "dev_cue_f1": rep["layers"]["cue_spans"]["micro"]["f1"],
                            "dev_score": round(score, 4)})
        print(f"epoch {epoch:02d} loss={tr_loss:.3f} value={history_log[-1]['dev_value_f1']} "
              f"cue={history_log[-1]['dev_cue_f1']} score={score:.4f}")
        if score > best["score"] + 1e-6:
            best = {"score": score, "epoch": epoch,
                    "state": copy.deepcopy({k: v.cpu() for k, v in model.state_dict().items()})}
            stale = 0
        else:
            stale += 1
            if stale >= args.patience:
                print(f"early stop at epoch {epoch} (best epoch {best['epoch']})")
                break

    model.load_state_dict(best["state"])
    model.to(device)
    rep, preds, score = evaluate_dev()

    args.outdir.mkdir(parents=True, exist_ok=True)
    tag = f"tf_h{args.history}"
    ckpt_path = args.outdir / f"checkpoint_{tag}.pt"
    torch.save({"state_dict": best["state"],
                "model_name": args.model,
                "v_tagset": v_tagset, "c_tagset": c_tagset,
                "history": args.history, "seed": args.seed,
                "max_length": args.max_length, "hist_words": args.hist_words,
                "best_epoch": best["epoch"], "dev_score": round(best["score"], 4)},
               ckpt_path)
    import hashlib as _h
    ckpt_sha = _h.sha256(ckpt_path.read_bytes()).hexdigest()
    (args.outdir / f"pred_{tag}_dev.jsonl").write_text(
        "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in preds), encoding="utf-8")
    rep["config"] = {
        "model": args.model, "history": args.history, "seed": args.seed,
        "epochs_max": args.epochs, "patience": args.patience, "batch": args.batch,
        "lr": args.lr, "weight_decay": 0.01, "max_length": args.max_length,
        "hist_words": args.hist_words, "selection": "best dev mean(value,cue) micro-F1",
        "best_epoch": best["epoch"], "best_score": round(best["score"], 4),
        "device": str(device), "torch": torch.__version__, "alignment_misses": misses_total,
        "v_tagset": v_tagset, "c_tagset": c_tagset, "epochs_run": history_log,
        "elapsed_sec": round(time.time() - t0, 1),
        "checkpoint": ckpt_path.name, "checkpoint_sha256": ckpt_sha,
    }
    (args.outdir / f"metrics_{tag}_dev.json").write_text(
        json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"best_epoch": best["epoch"], "score": round(best["score"], 4),
                      "value_micro_f1": rep["layers"]["value_spans"]["micro"]["f1"],
                      "cue_micro_f1": rep["layers"]["cue_spans"]["micro"]["f1"],
                      "elapsed_sec": round(time.time() - t0, 1),
                      "device": str(device)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
