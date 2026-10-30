#!/usr/bin/env python3
"""Error taxonomy for span predictions against gold (development side only: out-of-fold CV predictions).

Every gold span and every predicted span that is not an exact (start, end, label) match is put in one class:
  boundary  : overlaps a span of the same label, but the offsets differ
  label     : same offsets, different label
  overlap   : overlaps a span with a different label and different offsets
  missed    : gold span with no overlapping prediction
  spurious  : predicted span with no overlapping gold span
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402

LAYERS = ("value_spans", "cue_spans")


def overlaps(a: dict, b: dict) -> bool:
    return a["start"] < b["end"] and b["start"] < a["end"]


def classify(span: dict, others: list[dict]) -> str:
    if any(o["start"] == span["start"] and o["end"] == span["end"] and o["label"] == span["label"] for o in others):
        return "exact"
    if any(o["start"] == span["start"] and o["end"] == span["end"] for o in others):
        return "label"
    if any(overlaps(span, o) and o["label"] == span["label"] for o in others):
        return "boundary"
    if any(overlaps(span, o) for o in others):
        return "overlap"
    return "missing"


def analyse(gold: list[dict], preds: dict[str, dict], n_examples: int = 3) -> dict:
    counts = defaultdict(Counter)
    examples = defaultdict(list)
    for g in gold:
        p = preds[g["id"]]
        utt = g["current_user_utterance"]
        for layer in LAYERS:
            for s in g[layer]:
                c = classify(s, p[layer])
                kind = "missed" if c == "missing" else c
                counts[s["label"]][kind] += 1
                if kind != "exact" and len(examples[(s["label"], kind)]) < n_examples:
                    near = [f"{o['label']}:'{utt[o['start']:o['end']]}'" for o in p[layer] if overlaps(s, o)]
                    examples[(s["label"], kind)].append(
                        {"id": g["id"], "utterance": utt, "gold": utt[s["start"]:s["end"]], "pred": near})
            for s in p[layer]:
                if classify(s, g[layer]) == "missing":
                    counts[s["label"]]["spurious"] += 1
                    if len(examples[(s["label"], "spurious")]) < n_examples:
                        examples[(s["label"], "spurious")].append(
                            {"id": g["id"], "utterance": utt, "gold": None, "pred": [utt[s["start"]:s["end"]]]})
    return {"counts": {lab: dict(c) for lab, c in sorted(counts.items())},
            "examples": {f"{lab}|{kind}": ex for (lab, kind), ex in sorted(examples.items())}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--pred", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    gold = read_jsonl(args.gold)
    preds = {r["id"]: r for r in read_jsonl(args.pred)}
    if set(preds) != {g["id"] for g in gold}:
        raise SystemExit("prediction ids do not match gold ids")
    result = analyse(gold, preds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
