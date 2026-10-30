# D6 — Locked prospective test results (single access, 2026-10-30)

**Status: FINAL.** One logged access (`TEST_ACCESS_LOG.md` row 1), after the model freeze `2702a45` (pushed before
the access). Every system below was frozen before the test was opened; nothing was trained, tuned or selected on it.
Deviations during the access: DEV-002 (family key = official split + dialogue ID, `PROTOCOL_DEVIATIONS.md`) and two
crash fixes of the never-executed v1.1 inference script (its output was checked to reproduce the recorded v1.1 dev
predictions on 46/46 records).

## Test set

| Item | Value |
|---|---|
| Records | 363 user turns from official SGD **dev/test** dialogues (358 families); no dialogue shared with the 857 train-side records |
| Reference | DEV-001 consensus: 300 records with identical reviewer annotations, 3 decided by rule, 60 = intersection of the two reviewers (one-sided spans excluded: 83 VALUE, 11 CUE) |
| Spans | NEW_VALUE 315, REFERENCE 114, UPDATE_CUE 31, KEPT_VALUE 3; 87 records contain no span |
| Files | `data/gold/test_reference_v1.jsonl`; full gold + 3-way manifest digest `dea1d83a…4c23`, gold content SHA-256 `8a3e9fd7…c4b4` |
| Scorer | `scripts/evaluate_frozen_test.py --accept-consensus-reference` (strict exact-span micro-F1), reports in `reports/d6_test/` |

## Main table

| System | Train data | VALUE F1 | CUE F1 | **S** |
|---|---|---|---|---|
| B1 lexicon copy | 857 | 0.526 | 0.414 | 0.470 |
| B2 surface rules | 857 | 0.462 | 0.364 | 0.413 |
| CRF (history = no) | 857 | 0.758 | 0.712 | 0.735 |
| BERT-base v1.1 (history = no), "before" row | 411 | 0.780 | 0.644 | 0.712 |
| **DeBERTa-v3 ensemble, history = no — selected model** | 857 | **0.845** | **0.691** | **0.768** |
| DeBERTa-v3 ensemble, history = tail60 — pre-registered counterpart | 857 | 0.870 | 0.757 | 0.813 |

S = mean of VALUE and CUE micro-F1. The **headline result is the selected model (S 0.768)**: it is the one fixed by
the protocol before the test was opened. The tail60 row is the pre-registered history comparison, not a re-selection.

## Per label (SCOPE-001 claim labels)

| System | NEW_VALUE (315) | REFERENCE (114) | UPDATE_CUE (31) |
|---|---|---|---|
| CRF | 0.788 | 0.685 | 0.712 |
| BERT v1.1 | 0.788 | 0.768 | 0.644 |
| DeBERTa-v3, history = no | 0.858 | 0.821 | 0.691 |
| DeBERTa-v3, history = tail60 | 0.881 | 0.850 | 0.757 |

KEPT_VALUE (3 spans) is 0.000 for every system (out of scope, SCOPE-001).

## History hypothesis on the test set

Family bootstrap (1000 resamples, seed 20261102) on the identical 363 records — **descriptive**: the protocol
pre-registered the comparison of the two models, not this interval.

| Comparison | ΔS | 95% interval | Resamples where B is better |
|---|---|---|---|
| tail60 − no (DeBERTa ensembles) | **+0.045** | **[+0.016, +0.078]** | 99.8% |
| DeBERTa (no) − CRF | +0.033 | [−0.017, +0.079] | 92.3% |

**Cross-validation and test disagree on history.** On the 857 train-side records history did not help (−0.005,
[−0.021, +0.012]); on the prospective test it helps (+0.045, interval above zero), on every claim label. A plausible
reading, not tested here: the test turns come from different official SGD splits and contain relatively more
REFERENCE spans (114 of 432 value spans = 26% vs 189 of 959 = 20% in train), the label that most needs earlier turns; CV errors of the
REFERENCE-vs-NEW_VALUE type (`ERROR_ANALYSIS_CV.md` §3) point the same way. The selection rule chose the model that was
best on development data; the test shows that this choice did not transfer, which is exactly what a locked test is for.

## Reading the numbers honestly

- **v1.1 → v2:** +0.056 S (0.712 → 0.768) from more and better data (411 → 857 records, all new records
  double-blind), a better encoder and CV-based selection. The components are not separated.
- **Cue scores rest on 31 UPDATE_CUE spans** and are noisy. Cue precision is the weak point of every neural system
  (0.49–0.65 at recall ≈ 0.90): part of it is the intersection reference, which drops cues only one reviewer marked.
- **The DeBERTa vs CRF gap is not significant on this test** (interval includes 0), although DeBERTa is better on
  VALUE in every comparison.
- CV S (0.860) vs test S (0.768): the drop is expected for a prospective test from other splits with a stricter,
  intersection-based reference.

## Reproduce (requires the frozen checkpoints and the local test reference)

```bash
python scripts/d6_baselines.py --train-gold data/gold/train_dev_gold_v1_3.jsonl --input data/gold/test_reference_v1.jsonl --outdir reports/train_runs/d6
python scripts/d6_infer_frozen.py --checkpoint reports/train_runs/d5_tf_v1_1/checkpoint_tf_hno.pt --input data/gold/test_reference_v1.jsonl --out reports/train_runs/d6/pred_bert_v1_1_hno.jsonl
python scripts/d5v2_final.py predict --checkpoints reports/train_runs/d5v2_final/no/final_seed20261029.pt reports/train_runs/d5v2_final/no/final_seed20261030.pt reports/train_runs/d5v2_final/no/final_seed20261031.pt --input data/gold/test_reference_v1.jsonl --out reports/train_runs/d6/pred_deberta_v2_ens_hno.jsonl   # same with tail60/
python scripts/evaluate_frozen_test.py --full-gold data/gold/full_gold_v1_3_plus_test.jsonl --manifest reports/splits/frozen_full_manifest_v1_3.json --test-predictions reports/train_runs/d6/pred_<system>.jsonl --out reports/d6_test/metrics_<system>.json --accept-consensus-reference
```
