# D3 Annotation Handoff — exact files for reviewers + remaining technical blockers (2026-10-28)

**Status per CTO verdict:** D3 technical preparation = GO; annotation execution = ready to start; **gold = 0**, **test metrics = none**, **D5 = not started**. Everything below is verified by executed commands (75/75 tests, `HANDOFF_PRECHECK_PASS`, `RAW_POOL_LOCK_VALID`); the commit `ee01827`+ is on GitHub for independent inspection.

## 1. Exact files to hand to the two annotators (in this order)

| Step | Give the reviewer | Where | Est. time |
|---|---|---|---|
| 0. Read | `reports/D3_REVIEWER_ONBOARDING_TR.md` + `13_ANNOTATION_GUIDELINES.md` (R1–R12, DP-1/DP-2) | repo | 30 min |
| 1. **Calibration** | `data/annotations/d3_calibration_v0.1/calibration_sample.jsonl` (each their own copy) + `reports/D3_CALIBRATION_PROTOCOL.md` (key opens AFTER their attempt) | local | ~1 h + discussion |
| 2. **Pilot-30 trial** | `data/annotations/d3_pilot30_v0.1/reviewer_A_BLIND.jsonl` → reviewer A, `reviewer_B_BLIND.jsonl` → reviewer B | local | ~1.5 h each |
| 3. (after analysis) Full pass | `data/annotations/d3_merged_traindev_v0.1/reviewer_A/B_BLIND.jsonl` (457 records; the 30+10 already judged are re-checked only if the guideline changed) | local | ~10–14 h each |
| 4. (last, sealed) Test pass | `data/annotations/d3_test_packets_v0.1/reviewer_A/B_BLIND.jsonl` (363 records) | local | ~8–10 h each |
| Tool | `scripts/annotation_entry_helper.py` (their own `--reviewer-id`) | repo | — |

**Never give reviewers:** `PRIVATE_mining_manifest.jsonl`, `PRIVATE_sampling_manifest.jsonl`, `pilot30_index.json`, `calibration_index.json` (coordinator-only), `data/ai_suggestions/*` (AI drafts), or each other's files.

Output from each reviewer: `reviewer_X_filled.jsonl` (per packet), created independently.

## 2. Pilot-30 trial (the immediate next action)

30 train-partition items (SHA `3a6d7e77…`), disjoint from the 10 calibration items, stratified across buckets. After both reviewers finish: run `normalize` + `annotation_agreement.py --exclude-ids calibration_index.json` (PRIMARY score excludes the discussed calibration items) → review per-class exact-span agreement, DP-1/DP-2 consistency, `UNCERTAIN:` patterns and real minutes/example → then the GO/narrow decision for the full 820-record run (1,640 judgments). Full procedure: `reports/D3_PILOT30_TRIAL_PROTOCOL.md`.

## 3. Technical controls already in place

- **Calibration ≠ independent agreement:** `annotation_agreement.py --exclude-ids` reports `agreement_excluding_practice_items` as PRIMARY and discloses the included variant (tested).
- **Test gold sealing:** access log created (`reports/TEST_ACCESS_LOG.md`, zero accesses so far); test gold build requires `--allowed-splits dev,test`; single final evaluation via `evaluate_frozen_test.py`; unrecorded access = protocol violation.
- **Gold only from human decisions:** `build_adjudicated_gold.py` refuses fabricated/invalid spans, identical reviewers, missing decisions, overwrites (5 tests).
- **Guideline changes are versioned** with affected example IDs (`13_ANNOTATION_GUIDELINES.md` change log); **locked test selection never changes**.

## 4. Remaining technical blockers (honest list)

| # | Blocker | Severity | Status |
|---|---|---|---|
| 1 | **Two real human annotators not yet engaged** — the only path to gold; nothing else is missing technically | CRITICAL | owner action |
| 2 | Adjudicator availability for disagreement resolution (can be the owner + both reviewers together) | HIGH | owner action |
| 3 | Rare true-class support (CANCEL/RESTORE) likely tiny → diagnostic-only; dev partition (45 families) may lack classes → `NOT EVALUABLE` honesty rule applies | MEDIUM | documented, monitored |
| 4 | Deep-semantic paraphrase leakage not measurable with stdlib tooling | LOW | human spot-check during annotation |
| 5 | P2 sheet re-check before submission (10 rows were empty) | MEDIUM | recurring owner action |
| 6 | Frames enrichment for L4/L5 (portal license) — optional, separate pool, never touches the lock | LOW | optional, owner action |

## 5. Unchanged guarantees

No gold without human annotation; AI drafts never presented as human work; test labels sealed from development; no fabricated metrics; holdout lock and source hashes preserved; repo/history preserved; D5 final training awaits: pilot-30 review → full annotation → adjudication → validated gold → owner approval.
