# 05 — System Architecture (CLI-first)

**Status:** designed, not deployed. **Primary assessed artifact:** reproducible Python project, public GitHub repository, PPTX. No website/mobile app.

## Scientific boundaries
1. **Input** at prediction time: current USER message; optional strictly earlier USER/SYSTEM turns and optional *previously predicted* state. Never current-turn `frames[].state`, future messages, gold spans or adjudicator notes.
2. **Primary supervised output:** two independently scored token/span layers: VALUE (`NEW_VALUE`, `OLD_VALUE`, `KEPT_VALUE`, `REFERENCE`) and CUE (`UPDATE_CUE`, `CANCEL_CUE`, `KEEP_CUE`, `RESTORE_CUE`). Labels are **provisional until human feasibility review**.
3. **Secondary:** links to earlier mentions and dialogue-state transitions (`ADD`, `UPDATE`, `DELETE`, `KEEP`, `RESTORE`, `CANCEL_INTENT`, `UNRESOLVED`). Report separately, only where real transition gold exists.
4. **Level:** L1–L5 are diagnostic strata, not a claim that SGD has complete L4/L5 training labels.

## Dataflow
```
raw SGD (pinned hash, unmodified)
  -> scripts/audit_sgd.py -> empirical report (NOT gold)
  -> scripts/prepare_annotation_pilot.py -> blinded A/B queues + private sampling log
  -> independent HUMAN annotation -> adjudication -> validated GOLD JSONL
  -> dialogue-family split freeze -> tokenizer alignment -> train baseline/CRF/Transformer
  -> frozen evaluation -> confusion/error/robustness reports
  -> Python CLI prediction over example conversations -> PPTX evidence + public repo
```
Every arrow has provenance and failure logs. Training is blocked until gold is validated and sufficient class support measured.

## Modules, responsibilities and contracts
| Module | Entry point | Required artifact / action | Status |
|---|---|---|---|
| Source audit | `scripts/audit_sgd.py` | Source hashes, state-change candidates, offset diagnostics | Code present, real SGD not run |
| Annotation candidate sampling | `scripts/prepare_annotation_pilot.py` | Blind packets A/B and private hints | Code present, real SGD not run |
| Review packet normalization/agreement | `scripts/normalize_review_packet.py`, `scripts/annotation_agreement.py` | Canonical A/B drafts, disagreement report; **never gold** | Code present, synthetic tests |
| Annotation validation | `scripts/validate_annotations.py` | Validated offsets, overlaps, labels, provenance | Code present, tests synthetic |
| Frozen dataset split | `scripts/freeze_gold_splits.py` | Immutable group split manifest and hash | Code present, tests synthetic |
| Strict score engine | `scripts/evaluate_spans.py` | Micro/macro span F1 for separately reported layers | Code present, tests synthetic |
| Model training | `src/override/` future module | Inference checkpoints and predictions | NOT IMPLEMENTED |
| Terminal inference | `scripts/predict.py` future CLI | Real model spans and provenance | NOT IMPLEMENTED |

No production API/frontend is necessary. Do not ship an impressive-looking fake classifier: a rule example must be visibly labeled `RULE_BASELINE`, not a trained result.

## Serving interface design (for later implementation)
```json
{"dialogue_id":"demo-001","history":[{"speaker":"USER","utterance":"Paris on Friday for two"}],"current_user_utterance":"Actually make it three; keep Friday.","model_id":"TO_BE_FILLED_AFTER_TRAINING"}
```
Output: `value_spans`, `cue_spans` with exclusive-end character offsets; `transitions` only if resolver implemented; `warnings` for unresolved/ambiguous; model/hash metadata. Never silently alter user text to make offsets pass.

## Failure modes
- Empty spans/unknown class: reject with actionable error.
- Same-head overlap: error pending adjudication; two-head overlap permitted.
- History too long: preserve entire current message; deterministic history truncation and count truncated turns.
- `KEEP` absent explicit value: cue may exist without value span; preservation stored in state layer.
- Ambiguous prior referent: abstain/`UNRESOLVED`, never invent.
- Same string used by two services: resolve via explicit `(service, slot)` or mark unknown.

## Dependencies / reproducibility
Python 3.10+; standard-library audit and validation tools work without ML dependencies. Lock actual model/tokenizer versions in an environment lock **when training begins**, document operating system and GPU/CPU, seeds, precision and run commands. Paths relative to project root. Never put personal tokens in logs.

**v0.6 note:** `scripts/evaluate_spans.py` is a diagnostic engine; `scripts/evaluate_frozen_test.py` is the only permitted final-test entry point, verifying gold-hash and train/dev/test partition integrity.
