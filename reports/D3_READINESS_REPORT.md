# D3 Readiness Report — 2026-10-28 (after CTO review)

**Status:** D3 PACKETS READY FOR HUMAN ANNOTATION | **Gold: 0** | **D5: NOT started (no approval)** | **Holdout lock: preserved and unmodified**

CTO verdict implemented: D2 raw holdout lock is kept as-is; D3 preparation continues; no gold without real human review; the two-AI-drafts are never presented as independent human review.

---

## 1. The four CTO checks — status

| # | Check | Status | Evidence |
|---|---|---|---|
| 1 | Candidate count reconciliation with source IDs | ✅ DONE | `reports/D3_COUNT_RECONCILIATION.md` + `.json` (39 excluded records, each with source file, file SHA-256, dialogue ID, turn index, bucket, reason, matching holdout IDs) |
| 2 | Deep leakage: full-dialogue hash, normalized text, similar conversations, history repeats | ✅ DONE | `reports/D3_LEAKAGE_AUDIT.md` + `.json` (0 identical dialogues/sequences across splits; 27 exact + 10 near-dup train rows removed; 12 similar pairs listed for inspection; 62 shared history strings classified; 7 cross-pool families resolved by split plan) |
| 3 | CANCEL/RESTORE diagnostic-only; clarify refusal-vs-cancel and topic-return-vs-restore; evaluate Frames | ✅ DONE | `13_ANNOTATION_GUIDELINES.md` → **DP-1 / DP-2 decision procedures** with mined examples; Frames path documented (separate pool, `--source-release-id`, lock untouched); standard-scope note added |
| 4 | Holdout untouched; separate train-side dev for model selection | ✅ DONE | `reports/D3_TRAIN_DEV_SPLIT_PLAN.json`: 454 dialogue families pre-assigned **before annotation** (409 `train_gold` / 45 `dev_gold`, same hash-bucketing as `freeze_gold_splits.py`, seed 20261028). The locked holdout (`b42299f8…0581`) was never modified; `--verify` still `RAW_POOL_LOCK_VALID` |

## 2. Final blind D3 packets

| Item | Value |
|---|---|
| Location | `data/annotations/d3_packets_v0.1/` (local; raw SGD excerpts — hand out directly, not pushed) |
| Files | `reviewer_A_BLIND.jsonl` / `reviewer_B_BLIND.jsonl` (byte-identical; **SHA-256 `cd851ff577c93c40edc6d7d48807c5de44a86a98200754d01e6eec3fd7d1f1d3`**), `PRIVATE_mining_manifest.jsonl` (**never show**), `d3_packet_qa.json` |
| Records | **361** blind `UNLABELED` (UPDATE 50, RESTORE 50, MIXED 50, KEEP 49, NO_CONTEXT 48, HARD_NEGATIVE 47, REFERENCE 44, CANCEL 23), one per dialogue, ≤12-turn history, full provenance per record (`source_file` + `source_file_sha256` + `dialogue_id` + `turn_index` + `service`) |
| Secondary pool | `data/annotations/pilot_v0.1/` (100, seed 42) — same rules |
| QA | ids unique ✓ · one per dialogue ✓ · no holdout exact text ✓ · no holdout near-dup ≥0.9 ✓ · no hint/state keys ✓ · all `UNLABELED` ✓ |

## 3. How the two reviewers work (independence by construction)

1. **Inspectable:** every record shows full past context + current utterance + provenance; nothing hidden except sampling heuristics (private manifest stays with the owner).
2. **Uncertain cases are flagged** by the annotator: best judgment + `difficulty` + `uncertainty_notes` starting with `UNCERTAIN:` (guide convention). Pre-annotation flagging is deliberately avoided (bias).
3. **Independent storage:** each reviewer fills their own file (`reviewer_A_filled.jsonl` / `reviewer_B_filled.jsonl`) via `scripts/annotation_entry_helper.py` (`--reviewer-id reviewer_X_<name>`); files are created/edited separately, originals immutable, `annotation_agreement.py` refuses identical reviewer IDs.
4. **Then:** `normalize_review_packet.py` per reviewer → `annotation_agreement.py` disagreements → human adjudication with reason log → only then gold (`validate_annotations.py --require-gold`). `audit_research_dataset.py --require-academic-gold` is expected to FAIL until real reviews exist.
5. **Prohibitions (unchanged):** no gold without human annotation; AI drafts (`AI_SIMULATION`) are never renamed to human/gold; no fabricated metrics; D5 stays blocked.

## 4. Tests and source provenance (executed, current)

| Item | Value |
|---|---|
| Unit tests | `python -m unittest discover -s tests -p "test_*.py"` → **68/68 OK** |
| Preflight | `scripts/preflight_handoff.py` → `HANDOFF_PRECHECK_PASS` |
| Source commit | SGD pinned `e852981ae34990f4358979625854259302feaa78` (`REAL_SOURCE_VERIFIED`; train 16,142 / dev 2,482 / test 4,201) |
| Holdout lock | manifest SHA-256 `b42299f8c0f999de5f940f3252ad1b891d12c1297ecd37413317509106960581`, `--verify` = `RAW_POOL_LOCK_VALID` |
| Repo | https://github.com/eneserman/OVERRIDE — history preserved, no rebuild |

## 5. Residual risks going into annotation

- **CANCEL (23) and RESTORE (50)** pools remain weak in true-class yield (refusals/topic returns dominate) → diagnostic-only per decision log; if human review confirms near-zero true support, classes are demoted rather than relabeled.
- **Boilerplate recurrence** inside SGD: 12 similar pairs (0.8–0.9) retained by decision; system-template history overlap (56 strings) is inherent and disclosed.
- **Deep-semantic paraphrase similarity** is not measurable with stdlib tooling — human spot-check during annotation is the control.
- **Annotator availability** is the critical path: D3 is BLOCKED until two real independent reviewers complete both packets.

**Next gate (owner):** approve this readiness state, then schedule the two annotators (≈4–6 h each, `--resume` supported). D5 stays blocked until adjudicated gold exists.
