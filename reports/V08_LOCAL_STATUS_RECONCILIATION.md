# V0.8 Local Status Reconciliation — 2026-10-28

**Purpose:** the v0.8 handoff package was authored in an environment where the official SGD download had failed. On this machine, real-source work was executed the same day. This file records which v0.8 status claims are **superseded by executed evidence**, so no agent re-does finished work or trusts stale blockers. The v0.8 documents themselves are kept byte-identical as the package's own record; this reconciliation is the dated overlay.

## Superseded claims → current measured facts

| v0.8 claim (file) | Status | Current fact (evidence) |
|---|---|---|
| "Full original SGD repo: NOT DOWNLOADED; source hash cannot be asserted" (`28_V08_EVIDENCE_AUDIT.md`, `19_DATASET_CARD_V07.md`, `23_V07_PACKAGE_README.md`) | **SUPERSEDED** | Official SGD cloned; pinned commit `e852981ae34990f4358979625854259302feaa78`; 127 train file SHA-256s in `reports/SHA256_SGD_TRAIN_FILES.txt`; full audit `reports/D0_D1_FACTUAL_FINDINGS.md` (16,142 dialogues, 242,267/242,267 valid offsets) |
| `REPRODUCIBILITY_MANIFEST.json: full_official_sgd_downloaded: false` | **SUPERSEDED** | `true` as of 2026-10-28 on this machine; verified again by `scripts/inspect_upstream_provenance.py` → `reports/V08_UPSTREAM_PROVENANCE.json` (`REAL_SOURCE_VERIFIED`; train 16,142 / **dev 2,482 / test 4,201** dialogues, per-file SHA-256) |
| D0 next step: "git clone official SGD … pin HEAD … run inspect_upstream_provenance.py" (`27`, `29_NEXT_ACTIONS_TR.md`) | **DONE** | Executed 2026-10-28 (commands + exit codes in `reports/D0_D1_FACTUAL_FINDINGS.md` §2 and `reports/V08_UPSTREAM_PROVENANCE.json`) |
| "Repo license final choice … still needs review" (`28`) | **PARTLY SUPERSEDED** | Code license decided: root `LICENSE` = MIT (owner-approved 2026-10-28). Remaining open item is only *data* redistribution handling — resolved by root `DATA_LICENSE_AND_ATTRIBUTION.md` (CC BY-SA 4.0 derivatives attributed; full raw corpus stays out of the repo) |
| "Update P2 collision check" gates (`20`, `26`) | **DONE (re-check recurring)** | Live Blackboard P2 sheet checked 2026-10-28: no topic/dataset collision (Avengers=LID, Group8=punctuation, LucidAI=PII, Ultron=event args; SGD unclaimed). Re-check before submission — 10 rows still empty (`RELEASE_PRECHECK.md`) |
| Pilot packet location `data/sgd_pilot/annotator_*_UNLABELED.jsonl` ("user-supplied packets") | **ALIAS, same data** | These files are byte-identical (SHA-256 `55bad855a140650c…`) to the packets generated 2026-10-28 at `data/annotations/pilot_v0.1/` by `scripts/prepare_annotation_pilot.py` (seed 42, max 1/dialogue, 8-turn context; reproducibility and leakage checks in `reports/D1_D2_PILOT_PREPARATION.md`). One packet set, two locations; **not** 200 examples |
| Reviewers annotate "manually" (`22_HUMAN_REVIEW_QUICK_START_TR.md`) | **OPTIONAL TOOL ADDED** | `scripts/annotation_entry_helper.py` (typed phrase → verified offsets, vocabulary/overlap enforcement, crash-safe `--resume`); generates no labels; documented in `13_ANNOTATION_GUIDELINES.md` |
| Eight-label full-scope annotation targets (`18`, `20`, `27 D6`) | **NARROWED (see `11` decision log)** | D0 evidence: negated-cancel 0/164,982 user turns; explicit user-directed cancels near-absent; genuine RESTORE tens. Trainable core = `UPDATE_CUE`/`KEEP_CUE` + `NEW/OLD/KEPT_VALUE`; `CANCEL_CUE` restricted to explicit instructions; `RESTORE_CUE`/L4–L5 diagnostic-only, separately reported |

## Not changed (still true and binding)

- **0 human-adjudicated gold.** `data/gold/` remains empty by design; `--require-academic-gold` failing is correct.
- **AI drafts are `AI_SIMULATION`** and must never be renamed to human/gold; `data/ai_suggestions/` numbers are not IAA.
- **Synthetic 504/126/126 diagnostics are synthetic only**; `V08_MEASURED_SYNTHETIC_BASELINE.json` is not a real benchmark.
- **The 100 AI-examined pilot/train examples can never be the blind prospective test** (26 preregistration). The frozen real test must come from unseen **dev/test** candidates via `lock_prospective_holdout.py` — now possible locally (dev/test present and hash-verified).
- Two genuinely independent human annotators are still required for D3; if unavailable, D3 stays **BLOCKED** and the fallback framing in `29_NEXT_ACTIONS_TR.md` applies.

## Next executed steps (in order)

1. **D1** real candidate mining (`scripts/mine_sgd_revision_candidates.py --per-bucket 50 --seed 42`) on the pinned corpus.
2. **D2** prospective holdout lock from unseen dev/test candidates (`scripts/lock_prospective_holdout.py --git-sha e852981ae34990f4358979625854259302feaa78`), before any model evaluation.
3. **D3** human annotation of blinded packets (owner coordinates two real reviewers).
