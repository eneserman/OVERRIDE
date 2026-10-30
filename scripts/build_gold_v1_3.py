#!/usr/bin/env python3
"""Build gold v1.3 = gold v1.2 with the 320 D3-EXT solo records turned double-blind (amendment E3/E4).

For each of the 320 records: if round 2 matched the original annotator exactly, the gold v1.2 spans are
asserted unchanged; otherwise the final span set comes from the locked decisions file
(reports/D3_EXT2_DECISIONS.md, local JSON). Every other gold row must stay byte-identical; the result must pass
the gold validator.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl, validate_rows  # noqa: E402

LOG_ID = "D3-EXT2-2026-10-30"
ISSUE = {"identical": "ext_cross_double_blind_agreed",
         "separate_sheets_agreed": "ext_cross_double_blind_decision",
         "joint_decision": "ext_cross_double_blind_joint_decision",
         "no_agreement_gold_v1_2_kept": "ext_cross_double_blind_no_agreement_v1_2_kept"}


def spans(row: dict) -> tuple:
    return tuple(tuple(sorted((s["start"], s["end"], s["label"]) for s in row[l])) for l in ("value_spans", "cue_spans"))


def apply(gold_rows, solo_ids, round_a, round_b, decisions):
    A, B = {r["id"]: r for r in round_a}, {r["id"]: r for r in round_b}
    solo = set(solo_ids)
    if set(decisions) - solo:
        raise SystemExit("decision for a record outside the 320 solo set")
    out = copy.deepcopy(gold_rows)
    seen = set()
    for row in out:
        rid = row["id"]
        if rid not in solo:
            continue
        seen.add(rid)
        utt = row["current_user_utterance"]
        if rid in decisions:
            d = decisions[rid]
            for lay in ("value_spans", "cue_spans"):
                for s in d[lay]:
                    if utt[s["start"]:s["end"]] != s["text"]:
                        raise SystemExit(f"{rid}: decided span {s['text']!r} does not match the utterance")
            row["value_spans"] = [dict(s) for s in d["value_spans"]]
            row["cue_spans"] = [dict(s) for s in d["cue_spans"]]
            how = d["how"]
        else:
            if spans(A[rid]) != spans(B[rid]) or spans(A[rid]) != spans(row):
                raise SystemExit(f"{rid}: no decision, but round 2 does not equal the gold v1.2 version")
            how = "identical"
        ann = row["annotation"]
        ann["issue_type"] = ISSUE[how]
        ann["adjudication_log_id"] = LOG_ID
        ann["decision_reason"] = (f"D3-EXT record annotated blind by both reviewers (round 1 + cross round 2); "
                                  f"disposition: {how}")
    if seen != solo:
        raise SystemExit(f"{len(solo - seen)} solo records missing from gold v1.2")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True, help="gold v1.2")
    ap.add_argument("--index", type=Path, required=True, help="PRIVATE_ext_index.json")
    ap.add_argument("--round-a", type=Path, required=True, help="EK2_ALL320_A_BURAK_canonical.jsonl")
    ap.add_argument("--round-b", type=Path, required=True, help="EK2_ALL320_B_ENES_canonical.jsonl")
    ap.add_argument("--decisions", type=Path, required=True, help="D3_EXT2_FINAL_DECISIONS.json")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite {args.out}")
    base = read_jsonl(args.gold)
    idx = json.loads(args.index.read_text(encoding="utf-8"))["assignment"]
    solo = idx["A"] + idx["B"]
    new = apply(base, solo, read_jsonl(args.round_a), read_jsonl(args.round_b),
                json.loads(args.decisions.read_text(encoding="utf-8")))
    untouched = [a for a, b in zip(base, new) if a["id"] not in set(solo) and a != b]
    if untouched:
        raise SystemExit("rows outside the 320 changed")
    verdict = validate_rows(new, require_gold=True, allowed_splits=("train",))
    if verdict["status"] != "PASS":
        raise SystemExit("gold v1.3 invalid: " + str(verdict["errors"][:5]))
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new), encoding="utf-8")
    span_changes = sum(spans(a) != spans(b) for a, b in zip(base, new))
    labels = Counter(s["label"] for r in new for l in ("value_spans", "cue_spans") for s in r[l])
    print(json.dumps({"status": "GOLD_V1_3_BUILT", "rows": len(new), "records_with_span_changes": span_changes,
                      "ext_issue_types": dict(Counter(r["annotation"]["issue_type"] for r in new
                                                      if r["annotation"].get("issue_type", "").startswith("ext_"))),
                      "label_support": dict(sorted(labels.items())),
                      "gold_v1_2_sha256": hashlib.sha256(args.gold.read_bytes()).hexdigest(),
                      "gold_v1_3_sha256": hashlib.sha256(args.out.read_bytes()).hexdigest()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
