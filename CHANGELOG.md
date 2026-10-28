> **OVERRIDE v0.7 DATA UPDATE:** For accurate current status read `18_V07_RESEARCH_PROTOCOL.md`, `19_DATASET_CARD_V07.md`, `20_GOLD_RELEASE_GATES.md`, `21_GOLD_READINESS_TR.md`, and `AGENT_D3_V07_REAL_GOLD_MASTER_PROMPT.md` **before** following the older v0.6 development handoff. In v0.7: 504 synthetic train + 126 synthetic dev + 126 synthetic challenge; 100 SGD pilot examples; 2 sets of 100 AI draft suggestions; **0 human-adjudicated gold**. No actual model training results. All synthetic/AI outputs must be disclosed. Academic gold release is BLOCKED pending real human review.

# Project change history (design, not model training)

## D3-prep — 2026-10-28 (CTO review checks 1-4, executed)
- Check 1 reconciliation: full chain 400 mined − 27 exact-text − 10 near-dup − 2 in-train = **361 final D3**; all 39 exclusions recorded with source IDs/hashes/reasons (`reports/D3_COUNT_RECONCILIATION.md/.json`); corrected the earlier 375/373 presentation error.
- Check 2 deep leakage: 0 identical dialogues/user-sequences across official splits (full-fingerprint SHA-256); punctuation-variant near-dups removed train-side; 12 similar pairs listed; 62 shared history strings classified (56 system templates); 7 pilot-vs-mining family collisions resolved by split plan (`reports/D3_LEAKAGE_AUDIT.md/.json`).
- Check 3: DP-1 (refusal≠CANCEL) and DP-2 (topic-return≠value-restore) decision procedures added to `13_ANNOTATION_GUIDELINES.md` with mined evidence; Frames enrichment path documented (separate pool, lock untouched); two-annotator standard scoped as OUR research bar, not a verified P2 mandate.
- Check 4: frozen train-side dev plan (454 families → 409 train_gold / 45 dev_gold, pre-committed before annotation, `reports/D3_TRAIN_DEV_SPLIT_PLAN.json`); locked holdout untouched, `--verify` still RAW_POOL_LOCK_VALID.
- `reports/D3_READINESS_REPORT.md` consolidates deliverables, tests (68/68) and provenance. Gold stays 0; D5 not started.

## D1/D2 — 2026-10-28 (test lock first, then train mining; executed)
- **D2 lock:** prospective real-test pool mined from official SGD dev+test (seed 20261028) and frozen: 363 candidates / 358 families, manifest SHA-256 `b42299f8…0581`, `--verify` → `RAW_POOL_LOCK_VALID`. Fail-closed exclusions logged (14). Evaluation protocol locked (`EVALUATION_PROTOCOL_LOCK.md`): dev/test forbidden for training/prompt/hyperparameter work; selection immutable; one final evaluation.
- **D1 mining:** 164,982 train user turns scanned; 400 candidates (50/bucket) mined deterministically (seed 42) with per-category inspection (UPDATE clean; RESTORE bucket dominated by topic-return; CANCEL bucket by refusals — both confirmed diagnostic-weak).
- **D3 packets:** 373 blind records ready at `data/annotations/d3_packets_v0.1/` (27 train rows removed for holdout text overlap; all QA checks pass; no hints/state in packets).
- **Leakage evidence:** ID/family/text checks across train-mining/holdout/seen + synthetic split audit (0 collisions). Known SGD dialogue-ID collision across splits documented.
- Evidence: `reports/D1_D2_EXECUTION_REPORT.md`. Gold remains 0; no model trained (D5 not started by owner gate).

## D3-facilitation — 2026-10-28 (annotation entry helper)
- Added `scripts/annotation_entry_helper.py`: interactive terminal data entry for the two human reviewers (typed phrase → mechanically computed/verified offsets, label vocabulary enforcement, same-layer overlap rejection, per-example contract validation via normalize+validate). Generates NO labels; never reads the private sampling manifest; crash-safe incremental saves with `--resume`.
- 12 new unit tests (47 total, all passing), including proof that helper output is accepted as non-gold `ANNOTATED` and always FAILS `--require-gold`.

## D1/D2 — 2026-10-28 (real-corpus blind pilot preparation, executed)
- Generated 100 UNLABELED blind annotation packets from real SGD train (`seed 42`, max 1/dialogue, 8-turn context) with 9-strata round-robin (shortfall 0; NEGATED_CANCEL pool confirmed 0).
- Verified: independent re-run → 4/4 byte-identical outputs (reproducible); automated leakage audit → 0 problems (no state/slot_values/hints/future turns in packets); 100 unique dialogue IDs.
- Added `reports/D1_D2_PILOT_PREPARATION.md` with stratum breakdown, real sample false-positive inspection and GO recommendation. STOPPED for two independent human annotators (D3); no gold/prefilled labels/F1/training.

## D0 — 2026-10-28 (real official SGD train audit, executed)
- Cloned and pinned official SGD at commit `e852981ae34990f4358979625854259302feaa78` (CC BY-SA 4.0); SHA-256 of all 127 train files recorded in `reports/SHA256_SGD_TRAIN_FILES.txt`.
- Ran full read-only `audit_sgd.py` train audit: 16,142 dialogues, 329,964 turns, 242,267/242,267 valid span offsets. Raw outputs stay local (`reports/sgd_train_audit/`, gitignored).
- Added `reports/D0_D1_FACTUAL_FINDINGS.md`: measured candidate coverage, manual false-positive inspection (alias expansions, bare-"No" dilution ≈80%, hypothetical/third-party cancellations, travel-sense "back to"), zero corpus support for negated cancellation, category support table and GO/NARROW/NO-GO.
- No script/test changes required (35/35 tests pass on real source format). No gold labels, training or metrics produced — hard gate respected.

## v0.5 — 2026-10-27
- Consolidated all preparable design documents: architecture, modeling, evaluation, QA, release, presentation storyboard, risks, human annotation manual, data contracts and legal review checklist.
- Added controlling master prompt and D3–D7 phase prompts, plus agent start guide.
- Added standard-library Python annotation validator, split freezer, exact-span scorer, reviewer packet converter, and A/B disagreement reporter. Synthetic unit tests extended and run.
- Updated CLI-only delivery target and source-vs-gold status register; no webpage and no fabricated metrics.
- Did not download/evaluate the full SGD data or train ML models; those remain future verified execution work.

## v0.4 — 2026-10-27
- Blind pilot sampling, D0 audit code, design/requirements v0.3 and controlled D0–D2 prompts.

## v0.6 — scientific integrity hardening
- Fixed history provenance checks, reviewer consistency, duplicate reviewer identity guard and preservation of existing annotated queues.
- Strengthened adjudicated gold provenance contract, SHA-256 binding of gold to split manifest and per-split class support diagnostics.
- Added `evaluate_frozen_test.py` to prevent inadvertent train-as-test metrics and `preflight_handoff.py` for local checks.
- Expanded unit-test regressions and documented outstanding real-data/human/ML/release blockers in `17_V06_HARDENING_AUDIT.md`.


## v0.8 — 2026-10-28
- Verified related corpora and published DST benchmark sources (not OVERRIDE performance).
- Added prospective raw holdout lock + verification and mandatory contamination checks.
- Added official SGD provenance verifier, Frames candidate extractor and Python tests.
- Actually trained a classical token BIO model on synthetic data and saved separate exact-span diagnostic results.
- Main real gold, blind real test and real model scores still NOT AVAILABLE.
