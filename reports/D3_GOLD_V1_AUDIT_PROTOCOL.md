# D3 — Gold v1 Quality Audit + v1.1 Re-freeze Plan (PRE-REGISTERED 2026-10-30)

**Status: PRE-REGISTERED — no audit label exists yet.** Registered BEFORE the locked
holdout is opened (TEST_ACCESS_LOG has no executed access #2) and BEFORE any
re-annotation. Owner decision (2026-10-30): run the audit package (findings sheet +
blind re-annotation sample + taxonomy-narrowing proposal), then re-freeze.

## 1. Why

Gold v1 (`data/gold/train_dev_gold_v1.jsonl`, 457 rows, validator PASS) has a weak
segment: **357 records were annotated by one reviewer** and then checked by the
other **non-blind** (DOGRULAMA sheets: 357/357 `K`, 0 changes). Approving a label
while seeing it is a weaker signal than an independent annotation, so the error
rate of this segment is currently unmeasured. The 100 double-blind records
already have measured agreement (pilot-30 exact layer-set 0.833; test-363 0.910 is
reviewer-vs-reviewer on the holdout).

A second observation: the 357 solo rows carry `guideline_version: v0.2.2+R1-R5`,
while G1 says all sets are adjudicated under v0.2.3. The v0.2.3 deltas (C1-r, F1,
F2, G3) were checked on these rows only by a mechanical scan (§3).

## 2. Blind cross re-annotation audit

| Item | Registered value |
|---|---|
| Pool | `solo_A_ids` (178, Burak) and `solo_B_ids` (179, Enes) from `data/annotations/d3_full457_assignment/assignment_index.json` |
| Excluded before sampling | the 4 finding IDs of §3 (already shown to reviewer B / owner on 2026-10-30 → exposure-contaminated): `SGD-7bb4b2f1283e503502`, `sgd_f90ea0abaea8773c2149`, `sgd_3324bf1e7d2ec8ca4acf`, `SGD-90cfacf6a275f8d7f3` |
| Rule | per solo set: sort IDs by `sha256('20261030::<id>')` ascending, take the first **24** → 48 records |
| Assignment | Burak's solo sample → **Enes** re-annotates; Enes's solo sample → **Burak** re-annotates |
| Packets | copied verbatim from the blind 457 packets (UNLABELED, no hints, no gold), stamped `guideline_version: v0.2.3` |
| Tool | `scripts/annotation_entry_helper.py` (launchers `data/annotations/BASLAT_4_DENETIM_*.bat`) |
| Independence | reviewers do not talk about items and do not open gold v1 or each other's files during the audit |
| Metric | per record exact layer-set agreement with gold v1; per-label exact-span P/R/F1 with gold v1 as reference; zero-support labels = NOT EVALUABLE |
| Scoring | `scripts/gold_v1_audit.py score` (code committed before any audit label; refuses if gold v1 bytes changed) |

**Known limitation (reported, not hidden):** each re-annotator saw these records'
labels once, during the DOGRULAMA verification on 2026-10-29. The audit is blind at
annotation time but not exposure-naive; agreement may be biased upward. The 4
excluded records are known mechanical findings, so the estimate covers the
remaining 353 solo records; the 4 are reported separately.

**Freeze rule:** the audit score is computed once and frozen (file SHA recorded in
`CHANGELOG.md`). Later gold corrections never change it.

**Disposition rule:** no automatic action from the score. Every disagreeing record
goes to the two reviewers for a **joint** decision (same procedure as
`D3_ADJUDICATION_DECISIONS_FINAL.md`); the coordinator transcribes only. If the
pooled agreement is clearly below the pilot-30 level (0.833), the reviewers decide
whether to extend the audit to more solo records; that decision is recorded here
before any further sampling.

## 3. Mechanical v0.2.3 findings (decision sheet)

Read-only scan of all 457 rows for C1-r / F1 / F2 / C3-G3 / edge whitespace /
punctuation / same-text-different-label: 4 flagged spans, listed in
`reports/D3_GOLD_V1_FINDINGS_WORKSHEET.md` for joint decision. Everything else
passed the scan. The scan flags candidates only; it decides nothing.

## 4. Taxonomy narrowing

Separate proposal awaiting both signatures: `reports/D5_TAXONOMY_NARROWING_PROPOSAL.md`.
It changes which claims are made, not the labels or the locked test.

## 5. Gold v1.1 → re-freeze → D5 rerun (all BEFORE test access)

1. Joint decisions for §2 disagreements + §3 findings → appended to a new decisions
   record `reports/D3_GOLD_V1_1_DECISIONS.md` (v1 record is not edited).
2. Build `data/gold/train_dev_gold_v1_1.jsonl` from gold v1 + those decisions only,
   with the same mechanical assertion style as `build_train_gold_v1.py`;
   validator `--require-gold --allowed-splits train` must PASS. Gold v1 stays on
   disk unchanged.
3. Split: the same pre-committed plan (`D3_TRAIN_DEV_SPLIT_PLAN.json`, seed
   20261028). Families do not change, so train/dev membership must be identical;
   `freeze_plan_split.py` writes a NEW manifest
   `reports/splits/frozen_plan_traindev_gold_v1_1.json` (only the gold hash and
   digest change). Any membership difference aborts.
4. D5 rerun with the identical committed configuration: same scripts, seed
   `20261029`, same CRF settings, same transformer config, same selection metric
   mean(dev value micro-F1, dev cue micro-F1), new output dirs (`*_v1_1`).
   No new systems, no hyperparameter search.
5. New freeze record `reports/D5_RESULTS_V1_1.md` committed BEFORE test access:
   the selected checkpoint + SHA. v1 results stay in `D5_RESULTS.md` and are
   reported as history.
6. Only then fix `reports/TEST_ACCESS_LOG.md` (the pending uncommitted row #2 must
   reference the v1.1 checkpoints and the owner's approval) and run D6 once.

## 6. Reproduce the sample

```bash
python scripts/gold_v1_audit.py sample \
  --assignment data/annotations/d3_full457_assignment/assignment_index.json \
  --blind-a data/annotations/d3_full457_assignment/reviewer_A_BURAK_BLIND_457.jsonl \
  --blind-b data/annotations/d3_full457_assignment/reviewer_B_ENES_BLIND_457.jsonl \
  --gold data/gold/train_dev_gold_v1.jsonl --seed 20261030 --per-set 24 \
  --exclude-ids SGD-7bb4b2f1283e503502,sgd_f90ea0abaea8773c2149,sgd_3324bf1e7d2ec8ca4acf,SGD-90cfacf6a275f8d7f3 \
  --outdir data/annotations/d3_gold_v1_audit
# after both packets are filled:
python scripts/normalize_review_packet.py --input data/annotations/d3_gold_v1_audit/ENES_reannotates_BURAK_solo_filled.jsonl \
  --reviewer-id reviewer_B_ENES --out data/annotations/d3_gold_v1_audit/ENES_reannotates_BURAK_solo_canonical.jsonl
python scripts/normalize_review_packet.py --input data/annotations/d3_gold_v1_audit/BURAK_reannotates_ENES_solo_filled.jsonl \
  --reviewer-id reviewer_A_BURAK --out data/annotations/d3_gold_v1_audit/BURAK_reannotates_ENES_solo_canonical.jsonl
python scripts/gold_v1_audit.py score --index data/annotations/d3_gold_v1_audit/PRIVATE_audit_index.json \
  --gold data/gold/train_dev_gold_v1.jsonl \
  --enes-canonical data/annotations/d3_gold_v1_audit/ENES_reannotates_BURAK_solo_canonical.jsonl \
  --burak-canonical data/annotations/d3_gold_v1_audit/BURAK_reannotates_ENES_solo_canonical.jsonl \
  --out reports/D3_GOLD_V1_AUDIT_RESULT.json
```

## 7. Amendment A1 — recorded 2026-10-30, BEFORE the audit score is computed

Nothing below changes the sample, the metric or the scoring code. It records how the
48 audit labels were produced, so the score is read with the right caveats.

**AI assistance (declared by both reviewers):** AI was used only for Turkish↔English
translation and for computing character offsets. The reviewers state the label
decisions are their own and were written separately. The coordinator cannot verify
this; it rests on the declaration.

**Exposure (declared by both reviewers):** neither reviewer saw or used AI-generated
interpretation notes or AI-proposed labels while producing the final audit labels.
*Coordinator's record of fact:* such AI files existed in this session and were
attached to the coordination chat by the owner (`BURAK_blind_onerilen_etiketler`,
`BURAK_24_kayit_duzeltilmis`, `ENES_BURAK_diyalog_yorumlari_24` with interpretation
and suggested-response fields, and `second_pass_*` fields in
`ENES_BURAK_bagimsiz_ikinci_tur_24`). The owner therefore held them. This is reported
as an unverifiable limitation, not as proof of use.

**Rejected rounds (not scored, kept locally):** Burak's earlier files
(`BURAK_blind_onerilen_etiketler`, `BURAK_24_kayit_duzeltilmis`,
`BURAK_reannotates_ENES_solo_filled`, `..._filled_revised`) were rejected by the
coordinator because their free-text notes, difficulty and transitions were
identical to AI-proposed labels or they failed the schema. Enes's first labeled file
(`ENES_BURAK_24_DOLDURULMUS_ETIKETLER`) used a non-schema cue vocabulary.

**Accepted files and their only mechanical edits:**
- Burak: `BURAK_24_BAGIMSIZ_YENI_ETIKETLEME` → two offsets changed after owner
  confirmation (record `SGD-9ceb3eb66464f93159`: `"1"` [0,1]→[23,24]; record
  `SGD-a00ffcbaa62cc924f6`: `"2"` [117,118]→[145,146]; cause: the offset tool
  returned the first occurrence). Logged in `BURAK_offset_corrections.json`.
- Enes: `ENES_BURAK_24_ANNOTATED_v023_DUZELTILMIS` → only `reviewer_id` `ENES` →
  `reviewer_B_ENES`. Before this file, Enes translated his non-schema cue
  vocabulary into the four schema cue labels himself: of 30 cue spans, 21 were
  removed and 9 kept (UPDATE→UPDATE_CUE 5, NEGATION→UPDATE_CUE 1,
  CONTINUE→KEEP_CUE 1, RETURN→RESTORE_CUE 2). The value layer did not change
  (24/24 records identical). Logged in `ENES_stage_log.json`.

**Reading the score:** n = 48 records (24 per set), so the agreement figure is a
rough estimate with a wide interval; per-label F1 on rare labels is not conclusive.
It estimates agreement of AI-assisted (translation/offset) human re-annotation with
gold v1 on the 353 eligible solo records. It is not an exposure-naive,
fully-independent error rate. Disagreements go to the two reviewers for a joint decision.
