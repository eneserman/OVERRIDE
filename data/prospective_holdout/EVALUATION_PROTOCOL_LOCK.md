# Evaluation Protocol Lock — v0.8 (locked 2026-10-28, before any model development)

**Status:** PROTOCOL_LOCKED | **Binding:** this document and `real_sgd_heldout_lock.json` define the evaluation contract for all later phases (D5–D7). Any deviation must be recorded as a protocol violation, not silently applied.

## 1. Frozen test selection (immutable)

- **Lock artifact:** `data/prospective_holdout/real_sgd_heldout_lock.json`
- **Manifest SHA-256:** `b42299f8c0f999de5f940f3252ad1b891d12c1297ecd37413317509106960581`
- **Pool:** 363 blind candidates / 358 dialogue families mined deterministically from official SGD **dev + test** (seed `20261028`, `scripts/mine_sgd_revision_candidates.py`, per-bucket 25), after fail-closed exclusions (14 removed: 11 in-pool duplicate texts, 2 dialogue-ID collisions with seen families, 1 previously seen text — `private_pool/pool_exclusion_log.json`).
- **Source pin:** SGD commit `e852981ae34990f4358979625854259302feaa78`, `license_status: VERIFIED` (CC BY-SA 4.0).
- **Excluded by construction:** every record in `data/annotations/pilot_v0.1/`, `data/sgd_pilot/`, `data/ai_suggestions/` (100 AI-examined pilot examples and their dialogue families) — enforced by the lock tool at ID, dialogue-family and normalized-text level; verified by `--verify` → `RAW_POOL_LOCK_VALID`.

**The test selection is frozen NOW and must not be changed after this point** — not in response to inspecting example content, mining results, model outputs, or error analyses. Membership changes require a documented protocol deviation and a new lock; results obtained under a changed test cannot be reported under this registration.

## 2. Permitted and forbidden data use

| Data | Model training | Hyperparameter / prompt / threshold selection | Error analysis | Final reported test |
|---|---|---|---|---|
| SGD train (incl. D1 mined candidates, D3 future gold train/dev splits) | ✅ | ✅ (via gold train-side dev split only) | ✅ | ❌ |
| **SGD dev/test — locked holdout (363)** | **❌ FORBIDDEN** | **❌ FORBIDDEN** | **❌ until final evaluation** | ✅ once, after freeze |
| Synthetic bootstrap 504/126/126 | ✅ (warm-start, disclosed as synthetic) | ✅ (engineering only) | ✅ | ❌ never as real test |
| AI drafts (`data/ai_suggestions/`) | ❌ as labels | ❌ | ✅ (triage only) | ❌ |

**Dev/test examples must never enter model development, prompt engineering, or hyperparameter selection.** The locked holdout is touched exactly once for the final evaluation (D6), after model choices are fixed on train-side data.

## 3. Evaluation steps when the gate opens (D5 → D6)

1. Human-annotate and adjudicate the locked holdout (D3 workflow, two independent reviewers) → prospective test gold. Until then the holdout has **no gold and no scores**.
2. Freeze the model selection procedure using only train-side gold (family-disjoint train/dev from `freeze_gold_splits.py`); record all seeds/hyperparameters.
3. Run the frozen test **once** via `scripts/evaluate_frozen_test.py`-style strict exact-span scoring (VALUE and CUE heads separately), with per-label support; zero-support labels = `NOT EVALUABLE`.
4. Report micro P/R/F1 with denominators, family-bootstrap confidence intervals where feasible, and the history-vs-no-history ablation on identical example IDs. Published DST JGA numbers stay in the separately labeled literature table (not comparable to span F1).

## 4. Known data-quality caveats recorded at lock time

- **SGD dialogue IDs collide across official splits** (train∩dev 2,481 IDs; train∩test 4,191; dev∩test 2,405 — measured 2026-10-28). `dialogue_id` alone is therefore NOT a global family key; the lock combines `(dataset, split, dialogue_id, turn_index, source_file_sha256)`. Within-train gold splitting remains valid because train IDs are unique within train.
- RESTORE-bucket support is small in dev (16 selected of 17 observed) — rare-class test support will be limited; report as diagnostic where support is insufficient.
- The lock pool is a **heuristic candidate pool**, not gold; bucket labels are mining hints only and must never be shown to annotators or treated as labels.
