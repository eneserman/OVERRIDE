#!/usr/bin/env python3
"""D3-EXT: build 400 new blind train-side annotation packets (pre-registered in reports/D3_EXT_PROTOCOL.md).

Candidates come from official SGD train via mine_sgd_revision_candidates.scan_dialogues (same heuristic
buckets, never shown to reviewers). Fail-closed exclusions: every dialogue (family) already used anywhere
in data/annotations, data/sgd_pilot or gold; every utterance whose normalized text was already seen there
or in the locked holdout pool; at most one record per dialogue; no normalized-text duplicates.

Selection: fixed per-bucket quotas, seed-shuffled; a bucket that cannot meet its quota aborts the build.
Assignment: per bucket, ids ranked by sha256('<seed>::<id>'); the first SHARED[b] go to both reviewers,
the rest alternate A/B. New families get train/dev from the pre-committed plan rule
(sha256('20261028::<family>')[:15] / 16^15 < 0.10 -> dev_gold).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mine_sgd_revision_candidates import scan_dialogues  # noqa: E402

SEED = 20261031
PLAN_SEED = "20261028"
GUIDELINE = "v0.2.3"
# Amendment E1 (D3_EXT_PROTOCOL.md §7): MIXED has only 39 eligible dialogues, so 50 of its slots move to UPDATE.
QUOTAS = {"UPDATE": 170, "MIXED": 30, "HARD_NEGATIVE": 60, "REFERENCE": 50,
          "NO_CONTEXT": 30, "CANCEL": 20, "KEEP": 20, "RESTORE": 20}
SHARED = {"UPDATE": 34, "MIXED": 6, "HARD_NEGATIVE": 12, "REFERENCE": 10,
          "NO_CONTEXT": 6, "CANCEL": 4, "KEEP": 4, "RESTORE": 4}
PACKET_KEYS = {"example_id", "source", "history", "current_user_utterance", "annotation"}


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def rank(seed: int, rid: str) -> str:
    return hashlib.sha256(f"{seed}::{rid}".encode("utf-8")).hexdigest()


def plan_part(family: str) -> str:
    h = hashlib.sha256(f"{PLAN_SEED}::{family}".encode()).hexdigest()
    return "dev_gold" if int(h[:15], 16) / float(16 ** 15) < 0.10 else "train_gold"


def jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def seen_material(root: Path, outdir: Path) -> tuple[set, set, set]:
    """Train dialogue ids, normalized texts and raw-text SHA-256s that must not reappear."""
    families, texts, raw_shas = set(), set(), set()
    files = [p for d in ("data/annotations", "data/sgd_pilot", "data/gold") for p in (root / d).rglob("*.jsonl")
             if outdir.resolve() not in p.resolve().parents]
    for path in files:
        for row in jsonl(path):
            utt = row.get("current_user_utterance")
            if isinstance(utt, str):
                texts.add(norm(utt))
            src = row.get("source") or {}
            if src.get("split") == "train" and src.get("dialogue_id"):
                families.add(str(src["dialogue_id"]))
    lock = json.loads((root / "data/prospective_holdout/real_sgd_heldout_lock.json").read_text(encoding="utf-8"))
    raw_shas |= {c["current_text_sha256"] for c in lock["test_candidates"]}
    for row in jsonl(root / "data/prospective_holdout/private_pool/real_sgd_devtest_pool_locked.jsonl"):
        texts.add(norm(row["current_user_utterance"]))
    return families, texts, raw_shas


def select(rows, families, texts, raw_shas, quotas=QUOTAS, seed=SEED):
    rng = random.Random(seed)
    by_bucket: dict[str, list] = {}
    for bucket, hits, service, rec in rows:
        by_bucket.setdefault(bucket, []).append((bucket, hits, service, rec))
    chosen, used_dialogues, used_texts = [], set(), set()
    for bucket in sorted(quotas):
        options = sorted(by_bucket.get(bucket, []), key=lambda x: x[3]["example_id"])
        rng.shuffle(options)
        picked = 0
        for row in options:
            if picked >= quotas[bucket]:
                break
            rec = row[3]
            did, utt = str(rec["source"]["dialogue_id"]), rec["current_user_utterance"]
            n = norm(utt)
            if (not n or did in families or did in used_dialogues or n in texts or n in used_texts
                    or hashlib.sha256(utt.encode()).hexdigest() in raw_shas):
                continue
            chosen.append(row)
            used_dialogues.add(did)
            used_texts.add(n)
            picked += 1
        if picked < quotas[bucket]:
            raise SystemExit(f"bucket {bucket}: only {picked} eligible records for quota {quotas[bucket]}")
    return chosen


def assign(chosen, shared=SHARED, seed=SEED):
    plan = {"shared": [], "A": [], "B": []}
    for bucket in sorted(shared):
        ids = sorted((r[3]["example_id"] for r in chosen if r[0] == bucket), key=lambda i: rank(seed, i))
        plan["shared"] += ids[:shared[bucket]]
        for k, rid in enumerate(ids[shared[bucket]:]):
            plan["A" if k % 2 == 0 else "B"].append(rid)
    return plan


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"ABORT: refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sgd-root", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--plan-out", type=Path, required=True)
    args = ap.parse_args()

    families, texts, raw_shas = seen_material(args.repo_root, args.outdir)
    rows, observed, _ = scan_dialogues(args.sgd_root, "train")
    chosen = select(rows, families, texts, raw_shas)
    plan = assign(chosen)
    by_id = {r[3]["example_id"]: r for r in chosen}

    def packet(ids, who):
        recs = []
        for rid in sorted(ids, key=lambda i: rank(SEED, f"{who}:{i}")):
            rec = json.loads(json.dumps(by_id[rid][3]))
            rec["annotation"]["guideline_version"] = GUIDELINE
            assert set(rec) == PACKET_KEYS and rec["annotation"]["status"] == "UNLABELED"
            recs.append(rec)
        return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in recs)

    packets = {"reviewer_A_BURAK_EK_BLIND.jsonl": packet(plan["shared"] + plan["A"], "A"),
               "reviewer_B_ENES_EK_BLIND.jsonl": packet(plan["shared"] + plan["B"], "B")}
    for name, text in packets.items():
        write_new(args.outdir / name, text)

    fam_of = {rid: str(by_id[rid][3]["source"]["dialogue_id"]) for rid in by_id}
    split_plan = {
        "status": "PRE_COMMITTED_SPLIT_PLAN_NOT_GOLD",
        "purpose": "train/dev assignment for D3-EXT families, fixed BEFORE annotation",
        "method": "same rule as D3_TRAIN_DEV_SPLIT_PLAN.json: sha256('<seed>::<family>')[:15]/16^15 < 0.10 -> dev_gold",
        "seed": int(PLAN_SEED),
        "families": len(set(fam_of.values())),
        "assignment": {f: plan_part(f) for f in sorted(set(fam_of.values()))},
    }
    split_plan["partition_counts"] = {p: sum(1 for v in split_plan["assignment"].values() if v == p)
                                      for p in ("train_gold", "dev_gold")}
    write_new(args.plan_out, json.dumps(split_plan, indent=2, ensure_ascii=False) + "\n")

    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    index = {
        "status": "D3_EXT_PACKETS_NOT_GOLD", "protocol": "reports/D3_EXT_PROTOCOL.md", "seed": SEED,
        "quotas": QUOTAS, "shared_per_bucket": SHARED,
        "excluded_seen": {"train_families": len(families), "normalized_texts": len(texts), "holdout_raw_shas": len(raw_shas)},
        "observed_train_buckets": dict(observed),
        "assignment": plan,
        "records": {rid: {"bucket": r[0], "regex_hits": list(r[1]), "service": r[2], "family": fam_of[rid],
                          "split_plan": split_plan["assignment"][fam_of[rid]]} for rid, r in sorted(by_id.items())},
        "packets_sha256": {n: sha(args.outdir / n) for n in packets},
        "split_plan_file": str(args.plan_out), "split_plan_sha256": sha(args.plan_out),
        "note": "Coordinator-only. Buckets and assignment are never shown to reviewers.",
    }
    write_new(args.outdir / "PRIVATE_ext_index.json", json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "D3_EXT_PACKETS_BUILT", "records": len(by_id),
                      "shared": len(plan["shared"]), "A_solo": len(plan["A"]), "B_solo": len(plan["B"]),
                      "per_reviewer": {"A": len(plan["shared"]) + len(plan["A"]), "B": len(plan["shared"]) + len(plan["B"])},
                      "dev_families": split_plan["partition_counts"]["dev_gold"],
                      "packets_sha256": index["packets_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
