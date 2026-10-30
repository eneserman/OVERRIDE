# D3-EXT — 400 additional train-side gold records (PRE-REGISTERED 2026-10-30)

**Status: PRE-REGISTERED — committed before any candidate is drawn and before any label exists.**
Owner decision (2026-10-30): 400 new records, 80 annotated by both reviewers, 320 split between them.
Purpose: more train/dev support for the claimed classes (NEW_VALUE, REFERENCE, UPDATE_CUE) and a less noisy
dev set. The locked holdout (`real_sgd_heldout_lock.json`) is not touched; its pool text is used only to exclude
overlapping utterances, as in D1.

## 1. Candidates and exclusions (`scripts/build_ext_packets.py`, fail-closed)

- Source: official SGD **train** (pinned commit `e852981a…`), every USER turn, buckets from
  `mine_sgd_revision_candidates.scan_dialogues` (heuristic, private, never shown to reviewers).
- Excluded entirely: any train dialogue (= family) that appears in `data/annotations/**`, `data/sgd_pilot/**` or
  `data/gold/**` (gold v1.1, pilot-100 incl. the AI-examined records, D1 mining, calibration, audit); any utterance
  whose normalized text appears there or in the locked holdout pool; any utterance whose raw SHA-256 is in the lock.
- At most one record per dialogue; no two records with the same normalized text.

## 2. Sample (seed `20261031`)

| Bucket | Quota | Shared (both reviewers) |
|---|---|---|
| UPDATE | 120 | 24 |
| MIXED | 80 | 16 |
| HARD_NEGATIVE | 60 | 12 |
| REFERENCE | 50 | 10 |
| NO_CONTEXT | 30 | 6 |
| CANCEL | 20 | 4 |
| KEEP | 20 | 4 |
| RESTORE | 20 | 4 |
| **Total** | **400** | **80** |

Weighting favours explicit-revision buckets (claimed classes) and keeps span-less negatives (gold v1.1 has ~1/3
empty records). A bucket that cannot meet its quota aborts the build; quotas are never adjusted after drawing.
Assignment per bucket: ids ranked by `sha256('20261031::<id>')`; first *shared* go to both; the rest alternate
A/B → **each reviewer labels 240 records** (80 shared + 160 own). Packet order is shuffled per reviewer.

## 3. Train/dev for the new families (fixed now)

Same rule as `D3_TRAIN_DEV_SPLIT_PLAN.json`: `sha256('20261028::<family>')[:15] / 16^15 < 0.10 → dev_gold`, else
train_gold. Written to `reports/D3_EXT_SPLIT_PLAN.json` at build time, before annotation. Existing 457 records keep
their assignment.

## 4. Annotation rules

- Tool: `scripts/annotation_entry_helper.py` via `BASLAT_5_EK_A.bat` (Burak) / `BASLAT_5_EK_B.bat` (Enes); the
  helper enforces the label vocabulary and computes offsets. Guideline **v0.2.3**.
- Independent: no discussion of items, no access to the other reviewer's file, gold or the private index.
- AI: translation only (TR↔EN). No AI labels, no AI offsets, no AI "interpretation" notes. Any other AI use is
  declared before scoring and reported.

## 5. Quality measurement and disposition (fixed now)

1. **Agreement on the 80 shared records** is computed once with `annotation_agreement.py` (exact layer-set + per-label
   exact-span) and frozen before any adjudication (file SHA in `CHANGELOG.md`).
2. Shared disagreements → both reviewers decide separately, then jointly where they differ (same procedure as
   `D3_GOLD_V1_1_DECISIONS.md`). A change needs both reviewers; otherwise the record is decided at the joint step.
3. The 320 solo records get the mechanical v0.2.3 rule scan (C1-r, F1, F2, C3/G3, C6, DP-1/DP-2/R9 cue patterns,
   edge whitespace/punctuation); flagged spans go to the same joint decision. No other second pass is promised.
4. Gold **v1.2** = gold v1.1 + the 400 decided records, validator `--require-gold --allowed-splits train` must PASS;
   split = existing manifest + `D3_EXT_SPLIT_PLAN.json`.
5. Reporting: segment counts (double-blind adjudicated vs single + scan) and the frozen agreement are stated next to
   every model result trained on v1.2.

## 6. What does not change

The locked holdout, its consensus-reference rule (DEV-001), the evaluation metrics, the taxonomy scope (SCOPE-001)
and the frozen audit score. D5-v2 (grouped CV, model changes) is planned on gold v1.2 and will be pre-registered
separately before any run.

## 7. Amendment E1 — before any packet existed (2026-10-30)

The first build aborted fail-closed: **MIXED had only 39 eligible dialogues** (92 MIXED turns in all of SGD train).
Only per-bucket eligible counts were computed; no candidate was drawn, written or viewed. Eligible dialogues per
bucket: UPDATE 2767, REFERENCE 705, CANCEL 439, KEEP 360, RESTORE 156, MIXED 39, HARD_NEGATIVE 15649, NO_CONTEXT 15435.
Change: **MIXED 80 → 30, UPDATE 120 → 170** (shared MIXED 16 → 6, UPDATE 24 → 34). Totals stay 400 records / 80
shared / 240 per reviewer; the table in §2 is superseded by these values. UPDATE takes the slots because it is the
bucket with explicit revision words, i.e. the claimed classes.

## 8. Amendment E2 — how the labels were produced; which version is scored (2026-10-30, BEFORE agreement is computed)

**Declaration (owner, also on behalf of Burak, relayed):** the labels were given by Burak and Enes separately; AI was
used for translation, offset calculation and writing the JSON — it did not suggest labels. The `BASLAT_5_EK_*.bat`
helper (§4) was **not** used. This deviates from §4 ("no AI offsets"); the coordinator cannot verify the declaration.

**Submissions (SHA-256 of the files as received):**
- first: Burak `e80c46662d99c2529214a45e2fd6b6280e8e3e93d59b077cf442153b00181f0e`, Enes `af9e01dda199a1b4bfc13d6dd444aa3739b7b467e9ad87c6fab3940c0bfd8fa2`
  (both `status: LABELED`, no `reviewer_id`; otherwise schema-valid except the offset in Enes's file below)
- revised: Burak `3b32b43b2d0646a87de1847ec9c07819f12f6126e35aec598170ffdf449e5a95` (24 records with changed spans, 6 shared),
  Enes `d0083cad4e3525b93275c59677c284ae32048b85282e1bc53ebbe9267801cc64` (17 records, 4 shared)

**Exposure before revision:** between the two submissions the coordinator's chat message showed both reviewers' label
counts and that 59 of the 80 shared records had identical span sets in a pre-count (the coordinator saw this
pre-count while checking the files; it is not the frozen score). Revisions were therefore made after this exposure.

**Rule applied (same as the test-363 freeze: agreement only from the first blind files):**
- **Agreement (§5.1) is computed once from the FIRST submissions** on the 80 shared records, after only mechanical
  fixes: `status` → `ANNOTATED`, `reviewer_id` added, and one offset.
- **The REVISED files are the reviewers' positions for gold v1.2**: solo records take the revised labels (then the
  §5.3 rule scan); shared-record differences between the two revised files go to the joint decision (§5.2).
- Mechanical offset fix, owner-confirmed, applied to both of Enes's versions: `SGD-a5ef1678f12cecfdbe` `"3"`
  [35,36] → [57,58] (the offset tool returned the "3" inside "5:30"; it overlapped the `5:30 in the evening` span).
- Logged in `data/annotations/d3_ext_v0.1/D3_EXT_STAGE_LOG.json`.

## 9. Amendment E3 — blind cross re-annotation of the 320 single-annotated records (2026-10-30, before round 2)

Owner decision (own quality decision, not an instructor requirement): every D3-EXT record becomes double-blind.

- **Packets** (`scripts/build_ext2_packets.py`): Burak gets Enes's 160 solo records, Enes gets Burak's 160, copied
  from the original blind packets (UNLABELED), order reshuffled per reviewer. Launchers `BASLAT_6_EK2_A.bat` /
  `BASLAT_6_EK2_B.bat`; outputs `reviewer_*_EK2_filled.jsonl`.
- **Declaration before round 2 (owner, also for Burak, relayed):** neither reviewer has looked at the other's labels.
  Coordinator's record: the owner received and forwarded Burak's filled files, so he had access to them; this is
  stated as a limitation, not as proof of viewing.
- **Same rules as §4 and E2:** guideline v0.2.3; no discussion, no access to the other's files, gold v1.2 or private
  indexes; AI for translation only — any offset/JSON help is declared before scoring, and only the **first** submission
  is scored.
- **Agreement:** computed once with `annotation_agreement.py` on the 320 records, round-2 first submission vs the
  original annotator's **revised** file (the version in gold v1.2), and frozen before any decision. Reported next to
  the 80-record shared agreement (0.8625), never merged into it.
- **Disposition:** identical → unchanged; differing → both reviewers decide separately, then jointly where they differ
  (A = original annotator, B = round-2 annotator, D = other); no joint agreement to change ⇒ the gold v1.2 record stays.
  Result: **gold v1.3**, built from gold v1.2 + these decisions only; segment labels change from
  `ext_single_annotation_*` to `ext_cross_double_blind_*`.
