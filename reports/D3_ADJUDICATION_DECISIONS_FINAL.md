# D3 Adjudication — FINAL JOINT DECISIONS (2026-10-29)

**Status: JOINT / APPROVED.** Authored by the two reviewers independently (Burak 19:05 approved version, Enes approved version), converged in a joint resolution message (F1/F2/F3 + G1-G3). Coordinator only transcribed; **no label suggestion was made by AI** in this record.

**Scope:** train double-set T1–T6, pilot-30 P1–P10, general rules G1–G3, test-363 disposition rule.
**Frozen agreement scores are untouched by this record:** pilot `5e409339…`, test `36509d5f…`. Decisions change gold only.

## 1. General rules (G1–G3 + F1/F2 + threshold)

| # | Joint decision | Text |
|---|---|---|
| **G1** | all sets | Pilot, 457 and test are adjudicated under **v0.2.3** (single consistent gold). Original annotation guideline versions are preserved in the records. |
| **G2/C1-r** | prepositions | **Leading** place/time prepositions (`on, from, until, at`) and approximators (`around, about`) are **outside** the span. **Internal** connectives that complete the value (`in`, `of` — `8 in the night`, `10th of March`) are **inside**. Determiners/possessives **inside**. |
| **F1** | split | `for/of/with + N` quantities are **split**: `a table` + `three`, `tickets` + `four people`, `a hotel` + `3 rooms`. |
| **F2** | approximator | `around …` stays **outside**: `around 8 in the night` → `8 in the night`; `around 9:30 in the morning` → `9:30 in the morning`. |
| **threshold** | `at least` | `at least 4.2` stays **whole** (qualifier, not a preposition). |
| **G3** | C3 on agreed labels | Written C3 applied to agreed labels: bare `it`/`there` `REFERENCE`s are removed from gold. **Confirmed (2026-10-29, joint):** pilot-20 `it` [5-7] → removed; pilot-28 `there` [100-105] (P3) → removed; pilot-29 `there` [43-48] (`sgd_9c2a8dc501010484a5fd`) → removed. |

## 2. Train double-set T1–T6 (final)

| # | ID | Decision | Final spans |
|---|---|---|---|
| T1 | `SGD-835ec70f9e0a905054` | split (F1) | `a table` [68-75] · `three` [80-85] |
| T2 | `SGD-4dfe44204b3234df58` | around out (F2) | `the 9th` [34-41] · `8 in the night` [68-82] |
| T3 | `SGD-c5bd6a91af5fa668c3` | split (F1) | `a table` [54-61] · `four` [66-70] · `1:15 pm` [74-81] |
| T4 | `SGD-32ffc7799423754ec9` | split (F1) | `tickets` [50-57] · `four people` [62-73] |
| T5 | `SGD-148b0aee03a8931e50` | B | `an appointment` [15-29] · `the salon` [33-42] · REFERENCE `the same day` [45-57] · `11:15 in the morning` [61-81] |
| T6 | `SGD-9c4e5c1ad86443d8f3` | B | `a dentist appointment` [34-55] · REFERENCE `the same day` [59-71] (C6) |

## 3. Pilot-30 P1–P10 (final)

| # | ID | Decision | Final spans |
|---|---|---|---|
| P1 | `SGD-1bff672afd614f473b` | B (C4) | — (no span) |
| P2 | `SGD-3268166bbb220be170` | B (C2) | `13th of this month` [69-87] (`exciting and interesting` dropped) |
| P3 | `SGD-500c5b88b32a42951f` | A (C1-r) | `Vancouver` [40-49] · `Monday next week` [53-69] · UPDATE_CUE `Actually` [11-19] · REFERENCE `that date` [109-118] — agreed `there` [100-105] **removed (G3 confirmed)** |
| P4 | `SGD-50c2d5c01ea6273b` | ÖZEL (F3) | `a small rental car` [14-32] · `San Jose` [63-71] · `11th of March` [94-107] |
| P5 | `SGD-71a78f8aba480436` | A | `a salon` [16-23] |
| P6 | `sgd_43f2a82f62150cff` | A | `New York City` [20-33] · `a games event` [46-59] |
| P7 | `sgd_667a77ce3c34f0be` | ÖZEL (F3+G3) | — empty: `1 stop` unlabeled (C4), agreed `it` [5-7] removed |
| P8 | `sgd_a5d726d0e27a59f5` | B (C2) | — (no span) |
| P9 | `sgd_a7f975950eb100c6` | ÖZEL (F3) | `child-friendly` [58-72] (kept) · `a garden` [101-109]; bare `that` not labeled (C3) |
| P10 | `sgd_cb84c0478ba31271` | ÖZEL | `a restaurant` [71-83]; `there`/`near there` not labeled (C3) |

*P5/P6/P10 non-disputed spans (identical in both files) are preserved; tables show the decided content.*

## 4. Test-363 disposition rule (joint, registered BEFORE any model training/evaluation)

| Part | Rule |
|---|---|
| **3 of 63** | F1/F2 resolve them; joint decision: **take reviewer B's spans** for `SGD-473c2fae903c3d2740`, `SGD-afba777aac592e7d5d`, `SGD-01b297fc690c6a0e2b` |
| **60 of 63** | **No adjudication round.** Test reference = **only spans both reviewers agreed on**; each of the 60 records is reported as **UNRESOLVED** (one-sided spans excluded from the reference). |
| **Reporting** | The 60 unresolved records are reported explicitly in the evaluation report (count, ids, label breakdown) — never silently dropped or silently merged. |
| **Timing** | Test gold is built **after D5 training**, in one logged access (`reports/TEST_ACCESS_LOG.md`), by the mechanical builder + this rule. Coordinator has not read test label content; the 3-id decision above was given by the reviewers. |
| **Consistency check** | At test-gold build time, the 3 decided records are checked against written C1-r (offsets validated mechanically); any contradiction is surfaced to the reviewers before D6 — no model output is involved in that check. |

**Rationale (reviewers'):** the frozen two-annotator agreement already measures what both agreed on; disputed test spans are excluded rather than decided by a third party, keeping the test reference strictly human-consensus-based.

## 5. Consequences for gold construction (train/dev side)

| Segment | Records | Provenance rule |
|---|---|---|
| Pilot-30 | 30 | double-blind + joint decisions above |
| Calibration | 10 | discussed calibration round; **completion pending**: Burak +3 ids, Enes +4 ids (see §6) |
| Double-set 60 | 60 | double-blind + T1–T6 joint decisions |
| Solo A (Burak) | 178 | single annotation + **full second-eye verification by Enes** (DOGRULAMA sheet: all `K`, 0 changes) |
| Solo B (Enes) | 179 | single annotation + **full second-eye verification by Burak** (DOGRULAMA sheet: all `K`, 0 changes) |

Method statement for the report: *"457 records: 90 double-blind independently annotated (pilot-30 + 60 stratified double) and adjudicated by the two reviewers; 357 single-annotated with 100% second-reviewer verification (357/357 approved, 0 changes); 10 calibration items completed after discussion."*

## 6. Open items at the time of writing (both require reviewer action)

1. ~~**G3 confirmation for 2 labels**~~ → **RESOLVED 2026-10-29: both `there` labels removed** (joint confirmation; see §1 G3).
2. **Calibration completion** — Burak: fill `SGD-56999b51a110fa856a`, `sgd_b7dcd06bfc640bd25e55`, `sgd_ac18893cd1c26a16dfb0`; Enes: fill `SGD-4f7096486f77086be1` + the same 3 (all 4 are discussed-calibration items). **This is the last blocker before gold.**

**Signed (joint):** reviewer_A_BURAK (19:05 approval) · reviewer_B_ENES (session approval) — **Date:** 2026-10-29
**Transcribed by:** coordinator (mechanical; no label suggestions) · **Date:** 2026-10-29
