> **OVERRIDE v0.7 DATA UPDATE:** For accurate current status read `18_V07_RESEARCH_PROTOCOL.md`, `19_DATASET_CARD_V07.md`, `20_GOLD_RELEASE_GATES.md`, `21_GOLD_READINESS_TR.md`, and `AGENT_D3_V07_REAL_GOLD_MASTER_PROMPT.md` **before** following the older v0.6 development handoff. In v0.7: 504 synthetic train + 126 synthetic dev + 126 synthetic challenge; 100 SGD pilot examples; 2 sets of 100 AI draft suggestions; **0 human-adjudicated gold**. No actual model training results. All synthetic/AI outputs must be disclosed. Academic gold release is BLOCKED pending real human review.

# OVERRIDE — Developers | NLP Project 2

**Status: full design + pre-gold Python tooling prepared. D0 real SGD train audit EXECUTED (2026-10-28, commit `e852981a`, 16,142 dialogues, all offsets valid). Not trained. No human-adjudicated custom labels, model metrics, or PPTX yet.** Repo: https://github.com/eneserman/OVERRIDE

**Delivery:** Python command-line research repository, public GitHub and PowerPoint presentation. **No website or mobile app is required.**

**v0.6 safety fixes:** read `17_V06_HARDENING_AUDIT.md` before running the agent. Frozen test evaluation must use `scripts/evaluate_frozen_test.py` with the full adjudicated gold file, manifest and test-only predictions. Avoid direct test claims from unconstrained `evaluate_spans.py`.

**Handoff navigation:** start with `START_HERE_FOR_AGENT.md`; the coding agent receives `AGENT_MASTER_PROMPT.md`.

## One-sentence research question
Do context-aware token classifiers detect the exact phrases expressing revisions, cancellations, retained information and historical references in multi-turn conversations more reliably than last-turn-only classifiers?

## Primary vs secondary tasks
- **Primary / assessed focus:** two provisional token classification layers — VALUE (`NEW_VALUE`, `OLD_VALUE`, `KEPT_VALUE`, `REFERENCE`) and CUE (`UPDATE_CUE`, `CANCEL_CUE`, `KEEP_CUE`, `RESTORE_CUE`). Strict exact-span F1 on validated current-user-text spans.
- **Secondary / separately evaluated:** reference resolution and state transitions (`ADD`, `UPDATE`, `DELETE`, `KEEP`, `RESTORE`, `CANCEL_INTENT`, `UNRESOLVED`). **Do not** pretend SGD already provides gold revision labels or that the resolver is implemented.
- Complexity levels L1–L5 from simple correction to multi-turn restore/keep; rare L4/L5 cases remain exploratory until enough gold exists.

## Data, provenance and license
Upstream: [Google Schema-Guided Dialogue (SGD)](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue), license **CC BY-SA 4.0**. SGD provides conversations, frames, `slot_values`, and some character-level slot spans. OVERRIDE's correction/keep/restore cue annotations are **new intended labels, not supplied by SGD**. Source must be pinned to a commit, audited and cited; sharing adaptations must respect license conditions. **Project code is MIT-licensed (see `LICENSE`); this does not extend to the SGD data.**

## Quick start (Python 3.10+)

```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
python scripts/preflight_handoff.py

# Clone official source when network is available and document exact commit.
git clone https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd
git -C data/upstream/sgd rev-parse HEAD
python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit

# Only after real audit approval, prepare blind annotator packets:
python scripts/prepare_annotation_pilot.py --sgd-root data/upstream/sgd --out data/annotations/pilot_v0.1 --sample-size 100 --seed 42 --context-turns 8
```

The following tools exist **now**, but require genuine adjudicated gold for legitimate final use:

```bash
python scripts/validate_annotations.py --input examples/UNREVIEWED_annotation_example.jsonl
# After independent human reviews and adjudication:
python scripts/validate_annotations.py --input data/gold/override_gold_v0.1.jsonl --require-gold
python scripts/freeze_gold_splits.py --gold data/gold/override_gold_v0.1.jsonl --out reports/splits/frozen_v0.1.json --seed 42
# After real model predictions over a fixed held-out gold subset:
python scripts/evaluate_frozen_test.py --full-gold data/gold/override_gold_v0.1.jsonl --manifest reports/splits/frozen_v0.1.json --test-predictions <test_only_predictions.jsonl> --out <frozen_test_metrics.json>
```

**Synthetic validation passes do not prove scientific quality.** The included `examples/` file is invented solely to test schema, carries `SYNTHETIC_NOT_SGD`, and must never appear in training/evaluation.

## Directory guide

| Path | Purpose | Availability |
|---|---|---|
| `00_DESIGN_AUDIT.md`–`04_HUMAN_ANNOTATION_PILOT.md` | Requirements, token task, SGD audit and human annotation design | Written and reviewed as drafts |
| `05_SYSTEM_ARCHITECTURE.md`–`16_ARTIFACT_STATUS.md` | Architecture, experiments, evaluation, QA, release, storyboard, risk, contracts and status | Written as future implementation specs |
| `AGENT_MASTER_PROMPT.md`, `AGENT_D*.md` | Controlled phase-by-phase engineering handoff | Ready to give to coding agent |
| `scripts/audit_sgd.py` | Read-only source audit, state-change **candidates**, not gold | Implemented, synthetic tests |
| `scripts/prepare_annotation_pilot.py` | Blind A/B candidate packets + private hints | Implemented, synthetic tests |
| `scripts/normalize_review_packet.py`, `scripts/annotation_agreement.py` | Convert genuine reviewed blind packets to non-gold canonical reviewer format; report disagreements | Implemented, synthetic tests |
| `scripts/validate_annotations.py` | Offset, label, overlap, provenance/status checks | Implemented, synthetic tests |
| `scripts/annotation_entry_helper.py` | Interactive human data entry (typed phrase → verified offsets); generates no labels | Implemented, synthetic tests |
| `scripts/freeze_gold_splits.py` | Deterministic dialogue-family split manifest | Implemented, synthetic tests |
| `scripts/evaluate_spans.py` | Strict span scoring for exploratory/dev use | Implemented, synthetic tests |
| `scripts/evaluate_frozen_test.py` | Checks frozen gold and test partition before final scoring | Implemented, synthetic tests |
| `scripts/preflight_handoff.py` | Verifies local handoff completeness and syntax/tests | Implemented, synthetic tests |
| `tests/` | Unit/integration fixture tests | Tested locally; not official SGD results |
| `configs/experiment.example.json` | Future model run configuration template | **Template only** |
| `examples/UNREVIEWED_annotation_example.jsonl` | Artificial offset demonstration | **Not gold** |
| `contributions/CONTRIBUTION_TEMPLATE.md` | Real team members fill their own Git evidence | Template only |
| `reports/` | Verified reports after actual runs; old synthetic verification marked | Partial |
| `src/override/` | Future ML/data/model code | **Not implemented** |
| `data/upstream/`, `data/annotations/`, `data/gold/` | Real data and human reviewer outputs | **Not included in this handoff** |

## Next action and strict gate
Hand the **entire ZIP** to the coding agent and paste `AGENT_MASTER_PROMPT.md`. Agent runs D0 only, returns real data/hashes/counts and GO/NARROW/NO-GO. Then humans review D1–D3, and only after frozen gold is model training allowed. Do not skip gates because documents for later phases already exist.

## Academic and honesty checklist
The official P2 material emphasizes token classification, difficult/novel datasets/tasks, technical depth and P2 sheet collision avoidance. The explicit numerical rubric received earlier is from **Project 1**, so its percentages/timing are **not automatically P2 rules**. Submission asks for GitHub URL then PPTX. Public repo must be clean, licensed, documented and contain real team contribution histories. **Never fabricate metrics, gold labels or human reviews.**

## CI caveat
`.github/workflows/python-tests.yml` tests only the Python contract on synthetic cases. A green CI badge is **not evidence of official SGD evaluation or model quality**.


## 2026-10-28 v0.8 real-corpus research upgrade

See `24_EXTERNAL_DATASET_RESEARCH.md` through `29_NEXT_ACTIONS_TR.md`. Added source research, prospective real-test raw lock and independent input-hash checks, Microsoft Frames candidate extractor, upstream SGD commit/hash verifier, actually trained classical synthetic BIO baseline and measurements. **Synthetic challenge F1 is NOT real OVERRIDE F1, and real gold still does not exist.** Read `28_V08_EVIDENCE_AUDIT.md` before proceeding.
