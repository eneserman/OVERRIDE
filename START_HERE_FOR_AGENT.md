# START HERE — OVERRIDE Full Handoff

**Send the entire ZIP to your coding agent; then paste the text of `AGENT_MASTER_PROMPT.md`.** The archive contains preparatory documents and code, **not** real SGD results or a completed machine learning model.

**v0.6 audit:** Read `17_V06_HARDENING_AUDIT.md`. Run `python scripts/preflight_handoff.py` before D0. A PASS only certifies handoff files and synthetic tests.

## Mission summary
- Group: **Developers**, NLP Project 2.
- Product type: **Python command-line academic research project**, **not a website**.
- Main task: two-head, context-aware token classification of revision *values* and *cues*; secondary tasks are state transitions/reference links, scored separately.
- Input data: official Google SGD (must be downloaded and pinned by coding agent), with original correction labels NOT available by default.
- Research outcome sought: evidence that conversation context helps exact-span detection over last-turn-only model. This is a hypothesis to test, **not an established result**.

## Strict implementation order
1. **D0 only, immediately:** execute `AGENT_D0_DATA_AUDIT_PROMPT.md` on real official source; report facts and stop.
2. D1–D2 blind queues, **then independent actual human reviewers** and adjudication.
3. Gold validation and dialogue-group split freeze.
4. Rule / CRF / Transformer models after sufficient real gold.
5. Frozen test, error analysis, measured figures.
6. Public GitHub repository and PPTX based only on measured results.

**NEVER:** invent dataset counts, label approvals, model scores, human reviewer work, git commit diffs, dataset licenses, or web demos. Do not skip gate just because scripts/prompts for later phases already exist.

## Existing tools
`audit_sgd.py`, `prepare_annotation_pilot.py`, `normalize_review_packet.py`, `annotation_agreement.py`, `validate_annotations.py`, `freeze_gold_splits.py`, `evaluate_spans.py` are initial CLI code and tested with **synthetic cases**, not full SGD. Check `README.md` for commands.

## What requires owner/real-world input
- Up-to-date P2 group collision check and any new P2 grading rules.
- Access to real SGD source and optional compute resources.
- Two independent human annotations; student group names/IDs/GitHub usernames and actual work records.
- Decision whether training classes with low real support must be narrowed.
- Repository license approval, legal review of raw/clean data republication, final public push.

**Current gate:** `G1 real source audit pending`. Final grade and novelty cannot be guaranteed from prepared paperwork.
