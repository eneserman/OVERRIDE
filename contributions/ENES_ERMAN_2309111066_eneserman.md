# Enes Erman — 2309111066 — GitHub: eneserman

**Role:** project owner, annotator B (`reviewer_B_ENES`), coordination of the research protocol.

## Data and annotation

- Annotated as reviewer B in every round, blind to reviewer A: calibration and pilot sets, the 457-turn first gold
  (double sets and his single-annotated share), the locked 363-turn test, the 400-turn second batch (80 shared + 160
  solo) and the cross round (160 turns first labeled by reviewer A).
- With reviewer A, took every joint adjudication decision: the test disposition (DEV-001), the guideline rules added in
  v0.2.3 (C1-r boundaries, C4 question targets, C6 "same day", G3 bare pronouns), the round-1 and round-2 decision
  sheets, the "make it" rule (DP-5 / R11) and the 16 joint cross-round cases.
- Took part in the blind audit of the first single-annotated batch, which found agreement 0.458 and led to gold v1.1.

## Research decisions

- Approved each pre-registered protocol before it was run (gold audit, second batch and its amendments E1–E4, D5-v2).
- Decided the claim scope (SCOPE-001, taxonomy option A, KEPT_VALUE out of scope) before the test was opened.
- Approved the single test access after the model freeze was committed.

## Engineering

- Owner of this repository; ran the training and evaluation on his machine (RTX 4060).
- Built the pipeline, CV, final-ensemble, evaluation and analysis scripts with an AI coding assistant (Claude Code),
  reviewing and approving each step; commits carry a `Co-Authored-By` line. AI use is declared in the README.

## Where to see it in git

Commits by `eneserman`, in particular the protocol commits (`reports/*PROTOCOL*.md`), the gold builders
(`scripts/build_gold_v1_*.py`), `scripts/d5v2_*.py`, the freeze `2702a45`, the test access `eefdb91` and D6 `4c096d4`.
