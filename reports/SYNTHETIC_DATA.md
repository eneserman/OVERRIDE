# Synthetic training data experiment (protocol, written before the training run)

**Status:** FINAL. Protocol committed before the CV run (`bc99727`); results in §5. Human check of 50 records open.

## 1. What and why

Can AI-written training turns help a model trained on 857 human-labeled turns? The course allows AI use; the data is
**declared**: every synthetic record carries `annotation.status = SYNTHETIC_AI`, lives only in `data/synthetic/`, and
is never mixed into the human gold or the test.

## 2. How the data was made

1. **Real contexts** (`scripts/synth_contexts.py`, seed 20261031): 240 points in official-train SGD dialogues where the
   system has just confirmed or offered concrete values, spread over 26 services (at most 10 each). Dialogues of the
   released gold and of the locked test are excluded. Histories are real SGD text.
2. **AI-written next user turn** (`data/synthetic/authored_00{1,2,3}.jsonl`, author: Claude Opus 5.5): for each context
   one new user turn, written for that context (never copied from SGD), with spans labeled by the written guideline
   (`docs/ANNOTATION_GUIDELINES.md` v0.2.3: leading prepositions outside, determiners inside, `for N` split, no
   REFERENCE on bare pronouns, no UPDATE_CUE without an explicit cue word, question targets unlabeled).
   Mix by design: revisions with an explicit cue, references to earlier options, value-only turns, and **45 hard
   negatives** with no span ("No thanks, I'm good for now.", "Never mind, I don't want to go anymore.", "Back to the
   movie search, please.") aimed at the spurious-cue errors found in `ERROR_ANALYSIS_CV.md`.
3. **Build and checks** (`scripts/build_synthetic.py`): offsets computed by code; fail-closed on missing or ambiguous
   span text, same-layer overlap, duplicates, copies of any real SGD turn in our gold, and near-duplicates (token
   Jaccard ≥ 0.8).

## 3. Against the "AI pattern" problem

`reports/synthetic_quality.json` (240 records):

| Check | Synthetic | Human gold, same size |
|---|---|---|
| distinct-1 (unique words / words) | 0.246 | 0.177 |
| distinct-2 (unique word pairs / pairs) | 0.712 | 0.549 |
| most frequent opening (first two words) | "is there", 5.4% of turns | — |
| near-duplicates (Jaccard ≥ 0.8) | 0 | — |
| copies of real SGD turns | 0 | — |

19 different cue phrases are used; the most frequent ("instead") covers 17 of 76 cue spans. Lexical diversity is not
lower than the human data. What these numbers cannot show is whether the turns are *natural* and the labels *right*:
that is the human check below.

**Human check (open):** reviewers A and B each judge a fixed random sample of 50 synthetic records
(`data/synthetic/HUMAN_CHECK_50.md`): natural yes/no, labels correct yes/no. The rates are reported here when done.

## 4. Experiment (fixed before running)

- Configuration: the selected one — `microsoft/deberta-v3-base`, history = no, plain loss, 10 epochs, same folds,
  salt and seeds as `D5V2_PROTOCOL.md` (`scripts/d5v2_cv.py --extra-train data/synthetic/synthetic_v1.jsonl`).
- The 240 synthetic records are added to **every training fold** and are **never scored**; scoring is on the same 857
  human records, pooled out-of-fold.
- Primary comparison: S at **epoch 6** (the E* fixed by the original selection) against the original run, with the
  family bootstrap (`scripts/d5v2_bootstrap.py`, 1000 resamples). Best-epoch S is reported as secondary.
- Caveat stated in advance: the two runs differ only by the added data, but GPU training is not bit-deterministic and
  batch order changes, so small differences (|ΔS| < 0.01) are within run-to-run noise.
- **No test access.** The frozen model and every reported test number stay as they are.

## 5. Results

Pooled out-of-fold scores on the same 857 human records (`reports/train_runs/d5v2_cv/*/cv_result.json`, local):

| Training data | VALUE F1 | CUE F1 | **S (epoch 6)** | best epoch, S |
|---|---|---|---|---|
| 857 human (original selection run) | 0.891 | 0.830 | **0.860** | 6, 0.860 |
| 857 human + 240 synthetic | 0.888 | 0.827 | **0.858** | 5, 0.858 |

**Primary comparison:** ΔS = **−0.003**, 95% family-bootstrap interval **[−0.018, +0.014]**, synthetic better in 41% of
resamples (`reports/SYNTHETIC_BOOTSTRAP.json`). Within the run-to-run noise stated in §4: **no measurable effect**.

Per label (epoch 6): NEW_VALUE 0.905 → 0.899, REFERENCE 0.846 → 0.859, UPDATE_CUE 0.848 → 0.844. The 45 hard
negatives did not reduce spurious cues (false cue spans 39 → 45).

**Reading.** 240 AI-written turns (+28% training records) neither helped nor hurt. The model is not short of this kind
of easy, clean example; its remaining errors are the hard, context-dependent ones (`ERROR_ANALYSIS_CV.md`), which
written-to-order examples do not reproduce. The frozen model stays as it is; the synthetic set is released as a
declared resource with its quality report.
