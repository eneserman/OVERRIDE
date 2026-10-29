# D5 — Split Freeze Report (2026-10-29, BEFORE any model training)

**Status:** TRAIN/DEV SPLIT FROZEN. Model selection may use ONLY this train-side dev partition. The locked holdout stays untouched for the single D6 run.

## Inputs

| Item | Value |
|---|---|
| Gold | `data/gold/train_dev_gold_v1.jsonl` — 457 records, validator PASS |
| Gold content SHA-256 | `d0196b19452ae3fa273dd19c716cda4334f2a9bfef5345530d6938d513d12a42` |
| Pre-committed plan | `reports/D3_TRAIN_DEV_SPLIT_PLAN.json` — 454 families, seed `20261028`, committed BEFORE annotation |
| Frozen manifest | `reports/splits/frozen_plan_traindev_gold_v1.json` (local, gitignored) |
| **manifest_digest** | `9f864d551df9d621b979bf801030eae5e5b74aa5dc8b20d2afed7ffce37a6c5c` |

## Plan rule (verified, not assumed)

`bucket = sha256('20261028::<family>')[:15] / 16^15`; `bucket < 0.10 → dev, else train`.
Re-derivation over all 454 families reproduces the committed assignment with **0 mismatches**; gold's family set equals the plan's family set exactly (454/454; 3 families contain 2 records each → 457 records).

## A6 conflict handling (generic freeze vs pre-committed plan)

`freeze_gold_splits.py --seed 20261028` (generic 80/10/10 bucketing) produced **360/46/51** and disagrees with the plan on **142 families**. Per `D3_GOLD_CREATION_PROTOCOL` A6: **do not pick the favorable one** → resolution: `PRE_COMMITTED_PLAN_WINS`, conflict recorded here and inside the manifest (`conflict_with_generic_freeze`). The generic script's "test" bucket (51 train-side records) is **not** a test set under the plan — those records live in train/dev; the real test remains the separate locked holdout (`b42299f8…0581`).

## Frozen counts

| Split | Families | Records |
|---|---|---|
| train | 409 | 411 |
| dev | 45 | 46 |

## Gold span support per split (honest, pre-training)

| Label | train | dev | Note |
|---|---|---|---|
| NEW_VALUE | 333 | 35 | healthy |
| REFERENCE | 99 | 7 | dev small |
| KEPT_VALUE | 3 | 1 | marginal both sides |
| UPDATE_CUE | 71 | 3 | **dev n=3 → dev cue scores are indicative only** |
| CANCEL_CUE | 6 | **0** | **NOT EVALUABLE in dev** (train-only n=6) |
| KEEP_CUE | 0 | 1 | **NOT EVALUABLE in train** (single dev instance) |
| OLD_VALUE | 0 | 0 | NOT EVALUABLE |
| RESTORE_CUE | 0 | 0 | NOT EVALUABLE |

Consequences declared BEFORE training:
1. Dev-based model selection is driven by VALUE spans (NEW_VALUE/REFERENCE/KEPT_VALUE) + UPDATE_CUE counts; per-class numbers for empty dev classes are reported as **NOT EVALUABLE**, never as 0.
2. Tiny-dev classes (UPDATE_CUE n=3, KEPT_VALUE n=1, REFERENCE n=7) are reported with denominators and flagged unstable.
3. No split re-draw will be attempted after seeing any model output. This manifest is immutable (`freeze_plan_split.py` refuses overwrite).

## Reproduce

```bash
python scripts/freeze_gold_splits.py --gold data/gold/train_dev_gold_v1.jsonl \
  --out reports/splits/freeze_script_seed20261028.json --seed 20261028   # documented conflict
python scripts/freeze_plan_split.py --gold data/gold/train_dev_gold_v1.jsonl \
  --plan reports/D3_TRAIN_DEV_SPLIT_PLAN.json \
  --compare reports/splits/freeze_script_seed20261028.json \
  --out reports/splits/frozen_plan_traindev_gold_v1.json                  # authoritative split
```
