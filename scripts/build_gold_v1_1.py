#!/usr/bin/env python3
"""Build gold v1.1 from gold v1 + the three locked joint decisions (reports/D3_GOLD_V1_1_DECISIONS.md).

Only A1, A3 and A4 change; every other row must stay byte-identical. Each change is
asserted against the exact expected v1 state before it is applied (fail-closed), and
the result must pass the gold validator. Gold v1 is never modified.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl, validate_rows  # noqa: E402

LOG_ID = "D3-ADJ-2026-10-30-V1_1"
NOTE = "v1.1: joint decision D3-V1_1 (reports/D3_GOLD_V1_1_DECISIONS.md)"

# id -> (expected v1 VALUE spans, v1.1 VALUE spans); spans are (label, start, end, text); cue layer must not change.
CHANGES = {
    "SGD-7bb4b2f1283e503502": (  # A1, F1: `with + N` is split
        [("NEW_VALUE", 20, 40, "a hotel with 3 rooms")],
        [("NEW_VALUE", 20, 27, "a hotel"), ("NEW_VALUE", 33, 40, "3 rooms")]),
    "sgd_3324bf1e7d2ec8ca4acf": (  # A3, C6: reference to the earlier day in a non-revision sentence
        [("KEPT_VALUE", 41, 53, "the same day")],
        [("REFERENCE", 41, 53, "the same day")]),
    "SGD-90cfacf6a275f8d7f3": (  # A4, C6: only the label of `the same day` changes
        [("NEW_VALUE", 10, 25, "Jojo restaurant"), ("KEPT_VALUE", 26, 38, "the same day"),
         ("NEW_VALUE", 42, 53, "afternoon 1"), ("NEW_VALUE", 78, 90, "three people")],
        [("NEW_VALUE", 10, 25, "Jojo restaurant"), ("REFERENCE", 26, 38, "the same day"),
         ("NEW_VALUE", 42, 53, "afternoon 1"), ("NEW_VALUE", 78, 90, "three people")]),
}


def spans_of(row: dict) -> list[tuple]:
    return [(s["label"], s["start"], s["end"], s["text"]) for s in row["value_spans"]]


def apply_changes(rows: list[dict], changes: dict = CHANGES) -> list[dict]:
    by_id = {r["id"]: r for r in rows}
    missing = [i for i in changes if i not in by_id]
    if missing:
        raise SystemExit(f"decided ids not in gold v1: {missing}")
    out = copy.deepcopy(rows)
    for row in out:
        if row["id"] not in changes:
            continue
        before, after = changes[row["id"]]
        if spans_of(row) != before:
            raise SystemExit(f"{row['id']}: gold v1 VALUE spans differ from the decided 'before' state: {spans_of(row)}")
        utt = row["current_user_utterance"]
        for lab, s, e, text in after:
            if utt[s:e] != text:
                raise SystemExit(f"{row['id']}: new span {text!r} does not match utterance[{s}:{e}]")
        template = row["value_spans"][0]
        row["value_spans"] = [{**template, "label": lab, "start": s, "end": e, "text": text}
                              for lab, s, e, text in after]
        ann = row["annotation"]
        ann["adjudication_log_id"] = LOG_ID
        ann["decision_reason"] = f"{ann.get('decision_reason', '')}; {NOTE}"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite {args.out}")

    rows = read_jsonl(args.gold)
    new_rows = apply_changes(rows)
    changed = [a["id"] for a, b in zip(rows, new_rows) if a != b]
    if sorted(changed) != sorted(CHANGES):
        raise SystemExit(f"unexpected set of changed rows: {changed}")
    verdict = validate_rows(new_rows, require_gold=True, allowed_splits=("train",))
    if verdict["status"] != "PASS":
        raise SystemExit("gold v1.1 invalid: " + str(verdict["errors"][:5]))
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new_rows), encoding="utf-8")
    print(json.dumps({
        "status": "GOLD_V1_1_BUILT", "rows": len(new_rows), "changed_ids": sorted(changed),
        "gold_v1_sha256": hashlib.sha256(args.gold.read_bytes()).hexdigest(),
        "gold_v1_1_sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
        "out": str(args.out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
