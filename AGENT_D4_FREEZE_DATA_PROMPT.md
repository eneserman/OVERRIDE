# AGENT D4 — Freeze Gold Corpus, Group Split, and Provenance

Prerequisite: owner-approved adjudicated gold + G2 review. Read `07_EVALUATION_METRICS.md`, `08_TESTING_AND_QA.md`, `14_DATA_CONTRACTS.md`.

1. Validate every gold record and exact offsets: `python scripts/validate_annotations.py --input <gold.jsonl> --require-gold --report <validation.json>`.
2. Check example IDs, dialogue IDs, dialogue-family grouping and paraphrase/near-duplicates; review any cross-family suspicious similarity rather than hiding it. No source family in two splits.
3. Run `python scripts/freeze_gold_splits.py --gold <gold.jsonl> --out <split_manifest.json> --seed 42`. Document algorithm, counts and file hashes. **Do not overwrite** a frozen manifest silently.
4. Inspect label support per split and by L1–L5; verify no empty or misleading class evaluation. If inadequate, report NARROW or propose **prospective** split before final freeze, not test-set cherry-picking.
5. Record source upstream SHA, annotation guideline version, adjudication outcome, data licensing policy, gold file SHA and split manifest digest in `reports/D4_FREEZE_REPORT.md`.
6. STOP. Return exact hashes/commands and request explicit permission before D5. No train/test leakage; no model-selection access to test labels.

## v0.6 constraint

Frozen manifest must include a content-bound hash of adjudicated labels and per-split class support. If a priority class has zero held-out support, mark unsupported and seek human approval for a prospective split redesign before any model-driven evaluation; never keep trying random seeds after inspecting models.
