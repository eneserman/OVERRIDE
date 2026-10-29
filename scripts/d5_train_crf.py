#!/usr/bin/env python3
"""D5 linear-chain CRF (per head: VALUE and CUE) on frozen tokenized data.

Usage:
  python scripts/d5_train_crf.py --data data/intermediate/d5 \
      --gold data/gold/train_dev_gold_v1.jsonl --outdir reports/train_runs/d5_crf \
      [--with-history | --no-history]

- Labels/tags come ONLY from train BIO tags (dev never influences training).
- History feature = token appears in the dialogue history utterances (ablation
  flag switches it off; identical example IDs in both conditions).
- Predictions are decoded to exact char offsets and evaluated with
  scripts/evaluate_spans.py against the frozen dev gold.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

import sklearn_crfsuite

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402
import evaluate_spans  # noqa: E402

TIME_RE = re.compile(r"^\d{1,2}[:.]\d{2}$|^\d{1,2}[ap]m?$", re.I)
SHAPE = re.compile(r"[A-Z]")


def word_features(tokens: list[dict], i: int, history: str, use_history: bool) -> dict:
    w = tokens[i]["text"]
    feats = {
        "bias": 1.0,
        "w.lower": w.lower(),
        "w.len": min(len(w), 12),
        "w.isdigit": w.isdigit(),
        "w.isupper": w.isupper(),
        "w.istitle": w.istitle(),
        "w.hasShape": bool(SHAPE.search(w)),
        "w.isTime": bool(TIME_RE.match(w)),
        "w.suffix1": w.lower()[-1:],
        "w.suffix2": w.lower()[-2:],
        "w.prefix1": w.lower()[:1],
        "w.prefix2": w.lower()[:2],
        "BOS": i == 0,
        "EOS": i == len(tokens) - 1,
    }
    if use_history:
        feats["w.inHistory"] = w.lower() in history
    for d in (-1, -2, 1, 2):
        j = i + d
        if 0 <= j < len(tokens):
            feats[f"w{d}.lower"] = tokens[j]["text"].lower()
            feats[f"w{d}.istitle"] = tokens[j]["text"].istitle()
        else:
            feats[f"w{d}.lower"] = "<END>"
    return feats


def decode(tokens: list[dict], tags: list[str]) -> list[dict]:
    spans, cur = [], None
    for tok, tag in zip(tokens, tags):
        if tag.startswith("B-"):
            if cur:
                spans.append(cur)
            cur = {"start": tok["start"], "end": tok["end"], "label": tag[2:]}
        elif tag.startswith("I-") and cur and cur["label"] == tag[2:]:
            cur["end"] = tok["end"]
        elif cur:
            spans.append(cur)
            cur = None
    if cur:
        spans.append(cur)
    for s in spans:
        s["text"] = None
    return spans


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--history", choices=["with", "no"], default="with")
    ap.add_argument("--c1", type=float, default=0.1)
    ap.add_argument("--max-iter", type=int, default=200)
    args = ap.parse_args()

    def load(p: Path):
        return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]

    train = load(args.data / "train.jsonl")
    dev = load(args.data / "dev.jsonl")
    gold = {r["id"]: r for r in read_jsonl(args.gold)}
    use_hist = args.history == "with"

    def hist_text(rid: str) -> str:
        return " ".join(str(h.get("utterance", "")) for h in (gold[rid].get("history") or [])).lower()

    heads = {
        "value_spans": "value_tags",
        "cue_spans": "cue_tags",
    }
    args.outdir.mkdir(parents=True, exist_ok=True)
    summary = {"config": {"c1": args.c1, "max_iter": args.max_iter,
                          "history": args.history, "features": "word/prefix/suffix/shape/ctx"},
               "heads": {}}
    preds_out = {rid: {"id": rid, "value_spans": [], "cue_spans": []} for rid in gold}

    for head, tag_key in heads.items():
        tags_train = sorted({t for r in train for t in r[tag_key]})
        X_train = [[word_features(r["tokens"], i, hist_text(r["id"]), use_hist)
                    for i in range(len(r["tokens"]))] for r in train]
        y_train = [r[tag_key] for r in train]
        X_dev = [[word_features(r["tokens"], i, hist_text(r["id"]), use_hist)
                  for i in range(len(r["tokens"]))] for r in dev]

        model = sklearn_crfsuite.CRF(
            algorithm="lbfgs", c1=args.c1, c2=0.1, max_iterations=args.max_iter,
            all_possible_transitions=True)
        model.fit(X_train, y_train)

        for r, feats in zip(dev, X_dev):
            seq = model.predict([feats])[0]
            spans = decode(r["tokens"], seq)
            for s in spans:
                s["text"] = r["tokens"][0]["text"]  # placeholder replaced below
            # fill exact text from gold utterance
            utt = gold[r["id"]]["current_user_utterance"]
            clean = []
            for s in spans:
                if 0 <= s["start"] < s["end"] <= len(utt):
                    s["text"] = utt[s["start"]:s["end"]]
                    clean.append(s)
            preds_out[r["id"]][head] = clean

        summary["heads"][head] = {"train_tag_inventory": tags_train,
                                  "train_sequences": len(X_train)}

    dev_gold = sorted([gold[r["id"]] for r in dev], key=lambda r: r["id"])
    preds = [preds_out[r["id"]] for r in dev_gold]
    pred_path = args.outdir / f"pred_crf_h{args.history}_dev.jsonl"
    pred_path.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in preds),
                         encoding="utf-8")
    rep = evaluate_spans.evaluate(dev_gold, preds)
    rep["config"] = summary["config"]
    rep["heads"] = summary["heads"]
    out_path = args.outdir / f"metrics_crf_h{args.history}_dev.json"
    out_path.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "config": summary["config"],
        "value_micro_f1": rep["layers"]["value_spans"]["micro"]["f1"],
        "value_macro": rep["layers"]["value_spans"]["macro_f1_on_gold_supported_classes"],
        "cue_micro_f1": rep["layers"]["cue_spans"]["micro"]["f1"],
        "cue_macro": rep["layers"]["cue_spans"]["macro_f1_on_gold_supported_classes"],
        "out": str(out_path),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
