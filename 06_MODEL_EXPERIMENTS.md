# 06 — Model & Experiment Protocol

**Status: preregistration / experimental plan; no trained models or measurements exist.** Do not convert the examples below to result claims.

## Primary scientific claim to test
With the same gold annotations and split, a history-aware token tagger improves strict exact-span F1 on revision values/cues compared with a last-message-only tagger. Secondary question: does that difference persist for L3–L5 and hard negatives?

## Prerequisites (HARD BLOCK)
- Google SGD `train` source commit + file hashes recorded; D0 audit executed on real data.
- Anotator A/B files genuinely completed independently; conflict log; adjudicated spans pass validator; uncertain items remain tracked.
- Enough real training / validation / test support per declared class; if not, reduce training label set via written decision and keep rare items diagnostic.
- Frozen dialogue/family split, plus leakage/near-duplicate checks; official SGD dev/test cannot silently become new gold.

## Baselines and models
1. **Rules/lexical baseline:** transparent matching of cues, naive value spans; no history oracle. Important because task may become trivial without proper hard negatives.
2. **Linear-chain CRF:** contextual token features built from current utterance, optionally bounded history flags; train only on gold. Clearly describe which features require gold or are derived from raw text.
3. **Transformer token classifier:** a modest English encoder (`bert-base-uncased` or appropriate RoBERTa variant, finalized after hardware check); two prediction heads OR two trained classifiers for VALUE and CUE. Use offset alignment and padding/history masks. Do not claim an LLM API is a trained token-classification model.

## Required ablations
- Last-user-turn-only versus history-aware with identical encoder and train/dev/test.
- With versus without context for L4/L5; report counts and confidence intervals if meaningful.
- Rule baseline vs CRF vs Transformer on same final gold test.
- Optional history length (0, 2, 4, 8 prior turns) if compute allows. Distinguish exploratory and confirmatory results.

## Labeling/token rules
Character `[start,end)` is source of truth. Tokenizer offsets map spans onto subwords. Loss on **current USER tokens only**; padding, system/history, and excluded continuation subwords masked `-100`. Invalid alignment raises or is logged with explanation; no silent drops. Within-head overlap is a review error. No current or future state given at inference time.

## Hyperparameter selection
Fixed seed(s) (e.g., 42, 43, 44 if feasible), document optimizer/lr/batch/epochs/patience/max_length/selection metric. Tune on validation only. No test-driven model selection. Record GPU hours, oom handling, truncation percentage; final test once for selected config. Preserve random generator and source snapshot.

## Output artifacts (expected only after actual runs)
- `configs/experiments/*.json`, `reports/train_runs/<run_id>/config.json`, `metrics_dev.json`, `metrics_test.json`, timing and hardware notes.
- Predicted spans JSONL, trained checkpoint path/hash and inference example logs.
- Failure report: errors by L1–L5 and example IDs; raw data IDs may require redistribution review.

## Stop rules
If only cue detection is learned with an almost perfect lexical baseline, acknowledge low task novelty; strengthen gold negative controls or revise scope, never secretly redefine test after seeing failures. If rare categories lack support, mark `NOT_EVALUABLE` instead of declaring F1=1.00 or hiding categories.
