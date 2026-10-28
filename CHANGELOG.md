# Project change history (design, not model training)

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
