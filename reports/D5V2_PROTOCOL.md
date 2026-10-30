# D5-v2 — model development on gold v1.3 (PRE-REGISTERED 2026-10-30, before any v2 run)

**Status: PRE-REGISTERED.** Committed before any D5-v2 training run. Uses only train-side gold
(`data/gold/train_dev_gold_v1_3.jsonl`, SHA-256 `ce7b9a05…9dbc`, 857 records). The locked holdout is not opened;
`TEST_ACCESS_LOG.md` has no executed access. The v1.1 frozen row (`D5_RESULTS_V1_1.md`) stays as the reference.

## 1. Why a new procedure

On the 46-record dev the cue half of the selection metric rested on 4 spans and jumped between 0 / 0.4 / 0.57 / 0.67
across epochs. Model choices made on it are noise. D5-v2 replaces single-dev selection with grouped cross-validation
over all 857 train-side records.

## 2. Cross-validation (fixed now)

- 5 folds by dialogue family: `fold = int(sha256('20261101::<family>')[:8], 16) % 5`. No family is split across folds.
- Each fold: train on the other 4 folds for **10 epochs**; after every epoch, predict the held fold. No early stopping
  on the held fold.
- Score of a configuration at epoch *e*: out-of-fold predictions of all 857 records pooled, strict exact-span micro-F1
  per layer (`evaluate_spans.py`), **S(e) = mean(VALUE micro-F1, CUE micro-F1)**. Configuration score = max over *e*;
  **E\*** = that epoch.
- CV seed 20261029 (+ fold index for the per-fold run).

## 3. Search space (two stages, nothing else)

Fixed for all runs: AdamW lr 2e-5, weight decay 0.01, batch 16, grad-clip 1.0, fp32, max length 160 without history /
192 with history, labels on the first sub-token, word alignment by character offsets and the tokenizer's sequence ids,
history placed first and truncated before the utterance (`only_first`).

**Stage 1 — encoder** (history = no, loss = plain): `bert-base-cased`, `roberta-base`, `microsoft/deberta-v3-base`.
Highest score wins; exact ties go to the earlier name in this list.

**Stage 2 — context and loss** on the stage-1 encoder:
- history ∈ {`no`, `last_system` (the last SYSTEM turn, prefixed "SYSTEM: "), `tail60` (all history, last 60 words, as in v1)}
- loss ∈ {`plain`, `weighted` (cross-entropy weight 3.0 on every non-O tag, 1.0 on O)}
6 configurations; `no`/`plain` reuses the stage-1 result. Highest score wins; exact ties go to `no`, then `plain`.

## 4. Final model (fixed now)

Train the selected configuration on **all 857** records for E\* epochs with 3 seeds (20261029, 20261030, 20261031);
predict by averaging the per-tag softmax of the three models. Checkpoint SHA-256s, model revisions and E\* go into
`reports/D5V2_RESULTS.md`, committed **before** any test access. Nothing about the final model is chosen after that.

## 5. History hypothesis (the research question)

Reported from the CV (dev-side evidence): best `no`-history vs best history configuration on the selected encoder and
loss, with a 95% family-bootstrap interval of the difference in S (1000 resamples of families, seed 20261102).
At D6 the selected model and its counterpart with the history setting flipped (same encoder, loss, E\*, seeds) are
evaluated on the identical test records.

## 6. Rows that will appear at D6 (declared now)

B1 lexicon-copy, B2 surface rules and the CRF (c1 = c2 = 0.1, history = no) trained on all 857 with their fixed
configurations; the v1.1 frozen BERT checkpoint (411 records) as the "before" row; the D5-v2 final ensemble and its
history counterpart. Reporting scope follows SCOPE-001 (claims on NEW_VALUE, REFERENCE, UPDATE_CUE).

## 7. Dependencies (recorded, not tuned)

`sentencepiece` is installed for the DeBERTa-v3 tokenizer; `roberta-base` and `microsoft/deberta-v3-base` are downloaded
from the Hugging Face hub; their snapshot revisions are written to the result files. GPU: RTX 4060 Laptop (8 GB).

## 8. Not in scope

No CRF output layer, no learning-rate or batch search, no data augmentation, no use of the holdout. Any deviation is
recorded in `PROTOCOL_DEVIATIONS.md` before it is applied.
