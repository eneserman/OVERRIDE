# Error analysis — selected D5-v2 configuration (development side, out-of-fold CV)

Source: pooled out-of-fold predictions of DeBERTa-v3-base, history = no, loss = plain, epoch 6, on all 857 train-side
records (`reports/train_runs/d5v2_cv/deberta-v3-base__no__plain/oof_epoch6.jsonl`). Computed with
`scripts/error_analysis.py`; full counts and examples in `ERROR_ANALYSIS_CV.json`. **No test data is used.**

Error classes: *boundary* (same label, offsets differ), *label* (same offsets, other label), *overlap* (other label and
offsets), *missed* (no overlapping prediction), *spurious* (prediction overlapping no gold span).

| Label | Gold | Exact | Boundary | Label | Overlap | Missed | Spurious |
|---|---|---|---|---|---|---|---|
| NEW_VALUE | 764 | 705 | 29 | 0 | 2 | 28 | 48 |
| REFERENCE | 189 | 162 | 9 | 2 | 2 | 14 | 18 |
| UPDATE_CUE | 226 | 195 | 8 | 0 | 0 | 23 | 27 |
| CANCEL_CUE | 7 | 0 | 0 | 3 | 1 | 3 | 0 |
| rare others (KEPT, OLD, KEEP, RESTORE) | 9 | 0 | 0 | 3 | 1 | 5 | 0 |

## What the errors say

1. **Spurious values in turns that do not change anything (largest class for NEW_VALUE).** Refusals and chit-chat
   ("Not now. What is your opinion on going by bus?", "Teen Spirit is perfect, I'll keep that in mind") contain
   value-like phrases that the guideline leaves unlabeled (DP-1, C2/C4 question targets). The model labels the surface
   form; deciding that the turn makes no request needs discourse understanding.
2. **Determiner boundaries.** "the 13th of March" (gold, C1-r: determiners inside) is predicted as "the" + "13th of
   March", or the other way round. These are near-misses that strict exact-span scoring counts as one miss and one
   false positive.
3. **REFERENCE vs NEW_VALUE for names mentioned earlier.** "Dogman is actually awesome", "I want to see Shazam then":
   gold is REFERENCE because the system had offered these options before; the model, which sees no history, calls them
   NEW_VALUE. This is exactly where dialogue history should help, but it is a small share of all errors, which fits the
   null result of the history hypothesis.
4. **"Never mind" is read as UPDATE_CUE.** With 7 CANCEL_CUE spans against 226 UPDATE_CUE spans, "Never mind, make it
   for 12:30" is absorbed by the frequent class. Rare cue labels need targeted data, not a different loss (the
   weighted loss lowered S in every setting).
5. **Cue span length.** "I have changed my mind" vs "changed my mind", "a change of plan" vs "change": multi-word cues
   with variable extent are a boundary problem as much as a detection problem.
