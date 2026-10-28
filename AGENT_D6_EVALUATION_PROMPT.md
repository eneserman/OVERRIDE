# AGENT D6 — Held-out Metrics, Robustness, Ablation and Error Analysis

Prerequisite: D5 trained, approved model selection via dev, frozen manifest and gold test. No dataset modifications to make metrics look better.

1. Export predictions on frozen held-out gold as `JSONL` exactly matching `14_DATA_CONTRACTS.md`.
2. For **development-only diagnostic** scoring, use `evaluate_spans.py`. For final held-out TEST metrics for each model, use `scripts/evaluate_frozen_test.py` with full adjudicated gold, fixed manifest, and predictions for **test IDs only**. Do not hand-enter F1 numbers.
3. Show VALUE/CUE separate strict span micro/macro/per-class P/R/F1 with denominators. No class support = not evaluable; do not report perfect score.
4. Contrast RULE, CRF, last-turn Transformer and context Transformer under same splits, metrics and test inputs. Track confidence intervals by dialogue family if feasible.
5. Stratify by L1–L5, explicit/implicit updates, negated cancel, unchanged negatives, long-distance references; don't pretend tiny strata are statistically conclusive.
6. If structured reference/transition gold and resolver actually exist, evaluate secondary tasks **separately**, with abstention and wrong-edit rates. Otherwise mark `NOT_IMPLEMENTED/NO_GOLD`.
7. Write `reports/D6_EVALUATION_REPORT.md`, export reproducible plots and anonymized errors with IDs; inspect both model wins and failures.
8. Verify all reported metrics reproducible by rerunning command and comparing hashes. STOP for owner review before presentation/public release.

## Mandatory v0.6 integrity gate

All final TEST metrics must be regenerated through `python scripts/evaluate_frozen_test.py --full-gold data/gold/<actual>.jsonl --manifest reports/splits/<actual>.json --test-predictions <test_only>.jsonl --out <new_report>.json`. Reject altered gold or mismatch with frozen IDs. Report per-class supports and non-evaluable classes, and demonstrate test was never used for model selection. Do not report synthetic unit-test F1 as academic model performance.
