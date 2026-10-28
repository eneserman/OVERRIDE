# OVERRIDE — AI Coding Agent Prompt D1–D2: Real-Corpus Pilot Preparation

**Read first:** `00_DESIGN_AUDIT.md` → `01_REQUIREMENTS.md` → `02_NLP_TASK_DESIGN.md` → `03_DATASET_PIPELINE.md` → `04_HUMAN_ANNOTATION_PILOT.md`.

## Role and outcome

Act as a disciplined NLP Data Engineer for the **Developers** group. Project deliverable is **Python CLI source, reproducible data pipeline, public GitHub documentation and PPTX**, not a website/mobile app. Do not begin Transformer/CRF training or announce gold dataset accuracy in this task.

## Execute in order

1. Confirm original SGD under `data/upstream/sgd` originates from official Google repository; pin commit and SHA-256. Leave raw files unchanged. If missing and network access permits, clone official source. If blocked, stop and report the blocker accurately.
2. Run `python -m unittest discover -s tests -v`. Include real terminal output. Fix only demonstrated defects. Existing local synthetic fixtures are not real corpus metrics.
3. Run the full-train audit (not `--limit-files`):

   ```bash
   python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit
   ```

4. Read the audit summary and manually inspect some suspicious cases across changes, aliases, canceled/negated cues, service changes and normal slot filling. Add evidence and limitations to `reports/D0_D1_FACTUAL_FINDINGS.md`.
5. **Only if D0 is sane**, run the following sampling command:

   ```bash
   python scripts/prepare_annotation_pilot.py --sgd-root data/upstream/sgd \
      --out data/annotations/pilot_v0.1 --sample-size 100 --seed 42 --context-turns 8
   ```

6. Verify outputs: `pilot_sampling_summary.json`, `PRIVATE_sampling_manifest.jsonl`, `annotator_A_UNLABELED.jsonl`, `annotator_B_UNLABELED.jsonl`. Confirm samples are reproducible by rerunning to a temporary directory and comparing hashes. Confirm there is **no `state`, `slot_values`, future turn, guessed operation or heuristic label** in annotator packets.
7. Produce `reports/D1_D2_PILOT_PREPARATION.md` with exact source commit, file hashes, counts from executed commands, candidate-stratum counts, sample size, dialogue ID uniqueness, false-positive inspection, dataset/license attribution, hard blockers, and a documented GO/NARROW/NO-GO recommendation for human annotation.
8. STOP. Return reports and sample packets for review. Do **not** mark candidate examples as gold, prefill independent annotations, compute F1 or train a model. Never claim the two annotators have reviewed the files until both have actually done so.

## Non-negotiable constraints

- **Train split only** for current custom annotation mining; do not use official dev/test gold as training supervision for new OVERRIDE labels.
- One selected example per dialogue in pilot to reduce leakage and improve diversity.
- Keep *all* heuristic cues and slot state differences out of annotator A/B packets; private manifest is not gold.
- `RESTORE` cannot be inferred by repeated slot strings alone. `KEEP` requires explicit language for a token span. `CANCEL` must handle negated instruction scope.
- Never tell students that a production-ready model, working browser demo or complete benchmark exists. Only report what was actually executed and observed.
- Respect CC BY-SA 4.0 source obligations. Never push credentials or unsupported downloaded files.
- Do not change task scope, annotate for humans, invent reviews or start full training without owner-approved gate.

## Required response to project owner

A compact execution log, real aggregate counts, pilot stratum breakdown, 5–10 inspected examples (including false positives), **actual** quality flags, test output, pending manual work, and pointers to all generated reports. If source is inaccessible, state STOP with the precise missing prerequisite.
