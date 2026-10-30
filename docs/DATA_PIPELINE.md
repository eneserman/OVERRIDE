# Data pipeline — from raw SGD to released gold

Every step is a script in `scripts/`; every step that creates data checks its input and refuses to overwrite its
output. Protocols were committed before the step they govern (see `reports/`).

```
SGD (pinned commit) ─► audit ─► mine candidate turns ─► blind packets ─► 2 independent annotations
      │                                                                        │
      └─► holdout pool (official dev/test) ─► hash lock ─► blind packets ──────┤
                                                                               ▼
                         normalize ─► agreement (frozen on first submissions) ─► joint decisions
                                                                               ▼
                    build gold (fail-closed) ─► validate ─► freeze splits ─► export raw turns
```

## 1. Source and audit

| Step | Script | Output |
|---|---|---|
| Pin and check upstream | `inspect_upstream_provenance.py` | `reports/V08_UPSTREAM_PROVENANCE.json`, `reports/SHA256_SGD_TRAIN_FILES.txt` |
| Read-only audit of 16,142 train dialogues (schemas, offsets, state deltas) | `audit_sgd.py` | `reports/D0_D1_FACTUAL_FINDINGS.md` |

## 2. Selecting user turns (cleaning = keeping only turns that can carry a revision, with their past context)

| Step | Script | What it does |
|---|---|---|
| Mining | `mine_sgd_revision_candidates.py` | Scans every user turn of official `train` (164,982 turns), assigns one of 8 heuristic buckets (UPDATE, MIXED, CANCEL, KEEP, RESTORE, REFERENCE, HARD_NEGATIVE, NO_CONTEXT) and samples per bucket with a fixed seed. Buckets stay in a private file; annotators never see them. History = earlier turns only. |
| Pilot packets | `prepare_annotation_pilot.py` | First 100 blind turns for calibration. |
| New batch (400) | `build_ext_packets.py` | Pre-registered quotas and seed (`reports/D3_EXT_PROTOCOL.md`); excludes every family already used or locked. |
| Prospective test | `lock_prospective_holdout.py` | 363 turns / 358 families from official `dev`+`test`; SHA-256 lock of every text before annotation (`data/prospective_holdout/`). |

## 3. Annotation and agreement

| Step | Script | What it does |
|---|---|---|
| Entry helper (optional) | `annotation_entry_helper.py` | Turns typed span text into offsets; never suggests labels. |
| Normalize | `normalize_review_packet.py` | Filled packet → canonical per-reviewer records; checks offsets against the text. |
| Agreement | `annotation_agreement.py` | Exact span-set agreement per layer and per label, computed once on first submissions and frozen (`reports/*AGREEMENT_FREEZE.json`). |
| Rule scan | `rule_scan_v023.py` | Flags records that may break a written guideline rule; decides nothing. |
| Audit of old gold | `gold_v1_audit.py` | Blind re-annotation of a random sample of the single-annotated records. |
| Cross round | `build_ext2_packets.py` | Gives each reviewer the other reviewer's solo records, blind. |

## 4. Building gold

| Version | Script | Content |
|---|---|---|
| v1 (457) | `build_adjudicated_gold.py`, `build_train_gold_v1.py` | pilot + double sets adjudicated, single set verified |
| v1.1 | `build_gold_v1_1.py` | 3 audit fixes |
| v1.2 (857) | `build_gold_v1_2.py` | + 400 new records |
| **v1.3 (857)** | `build_gold_v1_3.py` | all 400 new records double-blind |
| **test reference (363)** | `build_test_reference.py` | DEV-001 consensus, built once after the model freeze |

Every builder asserts that untouched records are byte-identical to the previous version, checks every span against the
text and ends with `validate_annotations.py --require-gold`.

## 5. Splits and export

- `freeze_plan_split.py`: train/dev split by dialogue family from a pre-committed plan (771 / 86).
- `scripts/d5v2_cv.py` uses 5 folds by family instead of the fixed dev split (`reports/D5V2_PROTOCOL.md`).
- `export_raw_turns.py`: writes `data/raw/sgd_turns_unlabeled.jsonl` and re-checks every text against SGD.

## 6. Model input preparation

- `span_tokenizer.py`: one character-offset word tokenizer shared by every model.
- `d5_prepare_data.py`: gold spans → word-level BIO tags for the two heads; spans that do not align to word
  boundaries are reported (0 in gold v1.3).
- Transformers align words to sub-tokens by character offsets (`d5v2_cv.encode`); training fails if a labeled word
  has no sub-token.
