# D3 Candidate Count Reconciliation — 2026-10-28 (CTO check 1)

**Status:** EVIDENCE RECORD (not gold). Machine-readable companion: `reports/D3_COUNT_RECONCILIATION.json` (every excluded record with source file, file SHA-256, dialogue ID, turn index, service, bucket and reason).

## The chain (each stage is a subtraction with named reasons)

```
164,982 train user turns scanned (mine_sgd_revision_candidates.py, split=train)
   └─ heuristic buckets → 400 mined (50/bucket × 8, seed 42, one per dialogue)
        ├─ −27  L1: exact normalized current-text match with a LOCKED holdout record
        ├─ −10  L2: near-duplicate of LOCKED holdout text (token Jaccard ≥ 0.9;
        │           punctuation/case/word-order variants of boilerplate)
        └─ − 2  in-train duplicate of a kept record's text
   = 361 FINAL D3 records (data/annotations/d3_packets_v0.1/)
```

| Bucket | Mined | −L1 (exact) | −L2 (near-dup) | −in-train dup | Final D3 |
|---|---|---|---|---|---|
| HARD_NEGATIVE | 50 | 2 | 1 | 0 | 47 |
| NO_CONTEXT | 50 | 0 | 2 | 0 | 48 |
| UPDATE | 50 | 0 | 0 | 0 | 50 |
| REFERENCE | 50 | 4 | 1 | 1 | 44 |
| CANCEL | 50 | 21 | 6 | 0 | 23 |
| KEEP | 50 | 0 | 0 | 1 | 49 |
| RESTORE | 50 | 0 | 0 | 0 | 50 |
| MIXED | 50 | 0 | 0 | 0 | 50 |
| **Total** | **400** | **27** | **10** | **2** | **361** |

## Why the earlier report said 375 and 373

- **375** was a **presentation error** in the first `D1_D2_EXECUTION_REPORT.md` table: pre-exclusion and post-exclusion numbers were mixed in one column (HARD_NEGATIVE shown as 50 while REFERENCE/CANCEL were already post-filter). The table is corrected in place with a dated correction note.
- **373** was the real intermediate count after the L1 pass only. The CTO-requested near-duplicate pass (L2) and the in-train dedup removed 12 more → **361 final**.
- No data was silently lost at any stage: the JSON lists **all 39 excluded records** with full source provenance (`source_file` + `source_file_sha256` + `dialogue_id` + `turn_index`) and the matching holdout IDs that caused each exclusion. The two in-train duplicates are `SGD-65090fea3728d3b4fc` (9_00015 t12, REFERENCE) and `SGD-15fd33526ffbaeac57` (104_00034 t8, KEEP).

## The holdout side (separate chain, locked)

377 pool rows mined (dev 179 + test 198) → −11 in-pool duplicate texts, −2 seen-family ID collisions, −1 seen text = **363 locked** (`data/prospective_holdout/pool_exclusion_log.json`). The holdout was **not modified** by any train-side cleaning; the lock and its manifest SHA-256 `b42299f8…0581` remain valid (`--verify` = `RAW_POOL_LOCK_VALID`).

## Final D3 packet state

| Item | Value |
|---|---|
| Records | **361** (blind, `UNLABELED`, one per dialogue, ≤12-turn history) |
| Blind file SHA-256 | `cd851ff577c93c40edc6d7d48807c5de44a86a98200754d01e6eec3fd7d1f1d3` (A ≡ B byte-identical) |
| QA checks | ids unique ✓ · one per dialogue ✓ · no holdout exact text ✓ · no holdout near-dup ≥0.9 ✓ · no hint/state keys ✓ |
