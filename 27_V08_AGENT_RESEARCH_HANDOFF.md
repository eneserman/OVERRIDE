# 27 — IDE agent execution contract for evidence-first OVERRIDE v0.8

> **LOCAL STATUS OVERLAY (2026-10-28):** several D0 items below are already **executed on this machine** (official SGD pinned at `e852981a`, hashes + full train audit, dev/test available). Read `reports/V08_LOCAL_STATUS_RECONCILIATION.md` **before** acting, so completed provenance work is not re-done and the real next steps (D1 mining → D2 holdout lock) are used.

Read `24_EXTERNAL_DATASET_RESEARCH.md`, `25_LITERATURE_BENCHMARKS.md`, `26_PROSPECTIVE_TEST_PREREGISTRATION.md`, `18_V07_RESEARCH_PROTOCOL.md`, `02_NLP_TASK_DESIGN.md`, `14_DATA_CONTRACTS.md` first.

**D0 — Provenance and source access:** Clone official SGD at a fixed commit (git clone), verify original train/dev/test source counts and SHA256. The local handoff has no full official SGD raw files. Obtain Frames only with permitted portal agreement, confirm license; record provenance. Confirm this externally; DO NOT invent hashes or claim acquisition on failed download.

**D1 — Real candidate mining:** Use `scripts/mine_sgd_revision_candidates.py` and bias sampling toward explicit old/new, keep, true restore, cancellation vs non-cancellation, and hard negatives, across domains. Preserve official partition boundaries; inspect actual candidate examples, not just regex counts.

**D2 — Prospective test lock:** Collect genuinely unseen SGD dev/test raw candidates, run `scripts/lock_prospective_holdout.py`, store read-only manifest and signed/timestamped checksums BEFORE model evaluation; don't use old 100 AI-reviewed records as blind test. Optionally add independently sourced Frames challenge if license confirmed.

**D3 — Annotation:** Independent humans assess blinded candidates and adjudicate per v0.7 protocol. Do not fabricate persons or turn AI pseudo-labels into gold. Human review controls negative vs cancel, ADD vs UPDATE, topic return vs RESTORE, unresolved reference. Every span offset exact, no projected invisible old values.

**D4 — Validated gold/freeze:** Produce gold with provenance and complete evidence, verify with `scripts/validate_annotations.py`; freeze splits with `freeze_gold_splits.py` on real independent families and bind test membership to preregistration. Report unavailable labels rather than fake metrics.

**D5 — Models:** Run reproducible lexical baseline (`scripts/run_synthetic_token_baseline.py`) as **synthetic engineering check only**. Implement/evaluate CRF + pretrained Transformer actual gold in IDE with pinned dependencies/checkpoints, two BIO heads, history-loss mask, fair ablation, saved predictions and stdout. No claim of real-model quality from synthetic-only numbers.

**D6 — Research results:** Report strict span F1 and per-label support on heldout real gold, context/no-context delta with family bootstrap, hard negative false positives, L4/L5 true restoration, licenses, error taxonomy. Literature results only in a separately labeled related-work table.

**D7 — Submission:** Public Github repo and PPTX with required contribution evidence; first line repository URL as prescribed by professor. No private reviewer identities or restricted raw datasets committed. Final results must be measured, not projected.

STOP conditions: missing raw source; unverifiable source license; no authentic human gold; too-few positive examples; contaminated test; split hash mismatch; model code not actually executed. Document blocker and leave result `NOT MEASURED`.
