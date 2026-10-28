# D1/D2 Execution Report — Mining, Test Lock and D3 Packet Preparation

**Date:** 2026-10-28 | **Executed by:** coding agent, commands below actually run | **Gold count: 0** | **Model metrics: none (not trained, by gate)**

Order followed per owner instruction: **D2 test lock FIRST** (frozen before any mining/model work), then **D1 train mining**, then D3 packet assembly. No dev/test example is used for model development, prompt improvement or hyperparameter selection (`data/prospective_holdout/EVALUATION_PROTOCOL_LOCK.md`).

---

## 1. Real data distribution and per-category candidate counts

Source: official SGD pinned at `e852981ae34990f4358979625854259302feaa78` (CC BY-SA 4.0). Split sizes measured: train 16,142 / dev 2,482 / test 4,201 dialogues (`reports/V08_UPSTREAM_PROVENANCE.json`).

### 1.1 Train candidate scan (D1) — 164,982 user turns scanned, heuristic buckets (NOT labels)

| Mining bucket | Observed in train | Mined (50/bucket) | In D3 packets (after exclusion) |
|---|---|---|---|
| HARD_NEGATIVE (no cue, has history) | 142,670 | 50 | 48 |
| NO_CONTEXT (no cue, no history) | 16,068 | 50 | 50 |
| UPDATE (actually/instead/change/switch/rather/make it/i meant…) | **3,457** | 50 | 50 |
| REFERENCE (that one/the first/the previous/what i said…) | 1,087 | 50 | 46 |
| CANCEL (cancel/not now/never mind/forget it/don't book…) | 880 | 50 | 29 |
| KEEP (keep/same/don't change/leave as is/retain…) | 498 | 50 | 50 |
| RESTORE (go back/back to/restore/first option/original/earlier choice) | **230** | 50 | 50 |
| MIXED (≥2 cue families in one turn) | 92 | 50 | 50 |
| **Total** | 164,982 | **400** | **373** (−27 holdout-text-overlap exclusions, see `reports/D3_COUNT_RECONCILIATION.md`) |

> **Correction (2026-10-28, CTO review):** the first version of this table mixed pre-exclusion and post-exclusion columns and summed to 375 instead of 373. The chain is 400 mined − 27 excluded = 373; full per-record reconciliation is in `reports/D3_COUNT_RECONCILIATION.md`.

Selected set: 26 services represented (largest: Events_2 71, Flights_1 41, Movies_33, Restaurants_1 22), **one example per dialogue** (miner-enforced), deterministic under seed 42 (`blind_reviewer_sha256 d0fab930490c1ddabd18d8ff741f4ce6d55e3bbc88787a7649319c14067e8c3e`).

### 1.2 Holdout candidate scan (D2 pool) — dev + test, seed 20261028, per-bucket 25

| Bucket | dev observed / selected | test observed / selected |
|---|---|---|
| UPDATE | 477 / 25 | 933 / 25 |
| CANCEL | 88 / 25 | 244 / 25 |
| KEEP | 40 / 25 | 191 / 25 |
| RESTORE | 17 / 16 | 71 / 25 |
| REFERENCE | 157 / 25 | 229 / 25 |
| MIXED | 13 / 13 | 23 / 23 |
| HARD_NEGATIVE | 21,099 / 25 | 36,442 / 25 |
| NO_CONTEXT | 2,472 / 25 | 4,164 / 25 |
| **Selected** | **179** | **198** |

### 1.3 Manual category inspection (real mined examples; findings affect annotation, not labels)

- **UPDATE** is the cleanest pool: explicit revisions with both cue and new value (`[99_00007 t12] "No actually, I want only 1 ticket."`; `[121_00028 t4] "…change my picking up date to the 10th of March."`). ADD-vs-UPDATE co-occurs in one turn (`121_00028`: Standard car = ADD, date = UPDATE) — annotators must split per-slot.
- **RESTORE bucket is dominated by TOPIC RETURN, not value restore** — all inspected samples resume a task instead of reverting a value (`[73_00069 t16] "…Can you go back and book 3 tickets…"`; `[70_00006 t18] "Back to the bus tickets…"`). Per guidelines R7/R8 these are **NOT** `RESTORE_CUE`; true restore-to-previous-value remains rare → confirms diagnostic-only decision.
- **CANCEL bucket is dominated by refusals/deferrals** (`[126_00002 t10] "Not now. Thanks for everything."`), not cancellations of prior instructions (R4/R5). 21 of 50 selected CANCEL rows were also boilerplate duplicates of holdout text (see §3) and were removed.
- **KEEP** mixes discourse (`"Let's keep looking"`, R9) with genuine retention (`"Yes, I need the same."`, R10).
- **REFERENCE** is genuine deixis (`"That one sounds perfect."`) — good for the reference layer.
- **MIXED** carries complex cases (`"Not now… Go ahead and book those tickets. Make it 4 tickets."` — deferral + UPDATE).

## 2. Test lock SHA-256 values and verification report

| Item | Value |
|---|---|
| Lock artifact | `data/prospective_holdout/real_sgd_heldout_lock.json` (`status: RAW_POOL_LOCKED_NOT_HUMAN_GOLD`) |
| **Manifest SHA-256** | **`b42299f8c0f999de5f940f3252ad1b891d12c1297ecd37413317509106960581`** |
| Locked pool file SHA-256 | `921dcd5d851bf27d4be8eb0dd365964738a120dfb2040f49fed69cfa853c0a72` (509,083 bytes) |
| Candidates / families | **363 / 358** (dev 174, test 189) |
| Algorithm / seed | `prospective_raw_pool_sha256_v1` / `20261028` |
| Source pin / license | `e852981ae34990f4358979625854259302feaa78` / `VERIFIED` (CC BY-SA 4.0) |
| Seen-file SHA-256 (exclusion registry) | pilot `55bad855a140650c…` (A=B), AI drafts `a1b45ed4…` / `106c90e3…` |
| Per-candidate bindings | `raw_record_sha256` + `current_text_sha256` for every row |
| **Independent verification** | `lock_prospective_holdout.py --verify` → **`RAW_POOL_LOCK_VALID`** (exit 0) — manifest reconstructs byte-identically; any future change to pool/seen/manifest breaks verification |

**Fail-closed exclusions before locking** (`data/prospective_holdout/pool_exclusion_log.json`): 14 of 377 mined pool rows removed — 11 in-pool duplicate texts (kept first), 2 dialogue-ID collisions with previously seen families, 1 previously seen text. The lock tool additionally enforces: SGD pool must come from dev/test only, no labels/hints in rows, no future-turn history, no repeated IDs/texts.

**Immutability rule (registered before mining):** selection is frozen now; it may not be revised after inspecting contents or model results. Dev/test is forbidden for training, prompt work and hyperparameter choice; the holdout is evaluated once, after model freeze.

## 3. Train/dev/test separation — leakage checks (all executed)

| Check | Result |
|---|---|
| example_id uniqueness (train mining 400, holdout 363) | ✅ unique; **train ∩ holdout = 0**; ∩ seen files = 0 |
| Dialogue-family disjointness holdout vs seen (pilot/AI drafts) | ✅ **0** (fail-closed exclusion enforced) |
| Dialogue-ID collisions train ∩ holdout | ⚠️ **6 IDs** — known SGD naming artifact: dialogue IDs repeat across official splits (train∩dev 2,481 / train∩test 4,191 / dev∩test 2,405 measured). Different dialogues, same ID. Mitigated: identity uses (split, file SHA-256, turn_index); the 6 collide only nominally |
| Current-utterance text overlap train ∩ holdout | ⚠️ 12 distinct boilerplate texts (e.g. "No, not now.") matched 27 train rows → **all 27 removed from D3 train side** (holdout untouched, it is locked) → re-check: **0 overlap** |
| D3 packet internal checks | ✅ ids unique, one per dialogue, no holdout text, no hint/state keys, all `UNLABELED` |
| Blind-packet leakage walk (forbidden keys, future turns, null spans) | ✅ **0 problems** on both D3 packets (A ≡ B byte-identical by design) |
| Synthetic bootstrap splits (504/126/126) | ✅ 0 exact collisions, 0 pairs Jaccard ≥ 0.9 (`reports/V08_SYNTHETIC_SPLIT_SEPARATION.json`) |
| Residual (documented, not fixable) | history-context boilerplate overlaps (71 shared history texts across partitions — SGD system templates); accepted as corpus-internal templating, not sampling error |

## 4. Blind D3 packets for human annotation

| Item | Value |
|---|---|
| Location | `data/annotations/d3_packets_v0.1/` (**local, gitignored — hand out directly; raw SGD excerpts stay out of the public repo**) |
| Files | `reviewer_A_BLIND.jsonl`, `reviewer_B_BLIND.jsonl` (byte-identical, `5f61…`→ filtered `9e0e6caec82015c2e6c9541f8d544c72b3b2131f5ae7f499bd8db4e5aa5cc987`), `PRIVATE_mining_manifest.jsonl` (**never show to annotators**), `d3_packet_qa.json` |
| Records | **373** (50 each UPDATE/KEEP/RESTORE/MIXED/NO_CONTEXT, 48 HARD_NEGATIVE, 46 REFERENCE, 29 CANCEL), one per dialogue, ≤12-turn history, `annotation.status=UNLABELED` |
| Also ready | previous pilot set `data/annotations/pilot_v0.1/` (100, seed 42) + guide `13_ANNOTATION_GUIDELINES.md` + tool `scripts/annotation_entry_helper.py` |
| Workflow | two **independent human** reviewers, blind, per `AGENT_D3_V07_REAL_GOLD_MASTER_PROMPT.md` and `22_HUMAN_REVIEW_QUICK_START_TR.md`; then normalize → agreement → adjudication. **Nothing becomes gold before real human review.** |

## 5. Failed checks, data insufficiencies and academic risks

1. **Lock rejections (fail-closed, expected):** first lock attempt aborted on contamination (`family_id_collision_with_seen`) and in-pool duplicate texts; resolved by documented exclusions — no silent rewrites. `pool_exclusion_log.json` lists every removal.
2. **SGD dialogue IDs collide across splits** (2,481/2,482 of dev IDs also exist in train). Consequence: `dialogue_id` alone is not a valid global family key; all grouping must include split + source file hash. Within-train gold splitting stays valid.
3. **CANCEL pool is weak:** observed 880 but mostly refusals ("not now"); explicit user-directed cancellations remain rare (D0: near-absent). Expect tiny real support → keep narrowed/diagnostic per decision log.
4. **RESTORE pool is weak for value-restore:** observed 230, dominated by topic-return; dev support tiny (17 observed / 16 selected). L4 stays diagnostic-only; test-side RESTORE F1 will likely be `NOT EVALUABLE`.
5. **Boilerplate recurrence:** identical short utterances recur across official splits; 27 train rows removed to protect the locked test; history-level template overlap (71 texts) remains and is disclosed.
6. **No human gold, no metrics:** 0 adjudicated examples; no model trained (D5 deliberately not started per owner gate). Every count above is a corpus statistic or candidate count — **not** an accuracy.
7. **Academic risks carried forward:** annotator availability (D3 = BLOCKED until two real reviewers), rare-class support may force NARROW after pilot; P2 collision re-check before submission (10 sheet rows still empty).

---

**Commands executed (all exit 0 unless noted):** `mine_sgd_revision_candidates.py --split dev|test --per-bucket 25 --seed 20261028` → `lock_prospective_holdout.py … --seed 20261028` → `lock_prospective_holdout.py --verify` (`RAW_POOL_LOCK_VALID`) → `mine_sgd_revision_candidates.py --split train --per-bucket 50 --seed 42` → cross-partition audit + blind-packet leakage walk → `audit_v08_split_separation.py`. Unit tests/preflight re-run after this work: 68/68 OK, `HANDOFF_PRECHECK_PASS`.

**Next gate (owner):** approve the locked protocol and the D3 packets, then organize **two independent human annotators**. D5 training stays blocked until human gold exists.
