# D3 Gold Creation Protocol — train/dev and sealed test (2026-10-28)

**Binding rule:** no file is called "gold" until TWO independent human reviews + documented human adjudication exist. AI drafts (`AI_SIMULATION`) are never converted into human/gold. Every command below is runnable as-is; paths use the prepared packet directories.

## Phase A — train/dev gold (development data)

```bash
# A1. normalize each reviewer's filled packets (format reconciliation, still NOT gold)
python scripts/normalize_review_packet.py --input data/annotations/d3_merged_traindev_v0.1/reviewer_A_filled.jsonl --reviewer-id reviewer_A_ISIM --out data/annotations/d3_merged_traindev_v0.1/reviewer_A_canonical.jsonl
python scripts/normalize_review_packet.py --input data/annotations/d3_merged_traindev_v0.1/reviewer_B_filled.jsonl --reviewer-id reviewer_B_ISIM --out data/annotations/d3_merged_traindev_v0.1/reviewer_B_canonical.jsonl

# A2. independent agreement analysis (example-level + exact-span per class + uncertainty flags)
python scripts/annotation_agreement.py --a data/annotations/d3_merged_traindev_v0.1/reviewer_A_canonical.jsonl --b data/annotations/d3_merged_traindev_v0.1/reviewer_B_canonical.jsonl --out reports/D3_AGREEMENT.json

# A3. HUMAN adjudication meeting: resolve every disagreement (boundary|class|target|polarity|ambiguity),
#     write decisions JSONL (template below) with reasons. Disagreements are data - report them.

# A4. build gold ONLY from human decisions
python scripts/build_adjudicated_gold.py --a data/annotations/d3_merged_traindev_v0.1/reviewer_A_canonical.jsonl --b data/annotations/d3_merged_traindev_v0.1/reviewer_B_canonical.jsonl --decisions data/annotations/d3_merged_traindev_v0.1/adjudication_decisions.jsonl --adjudicator HAKEM_ISIM --log-id ADJ-2026-XXX --allowed-splits train --require-all --out data/gold/override_gold_traindev_v0.1.jsonl

# A5. independent audit of the produced gold
python scripts/validate_annotations.py --input data/gold/override_gold_traindev_v0.1.jsonl --require-gold --report reports/D3_GOLD_VALIDATION.json

# A6. freeze splits on the gold (family-grouped; must respect the PRE-COMMITTED plan)
python scripts/freeze_gold_splits.py --gold data/gold/override_gold_traindev_v0.1.jsonl --out reports/splits/frozen_traindev_v0.1.json --seed 20261028
```

**A6 constraint:** the freeze must be consistent with `reports/D3_TRAIN_DEV_SPLIT_PLAN.json` (454 families → 409 `train_gold` / 45 `dev_gold`, frozen BEFORE annotation). If `freeze_gold_splits` assigns differently, do **not** pick the more favorable one — report the conflict and use the pre-committed plan; changing it after seeing labels is a protocol violation.

## Phase B — sealed test gold (evaluation only)

```bash
# B1-B2: same normalize + agreement flow on data/annotations/d3_test_packets_v0.1/
# B3: separate adjudication for test items (same adjudicator policy, separate log id)
# B4: build test gold - note the split allowance:
python scripts/build_adjudicated_gold.py --a data/annotations/d3_test_packets_v0.1/reviewer_A_canonical.jsonl --b data/annotations/d3_test_packets_v0.1/reviewer_B_canonical.jsonl --decisions data/annotations/d3_test_packets_v0.1/adjudication_decisions.jsonl --adjudicator HAKEM_ISIM --log-id ADJ-2026-TEST-XXX --allowed-splits dev,test --require-all --out data/gold/override_gold_TEST_SEALED_v0.1.jsonl
python scripts/validate_annotations.py --input data/gold/override_gold_TEST_SEALED_v0.1.jsonl --require-gold --allowed-splits dev,test --report reports/D3_TEST_GOLD_VALIDATION.json
```

### Test access control (enforced + auditable)

1. **Sealed location:** `data/gold/*TEST_SEALED*` is gitignored (like all gold); test labels are never committed or published.
2. **Access log:** every opening of the test gold is recorded in `reports/TEST_ACCESS_LOG.md` (date, who, purpose, approver). Permitted purposes: adjudication (B3), validation (B4), and the **single final evaluation** (D6). Forbidden: model selection, prompt work, debugging, error analysis, threshold tuning.
3. **Single final evaluation:** `scripts/evaluate_frozen_test.py` (v0.6 integrity gate) with the full gold + frozen manifest + **test-ID-only** predictions; any train/dev prediction ID aborts.
4. **Violation handling:** if test content/labels influenced development, the affected result is reported as **protocol-violated / exploratory**, not as held-out performance.

## Adjudication decisions template (one JSON per example)

```json
{"example_id": "SGD-...", "value_spans": [{"start": 9, "end": 14, "text": "Paris", "label": "NEW_VALUE"}], "cue_spans": [], "transitions": [], "links": [], "difficulty": "L2", "issue_type": "class", "decision_reason": "reviewer B treated 'that one' as REFERENCE; adjudicated REFERENCE per rule R10 context", "uncertainty_notes": ""}
```

The builder rejects: unknown labels, offsets whose `text` ≠ slice, same-layer overlaps, non-distinct reviewer IDs, examples missing decisions (with `--require-all`), and overwriting existing gold.

## Agreement reporting requirements (CTO protocol item 4)

`reports/D3_AGREEMENT.json` reports, per reviewer pair:
- example-level `exact_layer_set_agreement`,
- **`span_level_agreement_by_label`** (exact-span matched / only-A / only-B / symmetric F1 per label per layer),
- `difficulty_agreement`, `uncertainty_flagged` lists,
- the full `disagreements` list for adjudication.
Report both raw and calibration-excluded statistics (calibration IDs in `data/annotations/d3_calibration_v0.1/calibration_index.json`).

## Class-support honesty rule (CTO risk note)

The pre-committed dev partition (45 families) may contain **no** examples of rare labels (e.g. true `RESTORE_CUE`, `KEEP_CUE`). If so:
- report `support=0 → NOT EVALUABLE` for that class **rather than** hiding it or changing the split;
- never re-balance by moving examples after labels are known;
- overall micro F1 must always be shown with per-class support counts.

## What must NOT happen

- No gold without two real independent human reviews + adjudication.
- No test labels in development; no AI labels as human; no invented metrics.
- No D5 training until Phase A gold is validated and frozen (owner gate).
