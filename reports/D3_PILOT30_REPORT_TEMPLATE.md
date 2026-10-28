# D3 Pilot-30 Result Report — TEMPLATE (fill when the two filled files arrive)

**Status:** TEMPLATE — no human annotations exist yet. Every value below stays `TBD` until two real independent reviewers deliver their files. Never fabricate a value.

## 0. Inputs (fill)

| Item | Value |
|---|---|
| reviewer A file / reviewer id | `TBD` |
| reviewer B file / reviewer id | `TBD` |
| Annotation dates / minutes per example | `TBD` |
| Guideline version used | v0.2 (or later, per change log) |
| Calibration done first? (10 items) | `TBD` |

## 1. Commands executed (run verbatim)

```bash
python scripts/normalize_review_packet.py --input data/annotations/d3_pilot30_v0.1/reviewer_A_filled.jsonl --reviewer-id <A> --out data/annotations/d3_pilot30_v0.1/reviewer_A_canonical.jsonl
python scripts/normalize_review_packet.py --input data/annotations/d3_pilot30_v0.1/reviewer_B_filled.jsonl --reviewer-id <B> --out data/annotations/d3_pilot30_v0.1/reviewer_B_canonical.jsonl
python scripts/annotation_agreement.py --a data/annotations/d3_pilot30_v0.1/reviewer_A_canonical.jsonl --b data/annotations/d3_pilot30_v0.1/reviewer_B_canonical.jsonl --exclude-ids data/annotations/d3_calibration_v0.1/calibration_index.json --out reports/D3_PILOT30_AGREEMENT.json
```

## 2. Agreement summary (from `D3_PILOT30_AGREEMENT.json`)

- Primary score (practice items excluded): example-level `exact_layer_set_agreement` = `TBD`
- Per-label exact-span agreement (`span_level_agreement_by_label`):

| Layer | Label | matched | only-A | only-B | symmetric F1 | support (A+B) |
|---|---|---|---|---|---|---|
| value_spans | NEW_VALUE | TBD | TBD | TBD | TBD | TBD |
| value_spans | OLD_VALUE | TBD | … | | | |
| value_spans | KEPT_VALUE | | | | | |
| value_spans | REFERENCE | | | | | |
| cue_spans | UPDATE_CUE | | | | | |
| cue_spans | KEEP_CUE | | | | | |
| cue_spans | CANCEL_CUE | | | | | |
| cue_spans | RESTORE_CUE | | | | | |

- `difficulty_agreement` = `TBD`; `uncertainty_flagged` A=`TBD` / B=`TBD`
- Calibration-included variant (disclosure only): `TBD`

## 3. Class supports observed in the pilot (human labels)

| Label | A count | B count | adjudicated expectation | note |
|---|---|---|---|---|
| … | TBD | TBD | TBD | zero support → `NOT EVALUABLE`, never hidden |

## 4. Problem analysis (CTO list)

- **Bad spans** (offset/text mismatches, same-layer overlaps — should be zero with the helper; list any from manual edits): `TBD`
- **DP-1 (refusal ≠ CANCEL) disagreements:** `TBD` — list example IDs + who labeled what + root cause
- **DP-2 (topic-return ≠ value-restore) disagreements:** `TBD`
- **Other rule ambiguities** (ADD vs UPDATE, KEPT vs NEW, REFERENCE): `TBD`
- **Uncertainty pattern** (are `UNCERTAIN:` flags clustered in one bucket?): `TBD`

## 5. Decision — GO / REVISE / STOP (pick one, justify)

| Decision | Criteria |
|---|---|
| **GO** | per-label agreement acceptable on supported labels; DP-1/DP-2 applied consistently; no systematic offset errors; workload realistic (target ≤ 3 min/example) → proceed to full pass (417 remaining) |
| **REVISE** | recurring rule confusion → guideline version bump + affected example IDs logged; re-trial on a small set; **locked test selection never changes** |
| **STOP** | fundamental construct problem (e.g. labels not observable in text) → report honestly; consider the AI-assisted fallback with limited academic claims |

**Decision:** `TBD` | **Signed (owner):** `TBD` | **Date:** `TBD`

## 6. Integrity statement

This report is completed only from real human annotations. No AI labels were used or presented as human work. No gold was produced at this stage (gold requires adjudication per `D3_GOLD_CREATION_PROTOCOL.md`). The sealed test set (363) was not opened.
