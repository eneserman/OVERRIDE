# OVERRIDE v0.7 — Data engineering + evidence handoff

## Quick start (Python 3.10+; no third-party dependency required for these tools)

```bash
python -m unittest discover -s tests -v
python scripts/build_synthetic_bootstrap.py --out data/synthetic_bootstrap --seed 20261028
python scripts/build_ai_review_triage.py --a data/ai_suggestions/annotator_A_AI_DRAFT.jsonl --b data/ai_suggestions/annotator_B_AI_DRAFT.jsonl --out data/review
python scripts/audit_research_dataset.py --project-root . --out reports/V07_DATASET_AUDIT.json
```

**Intentional non-passing gold gate** (exit code 2 until humans annotate and gold evidence is independently reviewed):

```bash
python scripts/audit_research_dataset.py --project-root . --require-academic-gold
```

## Official SGD mining (not executed here, source download unavailable)

```bash
# Populate official files under data/upstream/sgd/train/dialogues_*.json yourself.
python scripts/mine_sgd_revision_candidates.py --sgd-root data/upstream/sgd --split train --out data/annotations/sgd_candidates_v07 --per-bucket 50 --seed 42
```

Use the generated `reviewer_A_BLIND.jsonl` and `reviewer_B_BLIND.jsonl` for genuine independent human review. **Keep `PRIVATE_mining_manifest.jsonl` private.** This miner finds candidates based on cues and source context; it does not label, prove class membership, or guarantee 50 from each bucket. Rows contain previous turns only; no future conversation.

## New files
- `scripts/build_synthetic_bootstrap.py`: deterministic synthetic generator (14 semantic recipe types, 3 varied train phrasings, disjoint dev/challenge templates).
- `scripts/audit_research_dataset.py`: checks synthetic hashes, span offsets, no source reclassification and pilot AI provenance.
- `scripts/build_ai_review_triage.py`: creates a review queue for 100 real SGD-derived *unadjudicated* examples.
- `scripts/mine_sgd_revision_candidates.py`: real official SGD candidate miner, if available locally.
- `tests/test_v07_dataset_pipeline.py`: regression tests that stop mislabeled/negated transitions and invalid offsets.
- `18`–`23` docs: research/quality gates, protocol, data card, reviewer guide, agent prompt.

## STOP signs
No claim of human gold, true independent inter-annotator agreement or real held-out F1 is possible yet. Pretrained-model training/evaluation remains an additional coding phase after evidence. No professor-approved final dataset is implied.
