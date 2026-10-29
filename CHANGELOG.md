> **OVERRIDE v0.7 DATA UPDATE:** For accurate current status read `18_V07_RESEARCH_PROTOCOL.md`, `19_DATASET_CARD_V07.md`, `20_GOLD_RELEASE_GATES.md`, `21_GOLD_READINESS_TR.md`, and `AGENT_D3_V07_REAL_GOLD_MASTER_PROMPT.md` **before** following the older v0.6 development handoff. In v0.7: 504 synthetic train + 126 synthetic dev + 126 synthetic challenge; 100 SGD pilot examples; 2 sets of 100 AI draft suggestions; **0 human-adjudicated gold**. No actual model training results. All synthetic/AI outputs must be disclosed. Academic gold release is BLOCKED pending real human review.

# Project change history (design, not model training)

## D3 ADJUDICATION FINAL — 2026-10-29 (joint decisions registered, gold build gated on 2 items)
- Both reviewers approved proposals; joint resolution reached on the residual conflicts: **F1** `for/of/with+N` split, **F2** `around` outside, **`at least` inside**, **F3** (P4 artikelli `a small rental car [14-32]`, P7 agreed `it` removed, P9 `child-friendly` kept), **G1/G2** single version v0.2.3 for all sets, **G3** written C3 applied to agreed labels (2 `there` labels pending confirmation).
- Guideline **v0.2.3** published with change log + affected IDs (C1-r, C4, C6, G3); full record `reports/D3_ADJUDICATION_DECISIONS_FINAL.md`.
- **Test-363 disposition rule registered BEFORE training:** 3 of 63 disputes resolved by F1/F2 (take B's spans); remaining **60 records stay UNRESOLVED** — test reference uses only both-reviewer-agreed spans, all 60 reported explicitly at evaluation. Test gold builds post-D5 in one logged access.
- Train gold build gated on 2 reviewer actions: G3 confirmation (2 labels) + calibration completion (4 records). Frozen agreement scores unchanged (5e409339…, 36509d5f…).

## D3-pilot-30 RESULTS — 2026-10-29 (first real human agreement, executed)
- Two independent human annotators (reviewer_A_BURAK, reviewer_B_ENES) completed the blind pilot-30; format validation 0 errors. Real agreement measured: **exact layer-set 0.8333**; per-label exact-span **NEW_VALUE F1 0.800, REFERENCE F1 0.667, UPDATE_CUE F1 1.000**; difficulty agreement 0.9333. OLD_VALUE/KEPT_VALUE/KEEP_CUE/CANCEL_CUE/RESTORE_CUE = 0 support → NOT EVALUABLE (consistent with D0/D1).
- All 10 disagreements in 3 convention zones (boundary 5, value-ness 4, deixis 3); cue layer perfect (DP-1 and DP-4 both held). Decision: **REVISE-lite → GO**.
- Guideline **v0.2.2**: C1 boundary, C2 value-ness, C3 deixis conventions added with the 10 affected example IDs for re-check (change log updated; locked test selection untouched).
- Evidence: `reports/D3_PILOT30_RESULT.md`, `reports/D3_PILOT30_AGREEMENT.json`. Gold still 0 (adjudication next); D5 not started.

## Guideline v0.2.1 — 2026-10-28 (FROZEN for the human pilot; CTO rules 1-3)
- `13_ANNOTATION_GUIDELINES.md` v0.2.1 with three clarifications before human annotation: **DP-3** REFERENCE = specific referable value/option, not topic return; **DP-4** UPDATE_CUE only on explicit cue spans (no invented cues for implicit change); **DP-5** ADD vs UPDATE by the same slot's previous value (uncertainty recorded instead of forced UPDATE).
- Rule examples verified **independent of all annotation packets** (8/9 candidates outside merged-457/test-363; the one in-pool candidate discarded). Change-log row added; guideline version frozen pre-pilot; locked test selection untouched.
- No datasets, splits, holdout lock or AI drafts modified; no new AI labels; gold stays 0; D5 not started.

## D3-AI-prereview-review — 2026-10-28 (private quality diagnosis; NOT gold)
- Reviewed the CTO's pilot-30 AI suggestion package (2 policies, `AI_SIMULATION`) against guide v0.2: DP-1 respected 6/6 (no CANCEL on refusals), DP-2 respected 3/3 (no RESTORE on topic returns). Drafts kept local/gitignored — never shown to reviewers.
- Coverage diagnosis confirms the CTO finding: only NEW_VALUE/REFERENCE/UPDATE_CUE observable in pilot-30; `OLD_VALUE`, `KEPT_VALUE`, `KEEP_CUE`, `RESTORE_CUE` have zero support there (cancel/restore buckets contain refusals/topic-returns). Pilot-30 = quality diagnostic + agreement trial for observable labels; **no schema-wide GO from it**.
- The 6 AI-policy disputes analyzed against the guide → 3 rule zones: task-reference (guide gap), implicit-cue labeling, ADD-vs-UPDATE boundaries → candidate v0.3 rules listed for decision at pilot review (change-log mechanism; locked test selection immutable).
- Hash reconciliation: `reports/PACKET_HASH_AUDIT.json` — recorded content-SHA (LF) vs file-byte SHA (CRLF); test packet bytes = locked pool SHA `921dcd5d…` (byte-identical to holdout lock source). Integrity clean.
- `reports/D3_PILOT30_AI_PREREVIEW_REVIEW.md` is the diagnosis record. Human gold stays 0; agreement not measured; D5 not started.

## D3-pilot-verification — 2026-10-28 (CTO: no new features; bookkeeping only)
- Verified pilot-30 ⊂ merged-457 (records byte-identical), disjoint from the 10 calibration items; 457 = 30 + 10 + 417 (**no double counting**); independent agreement items = 447. Role registry: `data/annotations/annotation_registry_v0.1.json`.
- `reports/D3_PILOT30_REPORT_TEMPLATE.md`: GO/REVISE/STOP decision report skeleton (per-label agreement table, class supports, bad spans, DP-1/DP-2 disagreement analysis, workload) to be filled ONLY from real human files.
- `TEST_ACCESS_LOG.md`: post-creation non-viewing guarantee — dev workflow never opens test gold; only the single final evaluation reads it (owner-approved).
- 76/76 tests; gold stays 0; holdout untouched; D5 not started.

## D3-final-prep — 2026-10-28 (CTO GO for technical prep; executed)
- Calibration separated from independent scoring: `annotation_agreement.py --exclude-ids` (PRIMARY score excludes discussed practice items; both variants disclosed; tested).
- Pilot-30 independent trial packet built (`data/annotations/d3_pilot30_v0.1/`, 30 train-partition items, disjoint from calibration, stratified, SHA `3a6d7e77…`) + `D3_PILOT30_TRIAL_PROTOCOL.md` (analysis commands, guideline-fix flow, GO/narrow decision before the 1,640-judgment full run).
- Test gold sealing hardened: `reports/TEST_ACCESS_LOG.md` (zero accesses), access purposes restricted, violation policy.
- Guideline change-log added to `13` (version + affected IDs; locked test selection immutable).
- `reports/D3_ANNOTATION_HANDOFF.md`: exact reviewer file list + remaining blockers. 76/76 tests; gold stays 0; D5 not started.

## D3-technical-prep — 2026-10-28 (CTO approved; executed)
- Pools: merged 361 mining + 100 pilot → **457 blind train/dev records** (4 identical-turn duplicates logged & dropped; 7 overlapping families grouped to one partition per pre-committed plan); sealed **363 test packets** from the locked pool (no hints/AI/model content); 10-item TRAIN calibration sample.
- Tooling: `validate_annotations` gains `allowed-splits` (default unchanged; `dev,test` for sealed test gold); `annotation_agreement` gains per-label exact-span agreement + difficulty/uncertainty reporting; new `build_adjudicated_gold.py` builds gold ONLY from human decisions (5 safety tests). 75/75 tests.
- Protocols delivered: `D3_REVIEWER_ONBOARDING_TR.md` (TR onboarding), `D3_CALIBRATION_PROTOCOL.md` (DP-1/DP-2 practice + teaching key marked NOT gold), `D3_GOLD_CREATION_PROTOCOL.md` (agreement/adjudication commands, test access control, class-support honesty rule), `D3_TECHNICAL_QA_REPORT.md`.
- Holdout lock re-verified `RAW_POOL_LOCK_VALID`; gold stays 0; D5 not started.

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
