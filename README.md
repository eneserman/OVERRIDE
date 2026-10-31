# OVERRIDE — detecting revisions in multi-turn dialogue

**NLP Project 2 (token classification) · Team Developers**
Adnan Burak Özbay (2309111073) · Enes Erman (2309111066) · Mohammed Firas (2309015722) · İlayda Şenel (2309011159)

Users change their minds mid-conversation: *"Actually, make it 7 pm at the same place."* OVERRIDE labels, token by
token, **which words signal the change** (UPDATE_CUE), **what the new value is** (NEW_VALUE) and **what refers back**
to an earlier turn (REFERENCE). The labels do not exist in any public dataset: we selected 1,220 user turns from Google's
Schema-Guided Dialogue corpus and annotated them ourselves, double-blind. The model is chosen by pre-registered
cross-validation and evaluated **once** on a test set that was hash-locked before any model existed.

## Results (locked prospective test, 363 turns, strict exact-span micro-F1)

| System | VALUE F1 | CUE F1 | S (mean) |
|---|---|---|---|
| Laya zero-shot decision model (JEV alternative), added after D6 | 0.031 | 0.017 | 0.024 |
| B2 surface rules | 0.462 | 0.364 | 0.413 |
| B1 lexicon copy | 0.526 | 0.414 | 0.470 |
| BERT-base, first data version (411 turns) | 0.780 | 0.644 | 0.712 |
| CRF (word, shape and context features) | 0.758 | 0.712 | 0.735 |
| **DeBERTa-v3 3-seed ensemble, no history — selected model** | **0.845** | **0.691** | **0.768** |
| DeBERTa-v3 3-seed ensemble, last 60 words of history — pre-registered comparison | 0.870 | 0.757 | 0.813 |

- Selected by grouped 5-fold CV on 857 turns (CV S 0.860). On CV, dialogue history did not help (−0.005, 95%
  family-bootstrap CI [−0.021, +0.012]); **on the locked test it does** (+0.045, [+0.016, +0.078]). We report the
  model fixed before the test (0.768); the history result is reported as the comparison it was registered as.
  Details: [`reports/D6_TEST_RESULTS.md`](reports/D6_TEST_RESULTS.md).
- Per label on the test (selected model): NEW_VALUE 0.858, REFERENCE 0.821, UPDATE_CUE 0.691 (31 spans).
- Error analysis (CV predictions only): [`reports/ERROR_ANALYSIS_CV.md`](reports/ERROR_ANALYSIS_CV.md).
- **Why span F1, not accuracy:** a tagger that labels nothing gets 87.9% token accuracy on our data and 0 span F1
  ([`reports/metric_justification_cv.json`](reports/metric_justification_cv.json)).
- **JEV alternative:** Laya, an open System-1 decision model, asked about every word zero-shot, scores S 0.053 on the
  train-side records and 0.024 on the test: decision models answer sentence-level questions, not word roles in context
  ([`reports/JEV_ALTERNATIVE.md`](reports/JEV_ALTERNATIVE.md); second test access declared as DEV-003).
- **Synthetic data:** 1,000 AI-written turns on real SGD contexts, quality-checked (0 duplicates or copies, more
  lexical variety than the human data). Added to training they do not help: CV S −0.003 with 240 turns, −0.007
  [−0.024, +0.009] with 1,000 ([`reports/SYNTHETIC_DATA.md`](reports/SYNTHETIC_DATA.md)).

## Task

Each user turn is tagged with two BIO layers over a shared word tokenizer:

| Layer | Labels (claims in **bold**) |
|---|---|
| VALUE | **NEW_VALUE**, **REFERENCE**, OLD_VALUE, KEPT_VALUE |
| CUE | **UPDATE_CUE**, CANCEL_CUE, KEEP_CUE, RESTORE_CUE |

This is not NER: the same phrase ("Friday") is a NEW_VALUE, plain context or part of a REFERENCE depending on the
earlier turns. Eight labels are defined in the guideline; the five with fewer than 10 examples are kept in the data but
excluded from claims (SCOPE-001, decided before the test was opened). Metric: a predicted span counts only if start,
end and label all match (`scripts/evaluate_spans.py`).

## Repository layout

```
├── README.md                 this file
├── LICENSE                   MIT, code
├── DATA_LICENSE.md           CC BY-SA 4.0, data (adapted from SGD) and attribution
├── CHANGELOG.md              dated history of every data and model milestone
├── requirements.txt          pinned versions used for the reported results
├── app/                      live web demo: server.py (FastAPI around the frozen ensembles), static/ page, e2e_check.py
├── contributions/            one file per team member
├── data/
│   ├── raw/                  1,220 selected SGD turns without labels + how to fetch the pinned SGD source
│   ├── gold/                 released annotations: train-side 857, test 363, combined 1,220
│   ├── synthetic/            1,000 AI-written training turns on real SGD contexts (kept apart from gold)
│   └── prospective_holdout/  hash lock of the test turns, created before annotation
├── docs/
│   ├── ANNOTATION_GUIDELINES.md   labeling rules (v0.2.3) with the decision rules added during adjudication
│   ├── DATA_FORMAT.md             record and span schema
│   └── DATA_PIPELINE.md           raw SGD → released gold, step by step
├── reports/                  protocols (written before each step), agreement freezes, decisions, results
│   ├── d6_test/              test metrics, bootstrap intervals and predictions of all six systems
│   └── splits/               frozen split manifests (train/dev plan, full 3-way manifest)
├── scripts/                  every step of the pipeline (table below)
└── tests/                    unit tests (python -m unittest discover -s tests)
```

## Scripts

**Source and selection**

| Script | Purpose |
|---|---|
| `inspect_upstream_provenance.py` | Pin the SGD commit and check its split files |
| `audit_sgd.py` | Read-only audit of SGD (schemas, offsets, slot-state deltas) |
| `mine_sgd_revision_candidates.py` | Scan all train user turns, assign heuristic buckets, sample per bucket (buckets hidden from annotators) |
| `prepare_annotation_pilot.py` | Blind calibration/pilot packets |
| `build_ext_packets.py` | The 400-turn second batch, pre-registered quotas and seed |
| `build_ext2_packets.py` | Cross round: each annotator relabels the other's solo turns blind |
| `lock_prospective_holdout.py` | Select and hash-lock the 363 test turns from official SGD dev/test |
| `export_raw_turns.py` | Write `data/raw/` and verify every text against SGD |

**Annotation, agreement and gold**

| Script | Purpose |
|---|---|
| `annotation_entry_helper.py` | Turn typed span text into character offsets (no label suggestions) |
| `normalize_review_packet.py` | Filled packet → canonical per-annotator records |
| `annotation_agreement.py` | Exact span-set agreement per layer and label |
| `rule_scan_v023.py` | Flag records that may violate a written guideline rule |
| `gold_v1_audit.py` | Blind re-annotation audit of the first single-annotated batch |
| `validate_annotations.py` | Strict schema/offset/overlap validator used by every builder |
| `build_adjudicated_gold.py`, `build_train_gold_v1.py` | Gold v1 (457) from two annotations + joint decisions |
| `build_gold_v1_1.py`, `build_gold_v1_2.py`, `build_gold_v1_3.py` | Later gold versions; untouched rows asserted identical |
| `build_test_reference.py` | Test reference (DEV-001), run once after the model freeze |
| `freeze_gold_splits.py`, `freeze_plan_split.py` | Family-grouped split manifests |

**Models and evaluation**

| Script | Purpose |
|---|---|
| `span_tokenizer.py` | Character-offset word tokenizer shared by all models |
| `d5_prepare_data.py` | Gold spans → word-level BIO tags |
| `d5_run_baselines.py` | B0/B1/B2 surface baselines on the dev split |
| `d5_train_crf.py` | Linear-chain CRF per layer |
| `d5_train_transformer.py` | First transformer (shared encoder + two token heads), dev-split selection |
| `d5v2_cv.py` | Grouped 5-fold CV for one configuration (encoder × history × loss), pooled out-of-fold scoring |
| `d5v2_bootstrap.py` | Family-bootstrap 95% interval for the difference of two systems |
| `d5v2_final.py` | Train the final seeds on all 857 turns; ensemble prediction by softmax averaging |
| `d6_baselines.py` | Fit B1, B2, CRF on all 857 turns and predict the test |
| `d6_infer_frozen.py` | Predict with the first BERT checkpoint |
| `evaluate_spans.py` | Strict exact-span evaluator (per label, micro, macro) |
| `evaluate_frozen_test.py` | The only test scorer: re-verifies gold hash, manifest digest and family separation |
| `error_analysis.py` | Boundary / label / missed / spurious error taxonomy |
| `metric_justification.py` | Token accuracy vs strict span F1 for an all-O tagger and real predictions |
| `jev_alt_laya.py` | JEV alternative: Laya decision model asked about every word, zero-shot (`select` / `predict`) |
| `synth_contexts.py` | Sample real SGD contexts for the synthetic-data experiment (gold and test dialogues excluded) |
| `build_synthetic.py` | Build the declared synthetic set from AI-written turns; offsets, duplicate/copy checks, diversity report |
| `demo.py` | Label a sentence (and optional earlier turns) from the command line |

## Reproduce

Python 3.13, an 8 GB GPU for the transformers (CPU works, slowly).

```bash
pip install -r requirements.txt
python -m unittest discover -s tests            # 100+ tests, standard library only

# data (optional: re-verify the released turns against SGD)
git clone https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd
git -C data/upstream/sgd checkout e852981ae34990f4358979625854259302feaa78
python scripts/export_raw_turns.py --gold data/gold/train_dev_gold_v1_3.jsonl data/gold/test_reference_v1.jsonl \
  --out data/raw/sgd_turns_unlabeled.jsonl --sgd-root data/upstream/sgd

# model selection (one run per configuration; reports/D5V2_PROTOCOL.md lists all eight)
python scripts/d5v2_cv.py --gold data/gold/train_dev_gold_v1_3.jsonl --model microsoft/deberta-v3-base \
  --history no --loss plain --outdir reports/train_runs/d5v2_cv

# final model: seeds 20261029, 20261030, 20261031
python scripts/d5v2_final.py train --gold data/gold/train_dev_gold_v1_3.jsonl --model microsoft/deberta-v3-base \
  --history no --loss plain --epochs 6 --seed 20261029 --outdir reports/train_runs/d5v2_final/no

# test predictions and the frozen scorer
python scripts/d5v2_final.py predict --checkpoints reports/train_runs/d5v2_final/no/final_seed20261029.pt \
  reports/train_runs/d5v2_final/no/final_seed20261030.pt reports/train_runs/d5v2_final/no/final_seed20261031.pt \
  --input data/gold/test_reference_v1.jsonl --out reports/train_runs/d6/pred_deberta_v2_ens_hno.jsonl
python scripts/evaluate_frozen_test.py --full-gold data/gold/full_gold_v1_3_plus_test.jsonl \
  --manifest reports/splits/frozen_full_manifest_v1_3.json --accept-consensus-reference \
  --test-predictions reports/train_runs/d6/pred_deberta_v2_ens_hno.jsonl --out reports/d6_test/metrics_check.json

# demo (command line)
python scripts/demo.py --text "Actually, make it 7 pm at the same place." --checkpoints "reports/train_runs/d5v2_final/no/*.pt"

# demo (web app, http://localhost:8000): words, model tokens, per-seed confidence, spans, locked-test benchmark
python app/server.py --checkpoints-no "reports/train_runs/d5v2_final/no/*.pt" \
  --checkpoints-history "reports/train_runs/d5v2_final/tail60/*.pt"
python app/e2e_check.py --url http://localhost:8000   # 59 browser checks of every page and control (Playwright)
```

Checkpoints (6 × 0.7 GB) are not in the repository; their SHA-256 hashes are in `reports/D5V2_RESULTS.md`, and the
training commands above regenerate them. The released predictions in `reports/d6_test/predictions/` let anyone
re-score the test without a GPU.

## Research integrity

- **Pre-registration:** each protocol (`reports/D3_EXT_PROTOCOL.md`, `reports/D5V2_PROTOCOL.md`, …) was committed before
  the step it governs; git timestamps are the evidence.
- **Locked test:** the 363 test turns were hash-locked before annotation, annotated blind by both annotators, and opened
  once (`reports/TEST_ACCESS_LOG.md`) after the model freeze was committed and pushed.
- **Agreement** is always computed from first submissions and frozen before any decision
  (`reports/*AGREEMENT_FREEZE.json`).
- **Deviations** are recorded, never applied silently (`reports/PROTOCOL_DEVIATIONS.md`): DEV-001 consensus test
  reference, SCOPE-001 claim scope, DEV-002 family key across SGD splits, DEV-003 second test access for the added
  Laya row.
- **AI use (declared):** translation, character-offset computation, JSON formatting and coding assistance. Every
  label in `data/gold/` and every adjudication decision was made by the annotators. The only AI-written data is
  `data/synthetic/`, marked `SYNTHETIC_AI` in every record and used only in the experiment of `SYNTHETIC_DATA.md`.

## License and citation

Code: MIT (`LICENSE`). Data: CC BY-SA 4.0, adapted from Google SGD (Rastogi et al., AAAI 2020) — see `DATA_LICENSE.md`.
