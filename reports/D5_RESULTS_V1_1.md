# D5 — Results on gold v1.1 (2026-10-30, same frozen configuration, BEFORE any test access)

**Status: v1.1 BASELINE ROW.** Same scripts, seed `20261029` and selection rule as `D5_RESULTS.md`; only the gold changed
(v1 → v1.1: 3 records, `D3_GOLD_V1_1_DECISIONS.md`). The locked holdout has not been opened. This is the
reference row that any later D5-v2 change is compared against; it is **not** the final model freeze if D5-v2
is run (a D5-v2 freeze record must be committed before any test access).

## Inputs

| Item | Value |
|---|---|
| Gold | `data/gold/train_dev_gold_v1_1.jsonl` SHA-256 `6f0181c5…37b3` |
| Split | `reports/splits/frozen_plan_traindev_gold_v1_1.json`, digest `d60942ec…ea2b`; **membership identical to v1** (411 train / 46 dev, 409 / 45 families) |
| Data prep | `data/intermediate/d5_v1_1/` |

## Dev results (N=46; exact-offset span micro-F1)

| System | Value | Cue | Mean | v1 mean |
|---|---|---|---|---|
| B0 empty | 0.000 | 0.000 | 0.000 | 0.000 |
| B1 lexicon-copy | 0.415 | 0.500 | 0.457 | 0.435 |
| B2 surface rules | 0.337 | 0.375 | 0.356 | 0.347 |
| CRF + history | 0.610 | 0.400 | 0.505 | 0.513 |
| CRF no history | 0.617 | 0.400 | 0.509 | 0.516 |
| BERT + history | 0.688 | 0.667 | 0.677 | 0.649 |
| **BERT no history** | **0.696** | **0.667** | **0.681** | 0.652 |

Selection (declared rule, applied mechanically): **BERT no-history**, best epoch 4, checkpoint
`reports/train_runs/d5_tf_v1_1/checkpoint_tf_hno.pt` SHA-256 `770b90d4b7db9718de65898890b57aacefa24af4f97c36bbfee36a6b69081a61`.
Ablation (history=with): best epoch 3, `checkpoint_tf_hwith.pt` SHA-256 `8063e2008fca8a1a8d1f7e00329858968b69f5a11f843c0f12df6e0927e9e431`.

## Reading these numbers honestly

- The v1 → v1.1 rise (0.652 → 0.681) is **not** a model improvement: the dev labels themselves changed in 2 of 46
  records (A1 split, one `the same day` relabel), so the two rows are measured on different references.
- **The cue half of the selection metric rests on 4 dev spans** (3 UPDATE_CUE + 1 KEEP_CUE). Across epochs the dev cue
  F1 only takes the values 0 / 0.4 / 0.571 / 0.667, and it decides the selected epoch: epoch 8 reached value 0.796 but
  cue 0.4 and was not chosen. Model selection on this dev set is therefore very noisy — the main motivation for the
  planned D5-v2 grouped cross-validation.
- History vs no history: Δ = 0.004 on the mean, within this noise. No evidence of a context gain yet.

## Reproduce

```bash
python scripts/freeze_plan_split.py --gold data/gold/train_dev_gold_v1_1.jsonl --plan reports/D3_TRAIN_DEV_SPLIT_PLAN.json \
  --compare reports/splits/freeze_script_seed20261028.json --out reports/splits/frozen_plan_traindev_gold_v1_1.json
python scripts/d5_prepare_data.py --gold data/gold/train_dev_gold_v1_1.jsonl --manifest reports/splits/frozen_plan_traindev_gold_v1_1.json --outdir data/intermediate/d5_v1_1
python scripts/d5_run_baselines.py --gold data/gold/train_dev_gold_v1_1.jsonl --manifest reports/splits/frozen_plan_traindev_gold_v1_1.json --outdir reports/train_runs/d5_baselines_v1_1
python scripts/d5_train_crf.py --data data/intermediate/d5_v1_1 --gold data/gold/train_dev_gold_v1_1.jsonl --outdir reports/train_runs/d5_crf_v1_1 --history with   # and --history no
python scripts/d5_train_transformer.py --data data/intermediate/d5_v1_1 --gold data/gold/train_dev_gold_v1_1.jsonl --outdir reports/train_runs/d5_tf_v1_1 --history no   # and --history with
```
