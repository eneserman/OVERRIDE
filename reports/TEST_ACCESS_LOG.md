# Test Gold Access Log — sealed prospective test (created 2026-10-28)

**Rule:** the sealed test gold (`data/gold/override_gold_TEST_SEALED_*.jsonl`, gitignored) may be opened ONLY for: (1) test adjudication, (2) test gold validation, (3) the **single final evaluation** after the model is frozen. It must NEVER be used for model selection, prompt improvement, hyperparameter tuning, debugging or error analysis.

Every access is recorded below. An unrecorded access is a **protocol violation**; any result influenced by it is reported as `protocol-violated / exploratory`, never as held-out performance.

**Post-creation non-viewing guarantee (CTO rule, 2026-10-28):** locking unlabeled test data and protecting the eventual test **gold** are different things. When `override_gold_TEST_SEALED_*.jsonl` exists, the model-development workflow **never opens it**: the adjudicator stores it, its SHA-256 is logged here **without loading the content into any development session**, and the only reader is the single final-evaluation command (`scripts/evaluate_frozen_test.py`) executed after the model is frozen and the owner approves. Development agents work only with train/dev gold; any request to inspect test labels during development is refused and logged.

| # | Date | Who | Purpose | Scope (files/rows) | Approver | Outcome |
|---|---|---|---|---|---|---|
| 0 | 2026-10-28 | (none) | Log created; test gold does not exist yet (0 human labels) | — | CTO | baseline: **no accesses so far** |

Related artifacts: `data/prospective_holdout/real_sgd_heldout_lock.json` (manifest SHA-256 `b42299f8…0581`, immutable), `reports/D3_GOLD_CREATION_PROTOCOL.md` (phases B + access control), `data/annotations/d3_test_packets_v0.1/` (blind packets; unlabeled content is also sealed from development use).
| 2026-10-29 | coordinator | none (blind packets only) | distributed sealed test-363 blind packets for human annotation (Yol A: both reviewers label all 363 independently); no test gold exists yet, none accessed |
| 2026-10-29 | coordinator | meta-statistics only (agreement script) | both reviewers delivered 363/363 blind test annotations; agreement computed and FROZEN (D3_TEST363_AGREEMENT_FREEZE.json, sha 36509d5f...); 63 disagreements written mechanically to a human-only worksheet; test gold NOT yet built and not inspected for model development |
