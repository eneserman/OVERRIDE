> **OVERRIDE v0.7 DATA UPDATE:** For accurate current status read `18_V07_RESEARCH_PROTOCOL.md`, `19_DATASET_CARD_V07.md`, `20_GOLD_RELEASE_GATES.md`, `21_GOLD_READINESS_TR.md`, and `AGENT_D3_V07_REAL_GOLD_MASTER_PROMPT.md` **before** following the older v0.6 development handoff. In v0.7: 504 synthetic train + 126 synthetic dev + 126 synthetic challenge; 100 SGD pilot examples; 2 sets of 100 AI draft suggestions; **0 human-adjudicated gold**. No actual model training results. All synthetic/AI outputs must be disclosed. Academic gold release is BLOCKED pending real human review.

# Project change history (design, not model training)

## Gold v1.3 built — 2026-10-30 (before any test access)
- Round-2 dispositions locked (`D3_EXT2_DECISIONS.md`): 204 identical, 101 agreed on separate sheets, 11 joint, 4 kept from v1.2 by rule; 59 records change spans. K96 reverses F1 (RESTORE_CUE kept, three-turn context).
- `scripts/build_gold_v1_3.py` (fail-closed, tested): 857 records, validator PASS, SHA-256 `ce7b9a05…9dbc`. All 400 D3-EXT records are now double-blind.
- Split unchanged in membership (771 / 86); dev UPDATE_CUE support 26.

## D3-EXT round 2 agreement FROZEN — 2026-10-30 (amendment E4, before any decision)
- 320 single-annotated records, each now labeled blind by the second reviewer; round-2 first submissions vs the original annotator's revised file.
- **Exact layer-set agreement 0.805** (Burak-solo 0.803, Enes-solo 0.806); per label NEW_VALUE 0.951, REFERENCE 0.835, UPDATE_CUE 0.623. `reports/D3_EXT2_AGREEMENT_FREEZE.json`.

## D3-EXT round 2 packets — 2026-10-30 (amendment E3, before any round-2 label)
- Blind cross re-annotation of the 320 single-annotated D3-EXT records: Burak gets Enes's 160, Enes gets Burak's 160 (0 overlap with each other or the shared 80; all UNLABELED).
- Packets (local): `reviewer_A_BURAK_EK2_BLIND.jsonl` SHA-256 `4af6761e4d0ae5be9ea18f7d71ab0814ad07644106c4b7d141d7fdc11dc655bf`, `reviewer_B_ENES_EK2_BLIND.jsonl` `ed46771cf503a6b7e786935bc82875aa374295f98b6866bbe020bd35f592e72e`.

## Gold v1.2 built — 2026-10-30 (before any test access)
- 20 decisions locked (`D3_EXT_DECISIONS.md`): 18 matched between the two separate sheets; S4/S19 resolved jointly to B for consistency with gold v1.1; F1 removes one RESTORE_CUE.
- `scripts/build_gold_v1_2.py` (fail-closed, tested): **857 records** (457 v1.1 unchanged + 400 new: 61 double-blind agreed, 19 joint decisions, 320 single + rule scan). Validator PASS. SHA-256 `cc8efc0f…6362`.
- Split frozen from the union of the two pre-committed plans: 771 train / 86 dev; old 457 keep their partition. Dev UPDATE_CUE support 3 → 20.

## D3-EXT annotations received + agreement FROZEN — 2026-10-30 (before any test access)
- Both reviewers returned 240/240; amendment E2 (`D3_EXT_PROTOCOL.md` §8) records the production declaration (labels by the reviewers; AI for translation, offsets and JSON; helper not used), the exposure before revision and the rule: agreement from the FIRST submissions, revised files feed gold v1.2.
- **Frozen agreement (80 shared, first submissions):** exact layer-set **0.8625** (pilot 0.833, test 0.910 on the same metric); records identical in both layers 59/80; per-label NEW_VALUE 0.944, REFERENCE 0.857, UPDATE_CUE 0.692. `reports/D3_EXT_AGREEMENT_FREEZE.json`.
- Rule scan on the revised files (`scripts/rule_scan_v023.py`): 1 flag (a RESTORE_CUE). 19 shared records still differ between the revised files → local decision sheets for both reviewers.

## D3-EXT packets + gold v1.1 + D5 v1.1 — 2026-10-30 (before any test access)
- Gold v1.1 locked (`D3_GOLD_V1_1_DECISIONS.md`): 3 record changes; taxonomy narrowing Option A adopted (SCOPE-001).
- D5 rerun on v1.1 with the frozen config (`D5_RESULTS_V1_1.md`): BERT no-history dev mean 0.681; dev cue metric rests on 4 spans.
- D3-EXT pre-registered (`D3_EXT_PROTOCOL.md`, amendment E1 MIXED 80→30 / UPDATE 120→170 before any packet): **400 new train-side records, 80 double-annotated**, 240 per reviewer; 40 new families → dev by the plan rule (`D3_EXT_SPLIT_PLAN.json`).
- Packets (local): `reviewer_A_BURAK_EK_BLIND.jsonl` SHA-256 `c4155146b6e8203fe185b54a4e3d381f0a21a2c823c70aaa7f0e1a0bd8569bc0`, `reviewer_B_ENES_EK_BLIND.jsonl` `f1dd23fda41a16e5ac2ac7899325b7e692f9b8617338351166bfdea271e896fd`. Independent checks: 0 family / normalized-text overlap with all prior annotation, pilot and gold files; 0 holdout text or SHA overlap; no private bucket fields in packets.

## Gold v1 blind re-annotation audit — 2026-10-30 (score computed once and FROZEN; before any D6 test access)
- Pre-registered protocol (`reports/D3_GOLD_V1_AUDIT_PROTOCOL.md`, commit `b4a84bb`) + amendment A1 (`e4b8880`: AI limited to translation/offset, exposure declarations, rejected rounds, accepted files and their mechanical edits).
- Sample: 24 + 24 single-annotated gold v1 records (seed `20261030`), each re-annotated blind-at-annotation-time by the other reviewer.
- **Result (frozen):** exact layer-set agreement **22/48 = 0.458** (Burak-solo re-annotated by Enes 13/24; Enes-solo re-annotated by Burak 9/24); 26 records disagree. Re-annotations carry more spans than gold (value P 0.648 / R 0.885; cue P 0.321 / R 0.818). Rare cue labels have no gold support in the sample (not evaluable). n=48 → wide interval; not an exposure-naive error rate.
- Files: `reports/D3_GOLD_V1_AUDIT_RESULT.json` SHA-256 `634258541a2c22cd6fbb69e7a628ea7ae376bebc119098c188510960b8b29a1e`; gold v1 SHA-256 at scoring `1f7c286ead45aa80b226ec664b83e4a7604add136e27939f429cc93602cc5924` (unchanged).
- Next (not done): joint decisions on the 26 + 4 findings → gold v1.1 → same-plan re-freeze → D5 rerun → D6. Holdout untouched; `TEST_ACCESS_LOG` has no executed access.

## D3 ADJUDICATION FINAL — 2026-10-29 (joint decisions registered, gold build gated on calibration completion)
- Both reviewers approved proposals; joint resolution reached on the residual conflicts: **F1** `for/of/with+N` split, **F2** `around` outside, **`at least` inside**, **F3** (P4 artikelli `a small rental car [14-32]`, P7 agreed `it` removed, P9 `child-friendly` kept), **G1/G2** single version v0.2.3 for all sets, **G3** written C3 applied to agreed labels (2 `there` labels pending confirmation).
- Guideline **v0.2.3** published with change log + affected IDs (C1-r, C4, C6, G3); full record `reports/D3_ADJUDICATION_DECISIONS_FINAL.md`. G3 jointly confirmed: all 3 agreed bare labels (`it`, 2×`there`) removed from gold.
- **Test-363 disposition rule registered BEFORE training:** 3 of 63 disputes resolved by F1/F2 (take B's spans); remaining **60 records stay UNRESOLVED** — test reference uses only both-reviewer-agreed spans, all 60 reported explicitly at evaluation. Test gold builds post-D5 in one logged access.
- Train gold build gated on the last reviewer action: **calibration completion (4 records)** — G3 already confirmed. Frozen agreement scores unchanged (5e409339…, 36509d5f…).

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
