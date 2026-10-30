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
