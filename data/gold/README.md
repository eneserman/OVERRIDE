# Gold data (released)

| File | Rows | What it is |
|---|---|---|
| `train_dev_gold_v1_3.jsonl` | 857 | Model-development gold from official SGD `train`. SHA-256 `ce7b9a054138b48f1bbc18544ccc7374ed7b05e9196048317feb072fa8a39dbc` |
| `test_reference_v1.jsonl` | 363 | Locked prospective test from official SGD `dev`/`test`, DEV-001 consensus reference |
| `full_gold_v1_3_plus_test.jsonl` | 1,220 | Both files together; the input of `scripts/evaluate_frozen_test.py` with `reports/splits/frozen_full_manifest_v1_3.json` (gold content SHA-256 `8a3e9fd7…c4b4`) |

Each row: the raw fields of `data/raw/sgd_turns_unlabeled.jsonl` plus `value_spans` and `cue_spans`
(`{start, end, text, label}`, character offsets into `current_user_utterance`) and an `annotation` block (status,
guideline version, reviewers, decision provenance). Format: `docs/DATA_FORMAT.md`; rules: `docs/ANNOTATION_GUIDELINES.md`.

## Label counts

| Label | Train-side (857) | Test (363) |
|---|---|---|
| NEW_VALUE | 764 | 315 |
| REFERENCE | 189 | 114 |
| UPDATE_CUE | 226 | 31 |
| CANCEL_CUE | 7 | 0 |
| KEPT_VALUE / OLD_VALUE / KEEP_CUE / RESTORE_CUE | 3 / 3 / 2 / 1 | 3 / 0 / 0 / 0 |

Claims are made for NEW_VALUE, REFERENCE and UPDATE_CUE only (SCOPE-001, `reports/PROTOCOL_DEVIATIONS.md`).

## Provenance

| Segment | Records | How it was labeled |
|---|---|---|
| Pilot, calibration and double sets | 100 | double-blind, joint adjudication |
| First single-annotated batch | 357 | one annotator + second-eye check; blind audit of 48 found agreement 0.458 → 3 records fixed (`reports/D3_GOLD_V1_AUDIT_RESULT.json`) |
| New batch, shared | 80 | double-blind, agreement 0.8625, joint decisions |
| New batch, cross round | 320 | double-blind, agreement 0.805, separate + joint decisions |
| Test | 363 | double-blind (agreement frozen before any model), 300 identical, 3 decided by rule, 60 intersection only |

Labels and decisions were made by the two annotators (reviewer_A_BURAK, reviewer_B_ENES). AI was used for translation,
offset computation and JSON formatting, as declared in `reports/D3_EXT_PROTOCOL.md`.

**Rebuild:** `scripts/build_train_gold_v1.py` → `build_gold_v1_1.py` → `build_gold_v1_2.py` → `build_gold_v1_3.py`
(from the local annotation rounds) and `scripts/build_test_reference.py` (from the two test annotations and the lock).

**License:** CC BY-SA 4.0 (adapted from SGD), see `DATA_LICENSE.md`.
