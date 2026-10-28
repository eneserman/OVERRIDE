# Phase 04 — Local Verification (Synthetic Test Fixtures)

**Date:** 2026-10-27  
**Scope:** Scripts and annotation protocol for D1–D2, **not** a real SGD analysis.

## Implemented

- Added `scripts/prepare_annotation_pilot.py` for official **train** split only, seeded round-robin strata, max one selected example per dialogue, context history and blind annotator packets.
- Added `tests/test_prepare_annotation_pilot.py`, covering CLI output, negated cancellation case, deterministic sample, gold-state not leaked and no future-turn leakage.
- Retained `scripts/audit_sgd.py` and its three pre-existing synthetic tests.
- Added `04_HUMAN_ANNOTATION_PILOT.md` and `AGENT_D1_D2_PILOT_PROMPT.md`.
- Updated `03_DATASET_PIPELINE.md` to distinguish implemented local code from unrun real-corpus stages.

## Local execution results

Command:

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py tests/*.py
```

**Observed:** eight tests passed (`OK`), and Python compilation completed without errors in this container. Fixture dialogues are **synthetic only**. A subprocess integration test verified that A/B packets are equal and don't contain `state_change_candidates` or `slot_values`.

## Blockers remaining

- Official SGD train files were not available for processing. A download attempt in this environment failed. No source commit hash, real class proportions, real candidate samples, independent human annotations or benchmark results are reported.
- D0 full-corpus audit and D1–D2 real-corpus execution must happen in an environment that can access official dataset files.
- Two independent human reviews and adjudication must occur before training. Do not infer class correctness from heuristics or passing software tests.
- Final dataset-license redistribution, P2 collision check and group-contribution records remain unresolved.

**Gate status:** Local code/test readiness PASS. Real-data sampling readiness PENDING DATA. Gold/training readiness NOT READY.
