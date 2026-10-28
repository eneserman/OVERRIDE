# v0.7 build / research-data verification

**Verdict: ENGINEERING READY, ACADEMIC GOLD BLOCKED.**

## Actual execution

- `python -m unittest discover -s tests -q`: **48 tests PASS**.
- `python scripts/build_synthetic_bootstrap.py --out data/synthetic_bootstrap`: SUCCESS.
- `python scripts/audit_research_dataset.py --out reports/V07_DATASET_AUDIT.json`: `structural_pass=true`, `academic_gold_ready=false`.
- `python scripts/build_ai_review_triage.py ...`: SUCCESS.
- `python scripts/mine_sgd_revision_candidates.py ...` on complete official SGD: **NOT RUN**, official raw files unavailable here.
- Model training or true test metrics: **NOT RUN**.

## Generated examples and exact span support

| Partition | Records | CANCEL_CUE | KEEP_CUE | KEPT_VALUE | NEW_VALUE | OLD_VALUE | REFERENCE | RESTORE_CUE | UPDATE_CUE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train | 504 | 72 | 108 | 72 | 324 | 36 | 72 | 72 | 216 |
| dev | 126 | 18 | 27 | 18 | 81 | 9 | 18 | 18 | 54 |
| challenge | 126 | 18 | 27 | 18 | 81 | 9 | 18 | 18 | 54 |

100 source SGD-derived examples, **0 human gold**. Two AI drafts of the same 100 examples; 18 examples have at least one difference; not human IAA.

## Known blockers

- No independently human-adjudicated SGD gold dataset exists yet.
- Synthetic challenge set is only a rule/template held-out regression suite; it is NOT the final unbiased academic evaluation.
- A/B AI suggestions are from one model family; they do NOT constitute inter-annotator agreement.
- All synthetic examples must be labeled synthetic in training statistics; do not claim them as SGD or native annotations.
- Real SGD source files were not independently downloaded during this build; verify full source SHA-256 locally.
- A complete production model training and real-data external validation is not included in this dataset pack.

## Source/license

Original SGD: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue (CC BY-SA 4.0).

No claims of excellent grades, perfect labels, full model convergence, or independent validation.
