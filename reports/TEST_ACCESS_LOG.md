# Test Gold Access Log — sealed prospective test (created 2026-10-28)

**Rule:** the sealed test gold (`data/gold/override_gold_TEST_SEALED_*.jsonl`, gitignored) may be opened ONLY for: (1) test adjudication, (2) test gold validation, (3) the **single final evaluation** after the model is frozen. It must NEVER be used for model selection, prompt improvement, hyperparameter tuning, debugging or error analysis.

Every access is recorded below. An unrecorded access is a **protocol violation**; any result influenced by it is reported as `protocol-violated / exploratory`, never as held-out performance.

| # | Date | Who | Purpose | Scope (files/rows) | Approver | Outcome |
|---|---|---|---|---|---|---|
| 0 | 2026-10-28 | (none) | Log created; test gold does not exist yet (0 human labels) | — | CTO | baseline: **no accesses so far** |

Related artifacts: `data/prospective_holdout/real_sgd_heldout_lock.json` (manifest SHA-256 `b42299f8…0581`, immutable), `reports/D3_GOLD_CREATION_PROTOCOL.md` (phases B + access control), `data/annotations/d3_test_packets_v0.1/` (blind packets; unlabeled content is also sealed from development use).
