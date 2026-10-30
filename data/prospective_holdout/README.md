# Prospective holdout — lock

`real_sgd_heldout_lock.json` froze the prospective test **before any annotation or model**: 363 candidate turns / 358
dialogue families mined deterministically (seed 20261028) from official SGD **dev + test** at commit `e852981a`, after
fail-closed exclusions (`pool_exclusion_log.json`). Each turn is stored as IDs and SHA-256 hashes of its text; the
manifest hash is `b42299f8c0f999de5f940f3252ad1b891d12c1297ecd37413317509106960581`
(`python scripts/lock_prospective_holdout.py --verify ...` → `RAW_POOL_LOCK_VALID`).

The evaluation contract is `EVALUATION_PROTOCOL_LOCK.md`. The test reference was built once, after the model freeze
(`reports/TEST_ACCESS_LOG.md`), and is released as `data/gold/test_reference_v1.jsonl`.
