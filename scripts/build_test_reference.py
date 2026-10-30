#!/usr/bin/env python3
"""D6: build the prospective test reference + full gold + 3-way manifest.

Run ONLY inside the single logged test access (reports/TEST_ACCESS_LOG.md).
Registered rule (D3_ADJUDICATION_DECISIONS_FINAL.md §4, decided BEFORE any
model existed):
  - reviewers agree exactly (same span sets, both layers) -> that reference;
  - 3 decided IDs (F1/F2 rules; joint decision)          -> reviewer B's spans;
  - remaining disagreements (expected 60)                 -> per-layer intersection
    of identical spans only; every such record is flagged UNRESOLVED (DEV-001)
    and annotation.status=CONSENSUS_REFERENCE (never claimed adjudicated).

Fail-closed checks (any failure aborts before writing anything):
  - lock manifest re-verifies; both reviewer files cover exactly the 363
    locked IDs; every utterance matches the lock's current_text_sha256;
  - the 3 decided IDs truly disagree in the reviewer files AND appear in the
    signed decisions record;
  - computed disagreements == 63, unresolved == 60 (as registered in DEV-001);
  - no ID or dialogue-family overlap between train/dev gold and the test set;
  - combined gold passes the validator with the explicit consensus flag.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl, validate_rows  # noqa: E402

DECIDED_TAKE_B = ("SGD-473c2fae903c3d2740", "SGD-afba777aac592e7d5d", "SGD-01b297fc690c6a0e2b")
EXPECTED_DISAGREEMENTS = 63
EXPECTED_UNRESOLVED = 60
ADJ_LOG_ID = "D3-ADJ-2026-10-29-FINAL"


def canonical(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(obj) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def span_key(s: dict) -> tuple:
    return (s["start"], s["end"], s["label"], s.get("text"))


def layer_keys(row: dict, layer: str) -> list[tuple]:
    return sorted(span_key(s) for s in row[layer])


def key_to_span(k: tuple) -> dict:
    return {"start": k[0], "end": k[1], "label": k[2], "text": k[3]}


def family_key(official_split: str, dialogue_id: str) -> str:
    """SGD restarts dialogue numbering per official split, so a family is (split, dialogue_id) (DEV-002)."""
    return f"{official_split}::{dialogue_id}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", type=Path, required=True)
    ap.add_argument("--reviewer-a", type=Path, required=True)
    ap.add_argument("--reviewer-b", type=Path, required=True)
    ap.add_argument("--decisions", type=Path, required=True,
                    help="signed joint decisions record (D3_ADJUDICATION_DECISIONS_FINAL.md)")
    ap.add_argument("--train-dev-gold", type=Path, required=True)
    ap.add_argument("--plan-manifest", type=Path, required=True,
                    help="frozen train/dev plan manifest (frozen_plan_traindev_gold_v1.json)")
    ap.add_argument("--out-test", type=Path, required=True)
    ap.add_argument("--out-full-gold", type=Path, required=True)
    ap.add_argument("--out-manifest", type=Path, required=True)
    args = ap.parse_args()

    for p in (args.out_test, args.out_full_gold, args.out_manifest):
        if p.exists():
            raise SystemExit(f"ABORT: refusing to overwrite frozen artifact: {p}")

    # ---- 1. lock verification -------------------------------------------------
    lock = json.loads(args.lock.read_text(encoding="utf-8"))
    if lock.get("status") != "RAW_POOL_LOCKED_NOT_HUMAN_GOLD":
        raise SystemExit(f"unexpected lock status: {lock.get('status')}")
    lock_unhashed = {k: v for k, v in lock.items() if k != "manifest_sha256"}
    if sha(lock_unhashed) != lock["manifest_sha256"]:
        raise SystemExit("lock manifest_sha256 does not re-verify")
    candidates = {c["id"]: c for c in lock["test_candidates"]}
    if len(candidates) != 363:
        raise SystemExit(f"lock expects 363 candidates, got {len(candidates)}")

    # ---- 2. reviewer files ----------------------------------------------------
    rows_a = read_jsonl(args.reviewer_a)
    rows_b = read_jsonl(args.reviewer_b)
    a_by, b_by = {r["id"]: r for r in rows_a}, {r["id"]: r for r in rows_b}
    if len(a_by) != 363 or len(b_by) != 363:
        raise SystemExit(f"reviewer files must have 363 unique ids: A={len(a_by)} B={len(b_by)}")
    if set(a_by) != set(candidates) or set(b_by) != set(candidates):
        raise SystemExit("reviewer id sets differ from locked test_candidates")
    problems = []
    for rid, cand in candidates.items():
        for name, by in (("A", a_by), ("B", b_by)):
            row = by[rid]
            ann = row.get("annotation") or {}
            if ann.get("status") != "ANNOTATED":
                problems.append(f"{name}/{rid}: annotation.status={ann.get('status')}")
            if row.get("current_user_utterance") != a_by[rid].get("current_user_utterance"):
                problems.append(f"{name}/{rid}: utterance differs from reviewer A")
            utt_sha = hashlib.sha256(row["current_user_utterance"].encode()).hexdigest()
            if utt_sha != cand["current_text_sha256"]:
                problems.append(f"{name}/{rid}: utterance differs from LOCK current_text_sha256")
            if str(row.get("dialogue_family_id")) != str(cand["dialogue_family_id"]):
                problems.append(f"{name}/{rid}: family differs from lock")
            if str((row.get("source") or {}).get("split")) != str(cand["official_source_split"]):
                problems.append(f"{name}/{rid}: source.split differs from lock official split")
    if problems:
        raise SystemExit("reviewer/lock cross-check failed:\n" + "\n".join(problems[:10]))

    # ---- 3. decisions record cross-check --------------------------------------
    decisions_text = args.decisions.read_text(encoding="utf-8")
    for rid in DECIDED_TAKE_B:
        if rid not in decisions_text:
            raise SystemExit(f"decided id {rid} not present in signed decisions record")

    # ---- 4. C1-r disposition (registered rule, applied mechanically) ----------
    agreed, decided, unresolved = [], [], []
    test_rows: list[dict] = []
    excluded_one_side = {"value_spans": {"a_only": 0, "b_only": 0},
                         "cue_spans": {"a_only": 0, "b_only": 0}}
    disagreements = 0
    for rid in sorted(candidates):
        ra, rb = a_by[rid], b_by[rid]
        same_layer = {}
        for layer in ("value_spans", "cue_spans"):
            ka, kb = layer_keys(ra, layer), layer_keys(rb, layer)
            same_layer[layer] = ka == kb
        if all(same_layer.values()):
            agreed.append(rid)
            spans = {"value_spans": [key_to_span(k) for k in layer_keys(ra, "value_spans")],
                     "cue_spans": [key_to_span(k) for k in layer_keys(ra, "cue_spans")]}
            rule = "both_reviewers_identical"
        else:
            disagreements += 1
            if rid in DECIDED_TAKE_B:
                decided.append(rid)
                spans = {"value_spans": [key_to_span(k) for k in layer_keys(rb, "value_spans")],
                         "cue_spans": [key_to_span(k) for k in layer_keys(rb, "cue_spans")]}
                rule = "decided_take_reviewer_B_F1F2"
            else:
                unresolved.append(rid)
                spans = {}
                for layer in ("value_spans", "cue_spans"):
                    ka, kb = layer_keys(ra, layer), layer_keys(rb, layer)
                    inter = sorted(set(ka) & set(kb))
                    excluded_one_side[layer]["a_only"] += len(set(ka) - set(kb))
                    excluded_one_side[layer]["b_only"] += len(set(kb) - set(ka))
                    spans[layer] = [key_to_span(k) for k in inter]
                rule = "unresolved_agreed_intersection_DEV-001"
        row_out = {
            "id": rid,
            "source": dict(ra["source"]),
            "dialogue_family_id": family_key(cand["official_source_split"], ra["dialogue_family_id"]),
            "history": ra.get("history", []),
            "current_user_utterance": ra["current_user_utterance"],
            "value_spans": spans["value_spans"],
            "cue_spans": spans["cue_spans"],
            "transitions": [],
            "links": ra.get("links", []),
            "difficulty": ra.get("difficulty"),
            "annotation": {
                "status": "CONSENSUS_REFERENCE",
                "guideline_version": (ra.get("annotation") or {}).get("guideline_version"),
                "reviewers": [(ra.get("annotation") or {}).get("reviewer_id"),
                              (rb.get("annotation") or {}).get("reviewer_id")],
                "adjudication_log_id": ADJ_LOG_ID,
                "reference_rule": rule,
                "full_layer_agreement": all(same_layer.values()),
                "unresolved_DEV001": rid in unresolved,
            },
        }
        test_rows.append(row_out)

    if disagreements != EXPECTED_DISAGREEMENTS:
        raise SystemExit(f"disagreements={disagreements}, registered {EXPECTED_DISAGREEMENTS}")
    if len(unresolved) != EXPECTED_UNRESOLVED:
        raise SystemExit(f"unresolved={len(unresolved)}, registered {EXPECTED_UNRESOLVED}")
    if sorted(DECIDED_TAKE_B) != sorted(decided):
        raise SystemExit(f"decided set mismatch: computed {sorted(decided)}")
    # C1-r mechanical re-check: the 3 decided IDs must actually disagree
    for rid in decided:
        if all(layer_keys(a_by[rid], l) == layer_keys(b_by[rid], l)
               for l in ("value_spans", "cue_spans")):
            raise SystemExit(f"C1-r violated: {rid} does not disagree but is 'decided'")

    # ---- 5. validate test reference ------------------------------------------
    verdict = validate_rows(test_rows, require_gold=True, allowed_splits=("train", "dev", "test"),
                            accept_consensus=True)
    if verdict["status"] != "PASS":
        raise SystemExit("test reference invalid: " + str(verdict["errors"][:5]))

    # ---- 6. combined gold + 3-way manifest -----------------------------------
    td_rows = read_jsonl(args.train_dev_gold)
    plan = json.loads(args.plan_manifest.read_text(encoding="utf-8"))
    td_ids = {r["id"] for r in td_rows}
    test_ids = {r["id"] for r in test_rows}
    if td_ids & test_ids:
        raise SystemExit(f"ID overlap train/dev gold vs test: {sorted(td_ids & test_ids)[:5]}")
    td_fams = {family_key(r["source"]["split"], str(r.get("dialogue_family_id") or r["source"]["dialogue_id"]))
               for r in td_rows}
    test_fams = {str(r["dialogue_family_id"]) for r in test_rows}
    if td_fams & test_fams:
        raise SystemExit(f"FAMILY leakage train/dev vs test: {sorted(td_fams & test_fams)[:5]}")

    full_gold = sorted(td_rows + test_rows, key=lambda r: r["id"])
    full_verdict = validate_rows(full_gold, require_gold=True, allowed_splits=("train", "dev", "test"),
                                 accept_consensus=True)
    if full_verdict["status"] != "PASS":
        raise SystemExit("combined gold invalid: " + str(full_verdict["errors"][:5]))

    manifest = {
        "algorithm": "combined_precommitted_plan_traindev_plus_locked_holdout_v1",
        "seed": plan.get("seed"),
        "plan_file": str(args.plan_manifest),
        "plan_manifest_digest": plan.get("manifest_digest"),
        "lock_file": str(args.lock),
        "lock_manifest_sha256": lock["manifest_sha256"],
        "decisions_record": str(args.decisions),
        "adjudication_log_id": ADJ_LOG_ID,
        "test_reference_kind": "double_annotated_consensus_DEV-001",
        "splits": {"train": sorted(plan["splits"]["train"]),
                   "dev": sorted(plan["splits"]["dev"]),
                   "test": sorted(test_ids)},
        "family_assignment": dict(plan["family_assignment"]),
    }
    manifest["family_assignment"].update({str(f): "test" for f in sorted(test_fams)})
    manifest["family_counts"] = {"train": len({str(f) for f, s in manifest["family_assignment"].items() if s == "train"}),
                                 "dev": len({str(f) for f, s in manifest["family_assignment"].items() if s == "dev"}),
                                 "test": len(test_fams)}
    manifest["example_counts"] = {k: len(v) for k, v in manifest["splits"].items()}
    manifest["gold_content_sha256"] = hashlib.sha256(
        canonical(full_gold).encode("utf-8")).hexdigest()
    manifest["test_reference_stats"] = {
        "examples": len(test_rows),
        "full_layer_agreement": len(agreed),
        "decided_take_reviewer_B": sorted(decided),
        "unresolved_DEV001": len(unresolved),
        "unresolved_ids": sorted(unresolved),
        "excluded_one_side_spans": excluded_one_side,
        "status_counts": {"ADJUDICATED_equivalent_agreement": len(agreed) + len(decided),
                          "CONSENSUS_REFERENCE_unresolved": len(unresolved)},
        "note": ("All 363 test rows carry annotation.status=CONSENSUS_REFERENCE: the holdout was "
                 "double-annotated and disposed by the registered §4 rule, never jointly adjudicated "
                 "record-by-record. Rows with full agreement need no intersection loss."),
    }
    manifest["manifest_digest"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode()).hexdigest()

    # ---- 7. write ------------------------------------------------------------
    args.out_test.parent.mkdir(parents=True, exist_ok=True)
    args.out_test.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in test_rows),
                             encoding="utf-8")
    args.out_full_gold.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in full_gold),
                                  encoding="utf-8")
    args.out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                 encoding="utf-8")

    print(json.dumps({
        "status": "TEST_REFERENCE_BUILT",
        "test_rows": len(test_rows),
        "full_agreement": len(agreed),
        "decided_take_B": sorted(decided),
        "unresolved_DEV001": len(unresolved),
        "disagreements_total": disagreements,
        "excluded_one_side_spans": excluded_one_side,
        "full_gold_rows": len(full_gold),
        "gold_content_sha256": manifest["gold_content_sha256"],
        "manifest_digest": manifest["manifest_digest"],
        "outputs": [str(args.out_test), str(args.out_full_gold), str(args.out_manifest)],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
