# Taxonomy Narrowing — ADOPTED 2026-10-30 (Option A)

**Status: ADOPTED — Option A, with KEPT_VALUE out of scope (see §4).** It was adopted before the locked holdout was
opened; Burak's concurrence was relayed by Enes and no handwritten signatures were collected (§4). It changes the
scope of per-class claims; it does not change any label, the training tagset, the
frozen model configuration or the locked test selection.

## 1. Evidence used (train-side only; counts updated to gold v1.1, 2026-10-30)

Test-side supports were **not consulted** for this proposal (deciding claim scope
from holdout content would be a lock violation). Inputs:

| Label | gold v1 total | train | dev | Corpus evidence |
|---|---|---|---|---|
| NEW_VALUE | 369 | 333 | 36 | — |
| REFERENCE | 108 | 100 | 8 | — |
| UPDATE_CUE | 74 | 71 | 3 | — |
| CANCEL_CUE | 6 | 6 | 0 | D0: CANCEL bucket dominated by refusals (DP-1) |
| KEPT_VALUE | 2 | 2 | 0 | gold v1 had 4; A3/A4 became REFERENCE in v1.1 |
| KEEP_CUE | 1 | 0 | 1 | train support 0 → unlearnable |
| OLD_VALUE | 0 | 0 | 0 | D0/D1: no observed support |
| RESTORE_CUE | 0 | 0 | 0 | D0: RESTORE bucket = topic returns (DP-2) |

Sources: `D5_GOLD_V1_BUILD.md`, `D5_SPLIT_FREEZE.md`, `D0_D1_FACTUAL_FINDINGS.md`.

## 2. Options (tick one)

**☑ A — Narrow the claims (ADOPTED).**
- *Primary per-class claims:* NEW_VALUE, REFERENCE, UPDATE_CUE.
- *Marginal, reported with denominators and flagged unstable:* CANCEL_CUE.
- *Out of scope for this study, reported as NOT EVALUABLE with the corpus reason:* OLD_VALUE, KEEP_CUE, RESTORE_CUE, KEPT_VALUE.
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

**Decision:** ☑ A ☐ B ☐ C

## 4. Adoption record (2026-10-30)

- **Decision:** Option A. KEPT_VALUE is also out of scope: after gold v1.1 it has 2 instances in total (train 2, dev 0),
  so it cannot be evaluated on dev and is reported as NOT EVALUABLE like the other empty classes.
- **Primary per-class claims:** NEW_VALUE, REFERENCE, UPDATE_CUE. **Marginal (denominators, flagged unstable):** CANCEL_CUE (n=6, train only).
  **Out of scope / NOT EVALUABLE:** OLD_VALUE, KEPT_VALUE, KEEP_CUE, RESTORE_CUE.
- **Made before the holdout was opened:** `TEST_ACCESS_LOG.md` has no executed access; the test-side supports were not consulted.
- **Who:** decided by Enes (owner) in the coordination chat; Burak's concurrence was relayed by Enes and was not independently
  confirmed in this session. Handwritten signatures were not collected.
- **Unchanged:** all labels, the 8-label training tagset, the frozen model configuration, the metrics registered in
  `EVALUATION_PROTOCOL_LOCK.md` (strict per-layer micro P/R/F1 with denominators) and the locked test selection.
