# D3-EXT — decisions for the 400 new records (LOCKED 2026-10-30)

**Status: LOCKED, before any test access.** Applies `D3_EXT_PROTOCOL.md` §5.2–§5.4 and amendment E2. Agreement score
is unchanged (frozen: layer-set 0.8625, `D3_EXT_AGREEMENT_FREEZE.json`). Built into gold v1.2 by
`scripts/build_gold_v1_2.py`.

## 1. Decision table (shared records that still differed between the revised files, plus the rule flag)

| # | Record | Burak | Enes | Final |
|---|---|---|---|---|
| S1 | `SGD-2a7fc8f2eac3b42e62` | B | B | **B** |
| S2 | `SGD-361896f9c4d73eae25` | A | A | **A** |
| S3 | `SGD-3713e4d4c2714a5926` | A | A | **A** |
| S4 | `SGD-42dccee119bb562199` | B | A | **B** — joint resolution (below) |
| S5 | `SGD-46fec88e213aa350fa` | A | A | **A** |
| S6 | `SGD-47d6edc31e7c4243e4` | A | A | **A** |
| S7 | `SGD-576dfdb778da768f4f` | A | A | **A** |
| S8 | `SGD-5afe7751820cc4ba43` | B | B | **B** |
| S9 | `SGD-5cea83d03ce71a69a5` | A | A | **A** |
| S10 | `SGD-68ea758990beb3df96` | B | B | **B** |
| S11 | `SGD-7df9cb539887f2433b` | A | A | **A** |
| S12 | `SGD-8d53605ac03a2eed81` | D | D | **D**: `UPDATE_CUE "Actually"` [0-8], `UPDATE_CUE "Change"` [38-44], `NEW_VALUE "1:45 pm"` [57-64] |
| S13 | `SGD-9683f27705af5ad48b` | B | B | **B** |
| S14 | `SGD-b4595e7fb1a64c741f` | A | A | **A** |
| S15 | `SGD-bda5bb84c2e701c6b4` | B | B | **B** |
| S16 | `SGD-c219a5d64ad768094c` | A | A | **A** |
| S17 | `SGD-e34ca1ce46b62c7aa1` | A | A | **A** |
| S18 | `SGD-e499e52b23d1effc75` | A | A | **A** |
| S19 | `SGD-e4d6af27a3a851dc52` | B | A | **B** — joint resolution (below) |
| F1 | `SGD-96f8721d8120084e0d` (Enes solo) | D | D | **D**: remove `RESTORE_CUE "back to"` [47-54]; other spans unchanged |

A = Burak's revised record, B = Enes's revised record.

**S4 / S19 joint resolution (2026-10-30, relayed by Enes in chat):** B for both — `NEW_VALUE "a movie"` [17-24] and
`NEW_VALUE "a dentist"` [21-30] — chosen for consistency with gold v1.1, where `a movie` is labeled NEW_VALUE in 7/8
occurrences and `a dentist` in 8/8. The coordinator supplied these counts; the choice is the reviewers'.

## 2. Gold v1.2 provenance segments (new records only)

| Segment | Records | `annotation.issue_type` |
|---|---|---|
| Double-blind, identical revised spans | 61 | `ext_double_blind_agreed` |
| Double-blind, joint decision (S1–S19) | 19 | `ext_double_blind_joint_decision` |
| Single annotation + mechanical rule scan, no flag | 319 | `ext_single_annotation_rule_scan` |
| Single annotation, rule flag decided jointly (F1) | 1 | `ext_single_annotation_rule_flag_joint_decision` |
| **Total** | **400** | |

The validator requires two reviewer names on every gold row; for the 320 single-annotated rows both names are listed
as the responsible pair, and `decision_reason` states explicitly that the second reviewer did **not** re-check the row
(only the mechanical scan did). Model reports must give these segment counts.

## 3. Gold v1.2 result (built 2026-10-30)

| Item | Value |
|---|---|
| File | `data/gold/train_dev_gold_v1_2.jsonl` (local/gitignored), SHA-256 `cc8efc0fd5102e655cf741ffe7949b869050c9a2147d11eee9731b8bbfbe6362` |
| Rows | 857 = 457 from gold v1.1 (byte-identical rows) + 400 D3-EXT |
| Validator | `--require-gold --allowed-splits train` → PASS |
| Split | `reports/splits/frozen_plan_traindev_gold_v1_2.json`, digest `914750be…540c`; plan = union `D3_TRAIN_DEV_SPLIT_PLAN_V12.json`; **771 train / 86 dev** records (769 / 85 families); the 457 old records keep their partition |
| Label support (all) | NEW_VALUE 758, REFERENCE 181, UPDATE_CUE 197, CANCEL_CUE 6, KEPT_VALUE 3, KEEP_CUE 2, OLD_VALUE 2 |
| Dev support | NEW_VALUE 86, REFERENCE 14, **UPDATE_CUE 20** (was 3), KEEP_CUE 1 |

## 4. Provenance (declared, not verified by the coordinator)

- Both decision sheets were filled separately and returned on 2026-10-30. Burak's sheet carries a typed rationale for
  every item and a "draft / signature pending" header; the reviewers declare all decisions are their own.
- Labels: declared human (amendment E2); AI used for translation, offsets and JSON.
