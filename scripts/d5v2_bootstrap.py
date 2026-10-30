#!/usr/bin/env python3
"""Family-bootstrap 95% interval of S(B) - S(A) from two pooled out-of-fold prediction files
(reports/D5V2_PROTOCOL.md section 5). Families are resampled with replacement; strict exact-span micro-F1 per layer.
The point estimate is checked against evaluate_spans.py before resampling.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate_spans  # noqa: E402
from validate_annotations import read_jsonl  # noqa: E402

LAYERS = ("value_spans", "cue_spans")


def counts(gold: dict, pred: dict) -> dict:
    """Per-layer (tp, n_pred, n_gold) for one record."""
    out = {}
    for layer in LAYERS:
        g = {(s["start"], s["end"], s["label"]) for s in gold[layer]}
        p = {(s["start"], s["end"], s["label"]) for s in pred[layer]}
        out[layer] = (len(g & p), len(p), len(g))
    return out


def score(per_record: list[dict]) -> float:
    f1s = []
    for layer in LAYERS:
        tp = sum(c[layer][0] for c in per_record)
        np_ = sum(c[layer][1] for c in per_record)
        ng = sum(c[layer][2] for c in per_record)
        f1s.append(2 * tp / (np_ + ng) if np_ + ng else 0.0)
    return sum(f1s) / 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--a", type=Path, required=True, help="reference configuration OOF predictions")
    ap.add_argument("--b", type=Path, required=True, help="compared configuration OOF predictions")
    ap.add_argument("--resamples", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261102)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--accept-consensus-reference", action="store_true",
                    help="score against the DEV-001 consensus test reference (official dev/test splits)")
    args = ap.parse_args()
    eval_kw = ({"accept_consensus": True, "allowed_splits": ("train", "dev", "test")}
               if args.accept_consensus_reference else {})

    gold = read_jsonl(args.gold)
    pa = {r["id"]: r for r in read_jsonl(args.a)}
    pb = {r["id"]: r for r in read_jsonl(args.b)}
    if set(pa) != set(pb) or set(pa) != {g["id"] for g in gold}:
        raise SystemExit("prediction ids do not match gold ids")
    fam = defaultdict(list)
    for g in gold:
        fam[str(g.get("dialogue_family_id") or g["source"]["dialogue_id"])].append(
            (counts(g, pa[g["id"]]), counts(g, pb[g["id"]])))

    point = {}
    for name, preds in (("a", pa), ("b", pb)):
        rep = evaluate_spans.evaluate(gold, [preds[g["id"]] for g in gold], **eval_kw)
        ref = sum((rep["layers"][l]["micro"]["f1"] or 0.0) for l in LAYERS) / 2
        mine = score([c[0 if name == "a" else 1] for recs in fam.values() for c in recs])
        if abs(ref - mine) > 1e-5:  # evaluate_spans rounds F1 to 6 decimals
            raise SystemExit(f"scorer mismatch for {name}: {ref} vs {mine}")
        point[name] = ref

    rng = random.Random(args.seed)
    keys = sorted(fam)
    diffs = []
    for _ in range(args.resamples):
        sample = [c for k in (rng.choice(keys) for _ in keys) for c in fam[k]]
        diffs.append(score([c[1] for c in sample]) - score([c[0] for c in sample]))
    diffs.sort()
    lo, hi = diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]
    result = {"a": str(args.a), "b": str(args.b), "S_a": round(point["a"], 4), "S_b": round(point["b"], 4),
              "diff_b_minus_a": round(point["b"] - point["a"], 4), "ci95": [round(lo, 4), round(hi, 4)],
              "families": len(keys), "records": len(gold), "resamples": args.resamples, "seed": args.seed,
              "share_of_resamples_b_better": round(sum(d > 0 for d in diffs) / len(diffs), 3)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
