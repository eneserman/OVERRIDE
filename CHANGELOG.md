# Project change history (design, not model training)

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
