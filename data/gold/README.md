# Gold annotations — status

**Train/dev gold v1 EXISTS (human-annotated, human-adjudicated). Test gold does NOT exist yet and is built only after model freeze.**

## What is here

| File | Status |
|---|---|
| `train_dev_gold_v1.jsonl` | 457 records, `source.split == train`, validator `--require-gold --allowed-splits train` → **PASS 457/457, 0 errors**. (File itself is gitignored; regenerate with `scripts/build_train_gold_v1.py` + `scripts/build_adjudicated_gold.py`.) |
| Test gold | **Intentionally absent.** The locked 363-record holdout is annotated (double-blind, both reviewers) but its reference is built in ONE logged access after D5 model freeze, per `EVALUATION_PROTOCOL_LOCK.md` and `reports/TEST_ACCESS_LOG.md`. |

## Provenance (no fabricated labels, ever)

- **90 double-blind** records (pilot-30 + stratified double-set-60) independently annotated by `reviewer_A_BURAK` and `reviewer_B_ENES`, then adjudicated **jointly by the two humans** (`reports/D3_ADJUDICATION_DECISIONS_FINAL.md`, 2026-10-29). A coordinator only transcribed decisions; no label suggestion was made by AI.
- **357 single-annotated** records with **100% second-eye verification** (357/357 approved `K`, 0 changes; `DOGRULAMA_*` sheets).
- **10 calibration** records completed after discussion (2 spans removed by recorded decision, 1 decided B-wins).
- All 18 joint decisions in `scripts/build_train_gold_v1.py` are asserted against the signed document's "Final spans" columns — the build aborts on any mismatch.
- Frozen agreement scores (computed pre-adjudication) are never recomputed: pilot `5e409339…`, test `36509d5f…`.

## Honest label support in train/dev gold v1 (N=457)

| Layer | Label | Count | Evaluable? |
|---|---|---|---|
| VALUE | NEW_VALUE | 368 | yes |
| VALUE | REFERENCE | 106 | yes |
| VALUE | KEPT_VALUE | 4 | marginal (tiny support) |
| VALUE | OLD_VALUE | **0** | **NOT EVALUABLE** |
| CUE | UPDATE_CUE | 74 | yes |
| CUE | CANCEL_CUE | 6 | marginal (tiny support) |
| CUE | KEEP_CUE | 1 | **NOT EVALUABLE in practice (n=1)** |
| CUE | RESTORE_CUE | **0** | **NOT EVALUABLE** |

- 151/457 records carry no span at all (legitimate empty-revision examples).
- `transitions` layer is present but empty (`[]`) in gold: transition schemas were inconsistent across reviewer files and the transition layer is outside the locked evaluation contract (VALUE + CUE heads only). Raw transition annotations remain in the reviewer working files.
- Baseline ceiling warning: this is a **difficult, low-frequency-span** task — any claimed "≥90% baseline" here must be scrutinized per the course rubric's saturation rule.

## Hard rules

- Never create or edit a gold JSONL by hand. Gold is produced only by the two builder scripts above from human review artifacts.
- `data/annotations/` (reviewer files, worksheets, verification sheets) and `data/gold/*` (except this README) are gitignored by `.gitignore`.
- Historical note: versions ≤ v0.7 of this README declared "GOLD NOT AVAILABLE" during the AI-simulated pre-pilot era; those simulated files were never used as gold and are excluded from every claim above.
