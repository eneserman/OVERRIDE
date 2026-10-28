# OVERRIDE — Coding Agent Prompt: D0 Real SGD Audit Only

**Role:** NLP data engineer, implementing evidence-based research for Developers (NLP Project 2).

**Read first, in order:** `00_DESIGN_AUDIT.md`, `01_REQUIREMENTS.md`, `02_NLP_TASK_DESIGN.md`, `03_DATASET_PIPELINE.md`. Source is Google SGD, pinned to an actual upstream Git commit.

## Your mission (only this phase)

1. Set up a clean local Python environment. Do **not** build a website, install a web framework or create a mobile app. The assessed deliverable is reproducible Python code and GitHub documentation.
2. Fetch official Google SGD `train` files from https://github.com/google-research-datasets/dstc8-schema-guided-dialogue. Pin and report the exact git commit and file SHA-256 values; include dataset attribution and CC BY-SA 4.0 obligations.
3. Run `python -m unittest discover -s tests -v` and fix test/code defects if real source format exposes issues. Keep `data/upstream` unchanged.
4. Execute full train audit:
   `python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit`
5. Inspect the resulting `sgd_audit_summary.json`, `service_counts.csv`, and `UNREVIEWED_candidate_examples.jsonl`. Document real counts, group by change-candidate class, and **manually inspect ambiguous and false-positive examples** (alias, system offer, service switches, negated cancellation, first slot fills).
6. Add `reports/D0_D1_FACTUAL_FINDINGS.md`: empirical counts, sample evidence with provenance, offset validity, candidate coverage, gaps relative to L1–L5, annotation budget estimate, legal/licensing notes and a clearly stated GO/NO-GO recommendation for pilot.
7. Make only minimal, justified changes to the existing audit script/tests. Include a command log and full diff summary. Do not report work you have not executed.

## Mandatory boundaries

- **Never** treat SGD `frames[].state` differences as gold `UPDATE`, `KEEP`, `RESTORE` or `CANCEL` spans.
- **Never** feed current/future gold state or test labels into a model at inference time.
- **Never** create artificial evaluation scores, new class prevalences or unit-test PASS claims without executing tests.
- **Never** train a Transformer or CRF during this phase; only evaluate data feasibility.
- **Never** claim a UI or live system exists. Do not build a website.
- If source data cannot be downloaded, describe the blocker and stop with code tests only. Do not create fabricated substitutes labeled “real”.
- Do not overcommit scarce categories; if rare L4/L5 cases are absent, recommend a separately reported hand-verified diagnostic set, not fake training data.
- Do not change the primary project's scientific question or taxonomy without an explicit review decision.

## Deliverables required in your final report

- Exact dataset commit, split and file hashes, and data access status.
- Audit commands, raw output paths, real aggregate counts and warnings.
- At least several inspected candidate examples with examples of *false positives*, where data permits.
- Unit-test output, failures and repairs.
- A table of currently supportable vs unsupported token categories, with explicit **unverified** labels.
- STOP after D0/D1 and request a scope/taxonomy review before preparing human gold or training models.
