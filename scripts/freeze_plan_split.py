#!/usr/bin/env python3
"""Freeze the train/dev split from the PRE-COMMITTED plan (A6 rule).

Conflict rule (reports/D3_GOLD_CREATION_PROTOCOL.md A6): if the generic
freeze_gold_splits.py bucketing assigns differently than
reports/D3_TRAIN_DEV_SPLIT_PLAN.json (committed BEFORE annotation), the plan
wins; picking the more favorable split is a protocol violation. The conflict
itself is reported, never hidden.

Plan (verified byte-for-byte): seed 20261028, sha256('<seed>::<family>')[:15]
hex bucket, bucket < 0.10 -> dev_gold, else train_gold. 454 families.
This script only transcribes and binds the plan to the gold content hash.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl, validate_rows  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--compare", type=Path, help="freeze_gold_splits.py manifest to document conflict against")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = read_jsonl(args.gold)
    validation = validate_rows(rows, require_gold=True)
    if validation["status"] != "PASS":
        raise SystemExit("Refusing to split invalid gold: " + str(validation["errors"][:5]))

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    seed, assign = str(plan["seed"]), plan["assignment"]
    if plan.get("status") != "PRE_COMMITTED_SPLIT_PLAN_NOT_GOLD":
        raise SystemExit("plan status unexpected: " + str(plan.get("status")))

    groups: dict[str, list[str]] = collections.defaultdict(list)
    for row in rows:
        family = str(row.get("dialogue_family_id") or row["source"]["dialogue_id"])
        groups[family].append(row["id"])

    missing = set(groups) - set(assign)
    if missing:
        raise SystemExit(f"gold families absent from pre-committed plan: {sorted(missing)[:5]}")

    def bucket(family: str) -> float:
        h = hashlib.sha256(f"{seed}::{family}".encode()).hexdigest()
        return int(h[:15], 16) / float(16 ** 15)

    mismatches = []
    for family in sorted(groups):
        derived = "dev_gold" if bucket(family) < 0.10 else "train_gold"
        if assign[family] != derived:
            mismatches.append(family)
    if mismatches:
        raise SystemExit(f"plan rule no longer reproduces plan assignment: {mismatches[:5]}")

    canonical = json.dumps(sorted(rows, key=lambda r: r["id"]), ensure_ascii=False,
                           sort_keys=True, separators=(",", ":"))
    gold_sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    manifest = {
        "algorithm": "precommitted_plan_sha256_bucket_v1 (D3_TRAIN_DEV_SPLIT_PLAN.json)",
        "seed": int(seed),
        "gold_content_sha256": gold_sha,
        "plan_file": str(args.plan),
        "plan_status": plan["status"],
        "splits": {"train": [], "dev": []},
        "family_assignment": {},
    }
    for family in sorted(groups):
        part = "dev" if assign[family] == "dev_gold" else "train"
        manifest["family_assignment"][family] = part
        manifest["splits"][part].extend(sorted(groups[family]))
    for key in manifest["splits"]:
        manifest["splits"][key].sort()
    manifest["family_counts"] = dict(collections.Counter(manifest["family_assignment"].values()))
    manifest["example_counts"] = {k: len(v) for k, v in manifest["splits"].items()}

    by_id = {r["id"]: r for r in rows}
    manifest["gold_span_support_by_split"] = {}
    for split, ids in manifest["splits"].items():
        counts = {layer: collections.Counter() for layer in ("value_spans", "cue_spans")}
        for eid in ids:
            for layer in counts:
                counts[layer].update(s["label"] for s in by_id[eid][layer])
        manifest["gold_span_support_by_split"][split] = {
            layer: dict(sorted(c.items())) for layer, c in counts.items()}

    if args.compare and args.compare.exists():
        other = json.loads(args.compare.read_text(encoding="utf-8"))
        conflict = {f for f, p in other["family_assignment"].items()
                    if manifest["family_assignment"].get(f) != p}
        manifest["conflict_with_generic_freeze"] = {
            "file": str(args.compare),
            "generic_counts": other["example_counts"],
            "disagreeing_families": len(conflict),
            "resolution": "PRE_COMMITTED_PLAN_WINS (A6); conflict reported, not cherry-picked",
        }
        # the generic script's 'test' bucket is a TRAIN-SIDE bucket under the plan;
        # the real test is the separate locked holdout (never touched here)
        generic_test = other["splits"].get("test", [])
        manifest["conflict_with_generic_freeze"]["generic_test_bucket_ids_now_in_train_dev"] = len(generic_test)

    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite frozen manifest: {args.out}")
    manifest["manifest_digest"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "FROZEN_PLAN_SPLIT",
        "file": str(args.out),
        "manifest_digest": manifest["manifest_digest"],
        "gold_content_sha256": gold_sha,
        "counts": manifest["example_counts"],
        "families": manifest["family_counts"],
        "span_support": manifest["gold_span_support_by_split"],
        "conflict": manifest.get("conflict_with_generic_freeze"),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
