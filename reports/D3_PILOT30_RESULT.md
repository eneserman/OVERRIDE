# D3 Pilot-30 Result Report — FILLED 2026-10-29 (real human annotations)

**Status:** COMPLETE — **two independent human annotators** (reviewer_A_BURAK, reviewer_B_ENES), blind, no discussion during the pilot. Calibration (10, discussed) excluded from these statistics by design. **This is human agreement, not gold** — gold requires adjudication.

## 0. Inputs

| Item | Value |
|---|---|
| reviewer A | `reviewer_A_BURAK_filled.jsonl` (30/30, `ANNOTATED`) |
| reviewer B | `reviewer_B_ENES_filled.jsonl` (30/30, `ANNOTATED`) |
| Format validation | **0 errors** (offsets valid, `text == utterance[start:end]`, labels in vocabulary) |
| Guideline | v0.2.1 FROZEN (DP-1…DP-5) |
| Calibration done first? | Yes (10 items, discussed together; excluded from these scores) |

## 1. Agreement summary (`reports/D3_PILOT30_AGREEMENT.json`)

- **Example-level exact layer-set agreement: 0.8333** (50/60 layer judgments identical)
- **Per-label exact-span agreement:**

| Layer | Label | matched | only-A | only-B | symmetric F1 | support (A+B spans) |
|---|---|---|---|---|---|---|
| value_spans | NEW_VALUE | 24 | 8 | 4 | **0.800** | 36 |
| value_spans | REFERENCE | 6 | 4 | 2 | **0.667** | 12 |
| value_spans | OLD_VALUE | 0 | 0 | 0 | NOT EVALUABLE | **0** |
| value_spans | KEPT_VALUE | 0 | 0 | 0 | NOT EVALUABLE | **0** |
| cue_spans | UPDATE_CUE | 3 | 0 | 0 | **1.000** | 3 |
| cue_spans | KEEP_CUE | 0 | 0 | 0 | NOT EVALUABLE | **0** |
| cue_spans | CANCEL_CUE | 0 | 0 | 0 | NOT EVALUABLE | **0** |
| cue_spans | RESTORE_CUE | 0 | 0 | 0 | NOT EVALUABLE | **0** |

- `difficulty_agreement` = **0.9333**
- `uncertainty_flagged`: A = 0, B = 1 (`SGD-1bff672afd614f47`)

## 3. Class supports observed (human labels)

Both reviewers produced identical class **presence**: NEW_VALUE, REFERENCE, UPDATE_CUE only. `OLD_VALUE`, `KEPT_VALUE`, `KEEP_CUE`, `CANCEL_CUE`, `RESTORE_CUE` have **zero support in the pilot-30** — consistent with the D0/D1 corpus findings (cancel = refusals, restore = topic returns). These classes are **NOT EVALUABLE** from this pilot and must not be claimed as validated.

## 4. Problem analysis — all 10 disagreements in 3 convention zones

### Zone 1 — Determiner/NP boundary (5 cases: #3 #4 #5 #6 #10)
`"a salon"` vs `"salon"`; `"small rental car"` vs `"small"`; `"a games event"` vs `"games event"`; `"on that date"` vs `"that date"`; `"there"` vs `"near there"`. Both reviewers are internally consistent; the guideline's "complete mentioned value" rule lacks a determiner convention.

### Zone 2 — Is a vague/non-specific mention a value? (4 cases: #2 #7 #8 #10)
`"exciting and interesting"`, `"1 stop"` (inside a question), `"some other places"`, `"a restaurant"` — concrete-value vs vague-preference/query-target judgment.

### Zone 3 — REFERENCE in questions/deixis (3 cases: #1 #9 #10)
`"the genre"` (question about a property), `"that"` (prior offer), `"there"` (locative deixis).

**DP-rule performance (the hard ones):** DP-1 (refusal ≠ CANCEL) — **both perfect** (no CANCEL_CUE on any "Not now" item). DP-4 (explicit cue only) — **both perfect** (UPDATE_CUE F1 = 1.0). DP-2/DP-3 (topic return vs restore/reference) — no RESTORE misuse; the REFERENCE disputes are the Zone-3 convention issue, not rule violations.

## 5. Decision — **REVISE (minor) → GO**

**Why not plain GO:** the boundary and value-ness conventions would generate the same 3-zone friction across the full 457 run and contaminate adjudication with avoidable noise.

**Why not STOP:** core rule logic (cue decisions, DP-1/DP-2/DP-5) shows strong agreement; the disputes are conventions, not construct problems.

**Action plan (v0.2.2, ~1 hour total):**
1. Add 3 conventions to the guideline (change-log, affected IDs listed below):
   - **C1 boundary:** include the determiner when part of the noun phrase (`"a salon"`, `"a games event"`); modifiers belong to the value when they restrict it (`"small rental car"`).
   - **C2 value-ness:** label only **concrete/determinable** values; vague preferences (`"some other places"`, `"exciting and interesting"`) and query targets in questions (`"1 stop"` in *"Does it have 1 stop?"*) get **no** value span.
   - **C3 deixis:** bare pronouns/locatives (`"it"`, `"there"`, `"the genre"` as a question target) are **not** `REFERENCE`; `REFERENCE` needs a specific previously mentioned value/option.
2. Both reviewers re-check **only the 10 disagreement items** under v0.2.2 (~5 min each).
3. Adjudicate the remaining differences with reasons → proceed to the full 457 + sealed 363.

**Affected example IDs (re-check list):** `SGD-1bff672afd614f473b`, `SGD-3268166bbb220be1`, `SGD-500c5b88b32a4295`, `SGD-50c2d5c01ea6273b`, `SGD-71a78f8aba480436`, `sgd_43f2a82f62150cff`, `sgd_667a77ce3c34f0be`, `sgd_a5d726d0e27a59f5`, `sgd_a7f975950eb100c6`, `sgd_cb84c0478ba31271`

**Signed (owner):** `TBD` | **Date:** 2026-10-29

## 6. Integrity statement

Completed only from real human annotations (Enes + Burak, independent, blind). The 10 calibration items were discussed together and are excluded. No AI labels were used in this measurement. No gold was produced (adjudication pending). The sealed test set (363) was not opened. Workload note: 30 items ≈ 90 min/reviewer measured informally — full 457 feasible in sessions.

---
*Template: `D3_PILOT30_REPORT_TEMPLATE.md` (retained for the next rounds).*
