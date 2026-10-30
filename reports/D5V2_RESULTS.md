# D5-v2 — results and final model freeze (2026-10-30, BEFORE any test access)

**Status: FROZEN.** Applies `D5V2_PROTOCOL.md` (commit `fd06ef0`) without deviation. The locked holdout has not been
opened; `TEST_ACCESS_LOG.md` has no executed access. Nothing about the final models is chosen after this commit.

| Input | Value |
|---|---|
| Gold | `data/gold/train_dev_gold_v1_3.jsonl`, 857 records, SHA-256 `ce7b9a054138b48f1bbc18544ccc7374ed7b05e9196048317feb072fa8a39dbc` |
| CV | 5 folds by dialogue family (salt `20261101`), 10 epochs, pooled out-of-fold scoring, `scripts/d5v2_cv.py` |
| Encoders (HF revisions) | `bert-base-cased` `cd5ef92a…f221e`, `roberta-base` `e2da8e2f…bffac7b`, `microsoft/deberta-v3-base` `8ccc9b6f…53f3` |
| Hardware | RTX 4060 Laptop 8 GB, torch 2.14.1+cu126, transformers 5.22.0 |

## 1. Stage 1 — encoder (history = no, loss = plain)

| Encoder | VALUE F1 | CUE F1 | **S** | E\* |
|---|---|---|---|---|
| bert-base-cased | 0.862 | 0.814 | 0.838 | 8 |
| roberta-base | 0.872 | 0.807 | 0.839 | 8 |
| **microsoft/deberta-v3-base** | **0.891** | **0.830** | **0.860** | 6 |

Selected: **DeBERTa-v3-base** (highest S).

## 2. Stage 2 — context and loss (DeBERTa-v3-base)

| History | Loss | VALUE F1 | CUE F1 | **S** | E\* |
|---|---|---|---|---|---|
| **no** | **plain** | **0.891** | **0.830** | **0.860** | 6 |
| no | weighted | 0.872 | 0.818 | 0.845 | 5 |
| last_system | plain | 0.882 | 0.827 | 0.854 | 8 |
| last_system | weighted | 0.873 | 0.815 | 0.844 | 9 |
| tail60 | plain | 0.884 | 0.827 | 0.856 | 6 |
| tail60 | weighted | 0.877 | 0.814 | 0.846 | 6 |

Selected configuration: **DeBERTa-v3-base, history = no, loss = plain, E\* = 6.** The class-weighted loss is lower in
every history mode (−0.010 to −0.015).

Per-label out-of-fold F1 of the selected configuration (epoch 6; strict exact span):

| Label | Gold spans | Precision | Recall | F1 |
|---|---|---|---|---|
| NEW_VALUE | 764 | 0.888 | 0.923 | **0.905** |
| REFERENCE | 189 | 0.835 | 0.857 | **0.846** |
| UPDATE_CUE | 226 | 0.833 | 0.863 | **0.848** |
| CANCEL_CUE / KEPT_VALUE / OLD_VALUE / KEEP_CUE / RESTORE_CUE | 7 / 3 / 3 / 2 / 1 | — | — | 0.000 |

The five rare labels (16 spans in total) are never predicted correctly; this matches SCOPE-001, which keeps them out
of the claims.

## 3. History hypothesis (protocol section 5)

Best no-history vs best history configuration with the selected encoder and loss (`plain`): `no` (S 0.8602) vs
`tail60` (S 0.8556). Family bootstrap, 1000 resamples of 854 families, seed 20261102 (`scripts/d5v2_bootstrap.py`,
`reports/D5V2_HISTORY_BOOTSTRAP.json`):

| Difference S(tail60) − S(no) | 95% interval | Resamples where history is better |
|---|---|---|
| −0.0046 | [−0.0205, +0.0117] | 29.2% |

**No evidence that dialogue history helps on this data**; the interval contains zero. Per-epoch S shows history ahead
in the early epochs (epoch 1: 0.421 vs 0.281; epoch 4: 0.846 vs 0.829) and the gap closing from epoch 6 on.

## 4. Final models (protocol section 4)

Each checkpoint: all 857 records, 6 epochs, AdamW lr 2e-5, batch 16, fp32 (`scripts/d5v2_final.py train`). Prediction =
average of the per-tag softmax of the three seeds (`scripts/d5v2_final.py predict`). Checkpoints are local
(`reports/train_runs/d5v2_final/`, gitignored); their SHA-256s are frozen here.

**Selected — history = no** (`reports/train_runs/d5v2_final/no/`):

| Seed | Checkpoint SHA-256 |
|---|---|
| 20261029 | `1e6f2a9158d75095b00389ae3d3c59c394e1c4f0c04bb9626f94817c6e94d55c` |
| 20261030 | `c5254d9d53fe40ac9582b258236a80c5176a918428c871f36ca462b2e9764f6f` |
| 20261031 | `b828c91a2323063cdf360e68a61c53f3f28fc8fe4d6837123f08c3667779ca57` |

**History counterpart — history = tail60** (same encoder, loss, E\*, seeds; `tail60` is the best history mode in §3):

| Seed | Checkpoint SHA-256 |
|---|---|
| 20261029 | `506465da621c84444ced2f5fe42b08cbc0be5fe1d5fe60c115b242e54df634a4` |
| 20261030 | `16ff514c79fdc0518838ed3d9b397793b6efca0e020b70050e79e185db672f8d` |
| 20261031 | `666d6e7b92a92cbd22dea9a0fc16d6a3ac2eb02e04777a08bbe78b83fa025088` |

## 5. What D6 will report (unchanged from protocol section 6)

On the 363 locked test records, in one logged access, scored once with `scripts/evaluate_frozen_test.py
--accept-consensus-reference`: B1 lexicon-copy, B2 surface rules and the CRF (history = no) fitted on all 857
(`scripts/d6_baselines.py`); the v1.1 BERT checkpoint (`d5_tf_v1_1/checkpoint_tf_hno.pt`, SHA-256 `770b90d4…1a61`)
as the "before" row; the D5-v2 ensemble (history = no) and its tail60 counterpart. Claims follow SCOPE-001.

## 6. Reading these numbers honestly

- CV scores are dev-side evidence on the 857 train-side records; the test set comes from different official SGD
  splits and 60 of its 363 references are reviewer intersections (DEV-001), so test scores may be lower.
- These scores are not comparable to the v1.1 dev row (0.681): different gold, 46 vs 857 scored records.
- The human span agreement of round 2 (`D3_EXT2_AGREEMENT.json`) was measured on raw first submissions, the model on
  the adjudicated gold; they are different quantities and are not presented as "model beats humans".

## Reproduce

```bash
python scripts/d5v2_cv.py --gold data/gold/train_dev_gold_v1_3.jsonl --model microsoft/deberta-v3-base --history no --loss plain --outdir reports/train_runs/d5v2_cv
python scripts/d5v2_bootstrap.py --gold data/gold/train_dev_gold_v1_3.jsonl --a reports/train_runs/d5v2_cv/deberta-v3-base__no__plain/oof_epoch6.jsonl --b reports/train_runs/d5v2_cv/deberta-v3-base__tail60__plain/oof_epoch6.jsonl --out reports/D5V2_HISTORY_BOOTSTRAP.json
python scripts/d5v2_final.py train --gold data/gold/train_dev_gold_v1_3.jsonl --model microsoft/deberta-v3-base --history no --loss plain --epochs 6 --seed 20261029 --outdir reports/train_runs/d5v2_final/no   # seeds 20261030, 20261031; --history tail60 for the counterpart
```
