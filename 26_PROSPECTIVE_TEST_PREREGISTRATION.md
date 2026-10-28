# 26 — Prospective frozen test preregistration (written before gold scoring)

**Research plan locked on 2026-10-28, not a completed frozen gold test.** Freeze *raw candidate pool membership* BEFORE inspecting model results. An immutable list of texts alone is NOT a gold test; later independent annotation and strict governance are required.

## 1. Primary vs external
- `real_sgd_heldout`: main in-domain unseen conversations from a **separately downloaded official SGD dev/test split**, excluding any dialogue family or hashed text in pilot/AI suggestions/train. Source choice must be recorded in manifest. The 100 previously AI-reviewed SGD train examples are ineligible.
- `frames_cross_corpus` (conditional): genuine Microsoft Frames user turns, especially reference/tag-rich situations, disjoint from any training or inspection. No Frames raw files are present today and license portal needs human review.
- `synthetic_challenge`: *engineering regression only*, never primary academic evaluation.

## 2. Prospective lock protocol
1. Pin source release and verify hashes; prepare raw candidate JSONL with unique `example_id` or `id`, source (`dataset`,`split`,`dialogue_id`,`turn_index`), `current_user_utterance`, past-only history.
2. Run `scripts/lock_prospective_holdout.py --pool ... --seen ... --out ... --seed 20261028`. The script verifies no prior pilot records/families, fingerprints every row, and writes a **no-label manifest** containing all pool ids and file/content hash. Treat exported pool as sealed and save a copy in private storage.
3. Freeze `protocol_version`, selection rules, sample targets, class reporting and metrics. Annotation-team access to source dialogue text is necessary but model developers **must not** inspect locked labels or model outputs.
4. Two bona-fide independent reviewers plus adjudication; immutable originals, disagreements and agreement spot audit. If blind human annotation is impossible, identify real evaluation as `not_available`, not `heldout_gold`.
5. Once gold exists, use existing `freeze_gold_splits.py` or a dedicated test-only gold export validated against **same locked candidate fingerprints**, ensuring no test rows get swept into new train/dev. Gold file hash and predeclared evaluation must be archived.
6. Run a single documented evaluation, with errors locked; for improvements use dev only and reserve any confirmatory secondary test for a pre-registered one-time run.

## 3. Support/coverage gates
Target *at planning time*, subject to real pilot: at least 30 examples/class on main test where feasible, representative L1-L5 and hard negatives, positive/negative counts disclosed; if unsupported, explicitly report N/A and narrow scope, never invent samples. Distinct dialogue-family/source splits mandatory. Numeric thresholds are feasibility objectives, not powers/statistical guarantees.

## 4. Statistical reporting
Strict character-span match after tokenizer alignment; per-label P/R/F1 and micro/macro of VALUE/CUE heads. Cue polarity and operation precision measured separately if adjudicated. Randomization/permutation or paired bootstrap **by dialogue family**, NOT by token, for context gain confidence intervals; 3 seeds if feasible, median and range reported. Data contamination and duplicate utterance checks mandatory.

## 5. Fail-closed rules
- Do not call human-reviewed or model-generated examples 'gold' without credible documented review evidence.
- A SHA256 lock is a **tamper-evident record**, not statistical independence.
- `SGD test` official slot state labels are **not** gold correction spans.
- Do not report an external benchmark JGA as OVERRIDE F1.
- Never revise test membership to improve final model score after reveal.
