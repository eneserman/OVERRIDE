# OVERRIDE — Technical Design Audit

**Date:** 2026-10-27 | **Audit status:** CONDITIONAL — DO NOT START FULL MODEL TRAINING

## Files actually available during the audit

- `02_NLP_TASK_DESIGN.md` was the **only existing project MD** when the audit began.
- The conversation's earlier conceptual step(s) were **not** corresponding completed MD artifacts.
- This audit adds `01_REQUIREMENTS.md` and revises `02_NLP_TASK_DESIGN.md`.
- At the time of this audit, `03_DATASET_PIPELINE.md`, implementation, trained model, benchmark and PPTX were **not** created. A subsequent phase created `03_DATASET_PIPELINE.md` and a **read-only corpus audit script**; no trained model, real SGD audit or PPTX exists yet.

## Source cross-checks

- Google SGD repository README and task schema confirm utterances, per-service frames, user-turn states and non-categorical slot offsets; these are **NOT equivalent** to gold `UPDATE_CUE`, `KEEP_CUE`, `RESTORE_CUE` annotations.
- Source license declared `CC BY-SA 4.0` for SGD/SGD-X, with attribution/share-alike duties.
- The academic Project 1 rubric is for **text classification** and must not be silently applied to Project 2 token classification.
- Group collision rules described in announcements and user clarification imply a strict no-collision policy.

## Issues found and mitigations

| ID | Severity | Finding | Correction |
|---|---|---|---|
| F01 | CRITICAL | No actual gold corpus for proposed novel correction/restore cues | New `G1/G2` feasibility gate, human-reviewed labels and no full-training authorization without pilot |
| F02 | HIGH | State difference can be mistaken for an explicit correction | Pseudo-labels/candidates kept separate; equality/alias/service-switch checks; human adjudication |
| F03 | HIGH | Very rare RESTORE/KEEP/REFERENCE classes can make macro-F1 misleading | Class-level frequency gates, diagnostic-only rare categories, confidence intervals when possible |
| F04 | HIGH | No explicit method for comparing rule baseline vs Transformer without gold future/current states | Separate observable vs oracle input contracts and fair context budgets |
| F05 | HIGH | `Don't cancel` negative command potentially flips intended action | Add cue polarity, negation scope and cancellation target to structured labels/tests |
| F06 | HIGH | Dialogue state, token labels, and history links conflated in demos | Distinct outputs, losses, metrics, unresolved/abstention handling |
| F07 | MEDIUM | Draft serialized example lacked numeric offsets | Add half-open offsets and exact-slice assertions to sample |
| F08 | HIGH | P1 numerical rubric presented elsewhere as if P2 guaranteed | New `01_REQUIREMENTS.md` with separate confirmed P2 versus P1 precedent |
| F09 | HIGH | Duplicate topic/dataset would risk a zero | Mandatory up-to-date P2 sheet check and if necessary written instructor approval |
| F10 | MEDIUM | Full-history context may be truncated unpredictably | Bounded context policy, current-turn loss mask and history truncation reporting |
| F11 | HIGH | Annotation test split could be leaked or hand-picked | Dialogue-grouped custom split, frozen before training, no model-driven editing of test labels |
| F12 | MEDIUM | Licensing and redistributable data under public GitHub can be mishandled | Upstream attribution, license inventory, separate code/data licensing and transformation provenance |

## Stop/go decision

**GO:** source dataset inspection, candidate mining, annotation guideline and pilot preparation.

**NO-GO:** treating the two BIO heads as a finalized gold standard; promising 400–600 reliable examples; reporting any benchmark result; deploying demo as if trained; beginning full training without pilot class coverage.

## Next agent instructions

1. Read `01_REQUIREMENTS.md` and `02_NLP_TASK_DESIGN.md` together.
2. Implement only a read-only SGD corpus audit first: schema stats, per-service state diffs, candidate count by revision type, unique dialogues, offsets and distribution. Save machine-readable reports.
3. Read the new `03_DATASET_PIPELINE.md` now; revise it with **measured** corpus findings after the real audit. Draft final annotation guidelines **after** inspecting examples, never from invented empirical numbers.
4. Bring class counts and ambiguous examples for human review before freezing token labels.

## Official sources

- https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
- https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/dstc8.md
- https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/LICENSE.txt

## Follow-up delivery decision (2026-10-27)

The project owner clarified the assessed implementation is **Python code**, not a website. Any previous suggestions to build Streamlit or a frontend were optional demonstration ideas, not course requirements. The official implementation target is CLI preprocessing/training/evaluation/inference + GitHub repo + PPTX. `03_DATASET_PIPELINE.md` and `scripts/audit_sgd.py` were subsequently authored; the script passed synthetic fixture unit tests, **not a real corpus validation**.
