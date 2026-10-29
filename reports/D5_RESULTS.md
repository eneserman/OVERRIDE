# D5 — Development Results & MODEL FREEZE (2026-10-29)

**Status: MODEL FROZEN BEFORE ANY TEST ACCESS.** Development used ONLY the frozen
train/dev partition (`frozen_plan_traindev_gold_v1.json`, manifest `9f864d55…`).
The locked 363-record holdout has not been opened, referenced, or peeked at in any
model decision in this document.

## 1. Declared selection procedure (committed BEFORE any run)

From `scripts/d5_train_transformer.py` docstring, committed at `aa78875`
(git history predates the first transformer run):

> train split only; dev used solely for early-stopping model selection;
> selection metric = mean(dev value micro-F1, dev cue micro-F1);
> max 30 epochs, patience 5 evals; best weights kept; seeds recorded;
> no hyperparameter search beyond this single fixed configuration (only the
> documented history ablation repeats the run).

CRF configuration fixed at c1=0.1, c2=0.1, max_iter=200 (defaults, no search).
Cross-system comparison metric: **dev mean(value micro-F1, cue micro-F1)**.

## 2. Dev results (N=46 records; exact-offset labeled span F1)

| System | Value micro-F1 | Cue micro-F1 | Mean | Notes |
|---|---|---|---|---|
| B0 empty (predict nothing) | 0.000 | 0.000 | 0.000 | documents the accuracy trap (151/457 gold records are span-less) |
| B1 lexicon-copy | 0.370 | 0.500 | 0.435 | memorized train span texts |
| B2 surface rules | 0.319 | 0.375 | 0.347 | cue phrases + value patterns |
| CRF + history | 0.625 | 0.400 | 0.513 | |
| CRF no history | 0.633 | 0.400 | 0.516 | |
| Two-head BERT + history | 0.630 | 0.667 | 0.649 | best epoch 3 |
| **Two-head BERT no history** | **0.637** | **0.667** | **0.652** | **SELECTED (best epoch 4)** |

**Selection applied mechanically:** highest dev mean → `checkpoint_tf_hno.pt`
(value 0.6374, cue 0.6667). The two BERT conditions differ by 0.0034 (within
dev noise); the declared rule was applied as written — no re-interpretation
after seeing numbers.

## 3. Selected model (frozen artifact)

| Field | Value |
|---|---|
| Architecture | `bert-base-cased` shared encoder + 2 linear token heads (VALUE, CUE) |
| Input | current utterance only (history=**no**; history variant = required ablation) |
| Seed | `20261029` (python/numpy/torch); rerun reproduced epoch losses & metrics **byte-identical** |
| Optimizer | AdamW lr=2e-5, weight decay=0.01, grad clip 1.0, batch 16, max_len 160 |
| Early stopping | max 30 epochs, patience 5, metric = mean(dev value, cue) micro-F1 → best epoch 4 |
| Checkpoint | `reports/train_runs/d5_tf/checkpoint_tf_hno.pt` (local; train_runs/ gitignored) |
| Checkpoint SHA-256 | `1fad3a569f383c11…` (full hash in `metrics_tf_hno_dev.json`) |
| Ablation checkpoint | `checkpoint_tf_hwith.pt` (history=with, best epoch 3) |
| Device | RTX 4060 Laptop (CUDA), torch 2.14.1+cu126 |

## 4. Per-class dev detail (honest denominators)

Selected model (no-history), dev:

| Layer | Label | F1 | tp/fp/fn | Status |
|---|---|---|---|---|
| VALUE | NEW_VALUE | 0.676 | 25/14/10 | evaluable (gold n=35) |
| VALUE | REFERENCE | 0.500 | 4/5/3 | evaluable but tiny (gold n=7) |
| VALUE | KEPT_VALUE | 0.000 | 0/0/1 | **n=1, unstable, report with denominator** |
| VALUE | OLD_VALUE | — | — | **NOT EVALUABLE (dev gold n=0)** |
| CUE | UPDATE_CUE | 0.800 | 2/0/1 | tiny (dev gold n=3) |
| CUE | CANCEL_CUE | — | — | **NOT EVALUABLE (dev gold n=0)** |
| CUE | KEEP_CUE | 0.000 | 0/0/1 | **train support 0 → unlearnable; dev n=1** |
| CUE | RESTORE_CUE | — | — | **NOT EVALUABLE (dev gold n=0)** |

Same declarations carry to the final test report with test denominators (frozen
agreement already showed OLD_VALUE/CANCEL_CUE are tiny in the holdout too).
No model in this table exceeds 0.90 anywhere → task is demonstrably unsaturated.

## 5. History ablation (declared, identical example IDs)

| Condition | dev value | dev cue | dev mean |
|---|---|---|---|
| with history (tail 60 words as pair input) | 0.630 | 0.667 | 0.6486 |
| without history | 0.637 | 0.667 | 0.6520 |

Finding: history conditioning gave **no measurable gain** on dev (Δ=0.0034).
Revision information is largely present in the current utterance itself for
these 46 dev records. Reported as-is; at D6 both conditions are evaluated on
the identical test IDs, and the SELECTED condition (no-history) stays primary
regardless of test outcomes.

## 6. Model freeze — what is now immutable

1. Selected system + checkpoint + config + seed (§3). Any change = new freeze
   record declared BEFORE test access; silent swaps forbidden.
2. D6 procedure (next, in order):
   a. ONE logged test access (`reports/TEST_ACCESS_LOG.md`): build consensus
      test reference per `D3_ADJUDICATION_DECISIONS_FINAL` §4 rule (3 IDs take
      reviewer B's spans; 60 unresolved = both-agreed intersection, DEV-001),
      mechanical C1-r check on the 3 decided records, combined gold +
      train/dev/test manifest, family-overlap check (must be 0).
   b. Inference only with the frozen checkpoints (no retraining).
   c. Single evaluation through `scripts/evaluate_frozen_test.py`.
3. The holdout remains unopened until 2.a. Nothing in D5 used it.

## 7. Reproduce

```bash
python scripts/d5_prepare_data.py --gold data/gold/train_dev_gold_v1.jsonl \
  --manifest reports/splits/frozen_plan_traindev_gold_v1.json --outdir data/intermediate/d5
python scripts/d5_run_baselines.py --gold data/gold/train_dev_gold_v1.jsonl \
  --manifest reports/splits/frozen_plan_traindev_gold_v1.json --outdir reports/train_runs/d5_baselines
python scripts/d5_train_crf.py --data data/intermediate/d5 --gold data/gold/train_dev_gold_v1.jsonl \
  --outdir reports/train_runs/d5_crf --history with   # and --history no
python scripts/d5_train_transformer.py --data data/intermediate/d5 \
  --gold data/gold/train_dev_gold_v1.jsonl --outdir reports/train_runs/d5_tf --history no  # selected
```
