# Taxonomy Narrowing — PROPOSAL (2026-10-30, awaiting both signatures)

**Status: PROPOSED, NOT ADOPTED.** Becomes binding only when both reviewers sign
below, and only if signed **before** the locked holdout is opened. It changes the
scope of per-class claims; it does not change any label, the training tagset, the
frozen model configuration or the locked test selection.

## 1. Evidence used (train-side only)

Test-side supports were **not consulted** for this proposal (deciding claim scope
from holdout content would be a lock violation). Inputs:

| Label | gold v1 total | train | dev | Corpus evidence |
|---|---|---|---|---|
| NEW_VALUE | 368 | 333 | 35 | — |
| REFERENCE | 106 | 99 | 7 | — |
| UPDATE_CUE | 74 | 71 | 3 | — |
| CANCEL_CUE | 6 | 6 | 0 | D0: CANCEL bucket dominated by refusals (DP-1) |
| KEPT_VALUE | 4 (2 under review, B3/B4) | 3 | 1 | — |
| KEEP_CUE | 1 | 0 | 1 | train support 0 → unlearnable |
| OLD_VALUE | 0 | 0 | 0 | D0/D1: no observed support |
| RESTORE_CUE | 0 | 0 | 0 | D0: RESTORE bucket = topic returns (DP-2) |

Sources: `D5_GOLD_V1_BUILD.md`, `D5_SPLIT_FREEZE.md`, `D0_D1_FACTUAL_FINDINGS.md`.

## 2. Options (tick one)

**☐ A — Narrow the claims (coordinator's recommendation).**
- *Primary per-class claims:* NEW_VALUE, REFERENCE, UPDATE_CUE.
- *Marginal, reported with denominators and flagged unstable:* CANCEL_CUE, KEPT_VALUE.
- *Out of scope for this study, reported as NOT EVALUABLE with the corpus reason:* OLD_VALUE, KEEP_CUE, RESTORE_CUE.
- Locked headline metrics stay exactly as registered: per-layer strict micro P/R/F1
  (VALUE, CUE) with denominators. No new headline metric is introduced.
- Training tagset unchanged (all 8 labels kept in the BIO tag sets), so the
  frozen D5 configuration is unaffected.
- Write-up: the research question is stated for the supported labels; the
  absent classes are named as a corpus limitation of SGD, not as model failures.

**☐ B — Keep the full taxonomy in the claims.** Status quo: all 8 labels stay in
scope; empty classes are reported as NOT EVALUABLE in every table.

**☐ C — A + separate exploratory challenge set.** Same as A, plus a NEW,
separately locked pool (e.g. Microsoft Frames via `extract_frames_candidates.py`,
obtained manually under its terms) to try to collect OLD_VALUE / KEEP_CUE /
RESTORE_CUE examples. Requires new mining, a new lock, two-reviewer annotation;
reported only as exploratory, never merged into the registered holdout. Large
extra effort; does not change the main test.

## 3. Consequence for the registered protocol

Any option is recorded as a scope clarification in `PROTOCOL_DEVIATIONS.md`
(not a membership or metric change) at signing time.

**Decision:** ☐ A ☐ B ☐ C — **Signed:** reviewer_A_BURAK ________ · reviewer_B_ENES ________ · **Date:** ________
