# D5 — Train/Dev Gold v1 Build (2026-10-29)

**Status:** GOLD v1 CLOSED — validator `--require-gold --allowed-splits train` → **PASS, 457/457, 0 errors**. D5 model development may begin against this file only.

## Build procedure (reproducible)

1. `python scripts/build_train_gold_v1.py`
   - inputs: pilot-30 both canonicals, calibration-10 canonicals (decisions already merged), full-457 both canonicals + `assignment_index.json`
   - transcribes all **18 joint human decisions** (T1–T6, P1–P10, pilot-29/G3, calibration-completion) from `reports/D3_ADJUDICATION_DECISIONS_FINAL.md`
   - **mechanically asserts** every decided record's final spans against the signed document's "Final spans" columns (boundary + explicitly-stated labels); aborts on any mismatch → build passed with 0 problems
   - outputs `data/annotations/d3_gold_v1/{side_A,side_B,decisions_457}.jsonl`
2. `python scripts/build_adjudicated_gold.py --a side_A --b side_B --decisions decisions_457 --adjudicator "reviewer_A_BURAK+reviewer_B_ENES_joint" --log-id "D3-ADJ-2026-10-29-FINAL" --allowed-splits train --require-all --out data/gold/train_dev_gold_v1.jsonl`
   - 457 records, `undecided_omitted: 0`
3. `python scripts/validate_annotations.py --input data/gold/train_dev_gold_v1.jsonl --require-gold --allowed-splits train` → PASS
4. Full test suite at the same commit: **77/77 passed**.

## Provenance mix (recorded in each gold row's `annotation.decision_reason`)

| Segment | N | Rule |
|---|---|---|
| Double-blind, agreed | 82 | identical independent annotations (pilot non-disputed + cal non-disputed + double-set non-disputed) |
| Double-blind, adjudicated | 18 | joint human decisions (T1–T6, P1–P10, pilot-29, cal-completion) |
| Single + 100% second-eye verification | 357 | all `K`, zero changes (both DOGRULAMA sheets) |
| **Total** | **457** | |

## Label support (honest, from the written file)

| Layer | Label | N | Status |
|---|---|---|---|
| VALUE | NEW_VALUE | 368 | evaluable |
| VALUE | REFERENCE | 106 | evaluable |
| VALUE | KEPT_VALUE | 4 | marginal |
| VALUE | OLD_VALUE | **0** | **NOT EVALUABLE** |
| CUE | UPDATE_CUE | 74 | evaluable |
| CUE | CANCEL_CUE | 6 | marginal |
| CUE | KEEP_CUE | 1 | **NOT EVALUABLE (n=1)** |
| CUE | RESTORE_CUE | **0** | **NOT EVALUABLE** |

- 151/457 records have no spans (empty-revision negatives — real, kept).
- `transitions: []` in all 457 rows (locked eval = VALUE + CUE heads; raw transitions preserved in reviewer files).
- Any model report must state the NOT EVALUABLE classes before scoring; per-class scores for them are reported as NOT EVALUABLE, never as 0 or as a silent omission.

## Frozen agreement untouched

Pilot `5e409339…` and test `36509d5f…` remain the pre-adjudication scores. Adjudication changed gold only.

## Test side

Test reference is **not** built yet. After model freeze: one logged access (`reports/TEST_ACCESS_LOG.md`), mechanical rule (3 decided IDs take B's spans + 60 unresolved use both-agreed intersection, **DEV-001** disclosed), single D6 run.
