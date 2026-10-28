# D3 Technical QA Report — 2026-10-28

**Scope:** technical readiness for human annotation (packets, tooling, protocol). **Gold: 0. Real test metrics: none. D5: not started.** All numbers below were produced by executed commands.

## 1. Packet inventory (all local, gitignored — handed to annotators directly)

| Packet | Records | Blind SHA-256 | Notes |
|---|---|---|---|
| `d3_merged_traindev_v0.1/reviewer_A/B_BLIND.jsonl` | **457** | `9e0e6cae…`-derived set (see dir QA) | 361 mining + 100 pilot − 4 turn-level duplicates; A ≡ B byte-identical |
| `d3_test_packets_v0.1/reviewer_A/B_BLIND.jsonl` | **363** | `525a1069336d3d40c9120a0dcf245c1ebdacfcdbad5f34215e773a7479db0b42` | from the locked pool; sealed |
| `d3_calibration_v0.1/calibration_sample.jsonl` | **10** | (index in `calibration_index.json`) | practice items, excluded/included-transparent in agreement stats |

**7 overlapping dialogue families managed:** `101_00093, 107_00055, 74_00030, 79_00098, 85_00063, 98_00086, 99_00039` — 4 contained identical turns in both pools (pilot copies dropped, mining kept, logged) and 3 contribute two different turns (both kept, grouped into the same partition). No example was silently lost: the 4 dropped IDs are listed in the merge log.

## 2. Split integrity (frozen before annotation)

| Item | Value |
|---|---|
| Pre-committed plan | `reports/D3_TRAIN_DEV_SPLIT_PLAN.json` — 454 families → **409 `train_gold` / 45 `dev_gold`** (sha256 hex-bucketing, seed 20261028, same scheme as `freeze_gold_splits.py`) |
| Partition index | `d3_merged_traindev_v0.1/partition_index.json` — every example mapped to its partition (rows: 411 train / 46 dev) |
| Locked test pool | manifest SHA-256 `b42299f8…0581` — **unmodified**; `--verify` re-run during this work = `RAW_POOL_LOCK_VALID` |
| Namespaced identity | 363/363 unique `(split, dialogue_id)` in test packets; 5 raw-ID collisions are different dev/test dialogues (documented artifact) |

## 3. Leakage checks (executed)

- Test packets: no labels, no hints, no AI/model/mining keys ✓; ids unique ✓; one example per namespaced dialogue ✓.
- Merged pool vs locked holdout: 0 exact-text overlap, 0 near-dup (Jaccard ≥0.9) after the documented exclusions ✓.
- Train/dev/test content fingerprints: 0 identical dialogues, 0 identical user-turn sequences across official splits ✓ (`reports/D3_LEAKAGE_AUDIT_V08.json`).

## 4. Tooling prepared (tests prove the invariants)

| Tool | Change | Proven by |
|---|---|---|
| `scripts/validate_annotations.py` | `allowed_splits` (default `train` unchanged; `dev,test` for sealed test gold) | `test_d3_adjudication_tools.py` |
| `scripts/annotation_agreement.py` | + `span_level_agreement_by_label` (exact-span matched/only-A/only-B/F1), `difficulty_agreement`, `uncertainty_flagged` | same |
| `scripts/build_adjudicated_gold.py` (new) | merges 2 human reviews + **human decisions only**; rejects bad spans/same reviewers/missing decisions/overwrite | 5 tests incl. "gold only from human decisions" |
| `scripts/annotation_entry_helper.py` (existing) | data entry for reviewers; generates no labels | 12 earlier tests |

## 5. Tests and preflight

| Command | Result |
|---|---|
| `python -m unittest discover -s tests -p "test_*.py"` | **75/75 OK** |
| `python scripts/preflight_handoff.py` | `HANDOFF_PRECHECK_PASS` |
| `lock_prospective_holdout.py --verify` (re-run) | `RAW_POOL_LOCK_VALID` |
| Source | SGD pinned `e852981ae34990f4358979625854259302feaa78` (`REAL_SOURCE_VERIFIED`) |

## 6. Residual risks / known limitations

1. **Dev partition (45 families) may lack rare classes** — handled by the honesty rule in `D3_GOLD_CREATION_PROTOCOL.md` (support 0 → NOT EVALUABLE; never re-balance post-hoc).
2. **CANCEL/RESTORE true-class yield is expected to be low** (refusals/topic-returns dominate the pools) → diagnostic-only framing continues.
3. **Calibration items stay in the main pool** — agreement statistics must be reported with and without them.
4. **Deep-semantic paraphrase leakage** is not measurable with stdlib tooling; human spot-check remains the control.
5. **Annotator availability** is the only path to gold; D3 execution stays BLOCKED until two real reviewers complete the packets.

## 7. What was NOT done (by design)

No gold produced; test labels unopened/uncreated; no model trained; no metrics claimed; AI drafts not presented as human work; the locked holdout and all source hashes preserved; existing repo and history preserved (no rebuild).
