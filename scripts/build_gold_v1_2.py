#!/usr/bin/env python3
"""Build gold v1.2 = gold v1.1 (unchanged) + the 400 D3-EXT records (reports/D3_EXT_DECISIONS.md).

Fail-closed: the set of shared records whose revised spans differ must equal the decided set exactly; every
decided span is asserted against the utterance; the solo flag fix asserts its 'before' state; the combined file
must pass the gold validator. Gold v1.1 is never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl, validate_rows  # noqa: E402

REVIEWERS = ["reviewer_A_BURAK", "reviewer_B_ENES"]
LOG_ID = "D3-EXT-2026-10-30"
DECISIONS = {  # shared record -> "A" | "B" | list of (label, start, end, text)
    "SGD-2a7fc8f2eac3b42e62": "B", "SGD-361896f9c4d73eae25": "A", "SGD-3713e4d4c2714a5926": "A",
    "SGD-42dccee119bb562199": "B", "SGD-46fec88e213aa350fa": "A", "SGD-47d6edc31e7c4243e4": "A",
    "SGD-576dfdb778da768f4f": "A", "SGD-5afe7751820cc4ba43": "B", "SGD-5cea83d03ce71a69a5": "A",
    "SGD-68ea758990beb3df96": "B", "SGD-7df9cb539887f2433b": "A",
    "SGD-8d53605ac03a2eed81": [("UPDATE_CUE", 0, 8, "Actually"), ("UPDATE_CUE", 38, 44, "Change"),
                               ("NEW_VALUE", 57, 64, "1:45 pm")],
    "SGD-9683f27705af5ad48b": "B", "SGD-b4595e7fb1a64c741f": "A", "SGD-bda5bb84c2e701c6b4": "B",
    "SGD-c219a5d64ad768094c": "A", "SGD-e34ca1ce46b62c7aa1": "A", "SGD-e499e52b23d1effc75": "A",
    "SGD-e4d6af27a3a851dc52": "B",
}
# solo record -> (owner "A"|"B", cue span (label, start, end, text) to remove)
SOLO_REMOVALS = {"SGD-96f8721d8120084e0d": ("B", ("RESTORE_CUE", 47, 54, "back to"))}
CUE_LABELS = {"UPDATE_CUE", "CANCEL_CUE", "KEEP_CUE", "RESTORE_CUE"}


def clean(spans) -> list[dict]:
    return sorted(({"start": s["start"], "end": s["end"], "label": s["label"], "text": s["text"]} for s in spans),
                  key=lambda s: (s["start"], s["end"], s["label"]))


def keyset(row: dict) -> tuple:
    return tuple(tuple((s["start"], s["end"], s["label"]) for s in clean(row[l])) for l in ("value_spans", "cue_spans"))


def gold_row(base: dict, value, cue, issue: str, reason: str, notes) -> dict:
    return {"id": base["id"], "source": base["source"], "dialogue_family_id": base["dialogue_family_id"],
            "history": base["history"], "current_user_utterance": base["current_user_utterance"],
            "value_spans": clean(value), "cue_spans": clean(cue), "transitions": [], "links": [],
            "difficulty": base.get("difficulty"),
            "annotation": {"status": "ADJUDICATED", "guideline_version": "v0.2.3", "reviewers": list(REVIEWERS),
                           "adjudicator": "reviewer_A_BURAK+reviewer_B_ENES_joint", "adjudication_log_id": LOG_ID,
                           "issue_type": issue, "decision_reason": reason, "uncertainty_notes": notes}}


def build_ext_rows(a_rows, b_rows, shared, decisions=DECISIONS, solo_removals=SOLO_REMOVALS) -> list[dict]:
    A, B = {r["id"]: r for r in a_rows}, {r["id"]: r for r in b_rows}
    shared = set(shared)
    differing = {i for i in shared if keyset(A[i]) != keyset(B[i])}
    if differing != set(decisions):
        raise SystemExit(f"decided set != differing shared set: missing {sorted(differing - set(decisions))[:5]}, "
                         f"extra {sorted(set(decisions) - differing)[:5]}")
    out = []
    for rid in sorted(shared):
        a, b = A[rid], B[rid]
        notes = "; ".join(n for n in (a["annotation"].get("uncertainty_notes"), b["annotation"].get("uncertainty_notes")) if n) or None
        if rid not in decisions:
            out.append(gold_row(a, a["value_spans"], a["cue_spans"], "ext_double_blind_agreed",
                                "D3-EXT shared record: identical revised spans from both reviewers", notes))
            continue
        d = decisions[rid]
        if d in ("A", "B"):
            src = a if d == "A" else b
            value, cue = src["value_spans"], src["cue_spans"]
            reason = f"D3-EXT shared record: joint decision {d} ({'Burak' if d == 'A' else 'Enes'}'s revised spans)"
        else:
            utt = a["current_user_utterance"]
            for lab, s, e, text in d:
                if utt[s:e] != text:
                    raise SystemExit(f"{rid}: decided span {text!r} does not match utterance[{s}:{e}]")
            value = [{"start": s, "end": e, "label": lab, "text": t} for lab, s, e, t in d if lab not in CUE_LABELS]
            cue = [{"start": s, "end": e, "label": lab, "text": t} for lab, s, e, t in d if lab in CUE_LABELS]
            reason = "D3-EXT shared record: joint decision D (spans written in the decision record)"
        out.append(gold_row(a, value, cue, "ext_double_blind_joint_decision", reason, notes))
    owners = {i: "A" for i in A if i not in shared} | {i: "B" for i in B if i not in shared}
    for rid in sorted(owners):
        who = owners[rid]
        src = (A if who == "A" else B)[rid]
        name = "Burak" if who == "A" else "Enes"
        value, cue = list(src["value_spans"]), list(src["cue_spans"])
        issue = "ext_single_annotation_rule_scan"
        reason = f"D3-EXT single annotation by {name}; mechanical v0.2.3 rule scan, no flag; second reviewer did not re-check"
        if rid in solo_removals:
            owner, (lab, s, e, text) = solo_removals[rid]
            hit = [x for x in cue if (x["label"], x["start"], x["end"], x["text"]) == (lab, s, e, text)]
            if owner != who or len(hit) != 1:
                raise SystemExit(f"{rid}: solo fix precondition failed")
            cue.remove(hit[0])
            issue = "ext_single_annotation_rule_flag_joint_decision"
            reason = (f"D3-EXT single annotation by {name}; rule-scan flag decided jointly "
                      f"(removed {lab} {text!r}); second reviewer did not otherwise re-check")
        out.append(gold_row(src, value, cue, issue, reason, src["annotation"].get("uncertainty_notes")))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True, help="gold v1.1")
    ap.add_argument("--a", type=Path, required=True, help="Burak's REVISED canonical file")
    ap.add_argument("--b", type=Path, required=True, help="Enes's REVISED canonical file")
    ap.add_argument("--index", type=Path, required=True, help="PRIVATE_ext_index.json (shared ids)")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite {args.out}")
    base = read_jsonl(args.gold)
    shared = json.loads(args.index.read_text(encoding="utf-8"))["assignment"]["shared"]
    ext = build_ext_rows(read_jsonl(args.a), read_jsonl(args.b), shared)
    if len(ext) != 400 or {r["id"] for r in ext} & {r["id"] for r in base}:
        raise SystemExit("unexpected EXT size or id overlap with gold v1.1")
    rows = base + ext
    verdict = validate_rows(rows, require_gold=True, allowed_splits=("train",))
    if verdict["status"] != "PASS":
        raise SystemExit("gold v1.2 invalid: " + str(verdict["errors"][:5]))
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    labels = Counter(s["label"] for r in rows for l in ("value_spans", "cue_spans") for s in r[l])
    print(json.dumps({"status": "GOLD_V1_2_BUILT", "rows": len(rows), "from_v1_1": len(base), "ext": len(ext),
                      "ext_segments": dict(Counter(r["annotation"]["issue_type"] for r in ext)),
                      "label_support": dict(sorted(labels.items())),
                      "gold_v1_1_sha256": hashlib.sha256(args.gold.read_bytes()).hexdigest(),
                      "gold_v1_2_sha256": hashlib.sha256(args.out.read_bytes()).hexdigest()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
