# Data card — OVERRIDE v0.7

## Purpose
An **auditable research bootstrap package**, not a completed academic gold dataset. Provides (1) provenance-preserved SGD pilot inputs and clearly labeled AI suggestions, (2) deterministic compositionally labeled synthetic examples that exercise all eight span tags, and (3) tools to mine and independently human-review real SGD dialogues.

## Included dataset (verified by generator + tests)

| Source | Count | Status | Use |
|---|---:|---|---|
| `data/sgd_pilot/annotator_A_UNLABELED.jsonl` | 100 | Real SGD-derived pilot, not yet human labeled | Human review input |
| `data/sgd_pilot/annotator_B_UNLABELED.jsonl` | 100 *same records* | Same pilot examples, not additional independent data | Second human review input |
| `data/ai_suggestions/annotator_A_AI_DRAFT.jsonl` | 100 | One-model AI proposals | Triage only |
| `data/ai_suggestions/annotator_B_AI_DRAFT.jsonl` | 100 | Another prompt policy, same model family | Triage only |
| `data/synthetic_bootstrap/synthetic_train.jsonl` | **504** | Generated, exact programmatic span offsets | Warm-start training |
| `data/synthetic_bootstrap/synthetic_dev.jsonl` | **126** | Generated, different template families | Engineering validation |
| `data/synthetic_bootstrap/synthetic_challenge.jsonl` | **126** | Generated, separate template families | Synthetic regression only |
| `data/gold/` | **0** | No actual human-adjudicated gold | Cannot claim real measured generalization |

`generation_manifest.json` provides actual per-file SHA256 and per-label span counts. All eight labels occur in each synthetic split. The same entity values, generator, broad domain and task rules appear across partitions; don't describe the challenge subset as out-of-domain or external validation. Train includes 3 controlled phrase variants per recipe; dev/challenge use held-out phrasing. Repeated narrow templates can cause severe overfitting despite perfect offsets.

## Verified in this environment
- Existing v0.6 test suite plus new v0.7 tests pass (see `reports/V07_BUILD_VERIFICATION.md`).
- Synthetic data generation is deterministic (fixed seed 20261028), structurally valid and hash-checked.
- Historical references point only backward; `CANCEL_CUE` under negation does not produce cancellation operations.
- Real SGD pilot AI suggestion offsets are verified and marked `AI_DRAFT`, not human-verified.
- No full official SGD raw dataset was acquired here. The source hash cannot be asserted.

## Known limitations
- Real-world semantic correctness of generator rules needs human critique; generated data is formulaic, narrow-domain, and not independently gold-labeled.
- Current 100 SGD examples lack confirmed human gold for OLD_VALUE, KEPT_VALUE and other rare classes.
- Two AI strategies from one model are correlated. Their overlap does not measure inter-annotator reliability.
- The SGD source includes older task-oriented dialogue language, not a modern LLM-instruction corpus. Broader LLM instruction revision generalization is a **hypothesis**, not demonstrated.
- Ambiguous history references and apparently similar date values must be adjudicated; never force a numeric score.

## Intended audience and responsible use
Student NLP researchers who can honestly document weak supervision, synthetic augmentation, independent human annotation, and strict held-out real-data evaluation. **Not** an annotation-free shortcut to claiming a high-grade or academically verified corpus.

## Sources
SGD Dataset & license: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue — CC BY-SA 4.0. Original dataset paper: Rastogi et al. (2020), *Towards Scalable Multi-Domain Conversational Agents: The Schema-Guided Dialogue Dataset*, AAAI 2020.
