# D3-EXT round 2 — decisions and gold v1.3 (LOCKED 2026-10-30, before any test access)

**Status: LOCKED.** Applies amendments E3/E4 of `D3_EXT_PROTOCOL.md`. The frozen round-2 agreement is unchanged
(layer-set 0.805, `D3_EXT2_AGREEMENT_FREEZE.json`).

## 1. How the 320 cross-annotated records were disposed

| Disposition | Records | `annotation.issue_type` |
|---|---|---|
| Round 2 identical to the original annotator | 204 | `ext_cross_double_blind_agreed` |
| Different; both separate decision sheets gave the same span set | 101 | `ext_cross_double_blind_decision` |
| Different; resolved at the joint step | 11 | `ext_cross_double_blind_joint_decision` |
| Different; no joint agreement → gold v1.2 kept (K8, K23, K27, K44) | 4 | `ext_cross_double_blind_no_agreement_v1_2_kept` |
| **Total** | **320** | |

59 records change spans relative to gold v1.2. The final span sets are in the local file
`data/annotations/d3_ext_v0.1/D3_EXT2_FINAL_DECISIONS.json` (SHA-256 `8e7df6f0da20179e32695586ea0925df59a595097830c748bec514d62da57c35`),
kept out of git with the rest of the gold content.

**Joint step (16 records that differed after the separate sheets):** two proposal sheets (one filled by Burak, one by
Enes) and two final records (`D3_EXT2_ORTAK_16_SON_KARAR_KAYDI.md`, `…_SON_DURUM.md`) agree on the same outcome: 12
records resolved (K19 and K107 had different boxes but identical span sets, counted as separate-sheet agreement), 4
left to the default rule. No signatures were collected; the decisions were relayed by Enes.

**K96 (`SGD-96f8721d8120084e0d`) reverses the earlier F1 decision:** `RESTORE_CUE "back to"` [47-54] is kept. The
round-2 sheet showed three context turns, in which the system had proposed "March 2nd" earlier; with the earlier
two-turn view the reviewers had removed it. UPDATE_CUE is now `change` [23-29].

## 2. Gold v1.3

| Item | Value |
|---|---|
| File | `data/gold/train_dev_gold_v1_3.jsonl` (local), SHA-256 `ce7b9a054138b48f1bbc18544ccc7374ed7b05e9196048317feb072fa8a39dbc` |
| Builder | `scripts/build_gold_v1_3.py` (fail-closed: unchanged records asserted equal to gold v1.2; decided spans checked against the text; rows outside the 320 must be byte-identical) |
| Validator | `--require-gold --allowed-splits train` → PASS, 857/857 |
| Split | `reports/splits/frozen_plan_traindev_gold_v1_3.json` (digest `4f810ab8…80ef`), same plan and **identical membership** to v1.2: 771 train / 86 dev |
| Label support | NEW_VALUE 764, REFERENCE 189, UPDATE_CUE 226, CANCEL_CUE 7, KEPT_VALUE 3, OLD_VALUE 3, KEEP_CUE 2, RESTORE_CUE 1 |
| Dev support | NEW_VALUE 86, REFERENCE 14, UPDATE_CUE 26, CANCEL_CUE 1, KEEP_CUE 1 |

## 3. Provenance of gold v1.3 (for every model report)

| Segment | Records | Evidence |
|---|---|---|
| Gold v1 pilot / calibration / double sets | 100 | double-blind + joint adjudication |
| Gold v1 single + non-blind verification (3 changed in v1.1) | 357 | audited: 48-record blind re-annotation, agreement 0.458 |
| D3-EXT shared | 80 | double-blind, agreement 0.8625, joint decisions |
| D3-EXT cross round | 320 | double-blind (round 1 + cross round 2), agreement 0.805, decisions above |

AI use (declared, E2/E4): translation, offsets and JSON writing; labels and decisions are the reviewers'.
