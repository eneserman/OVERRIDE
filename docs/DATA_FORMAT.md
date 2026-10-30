# 14 — Data Contracts and File Formats

## Sources
- `data/upstream/sgd/{train,dev,test}/dialogues_*.json` only if available and unchanged; actual files/commit hashes must be recorded.
- `data/annotations/pilot_v0.1/annotator_A_UNLABELED.jsonl`, B: independent packets; not gold.
- `data/gold/override_gold_vX.jsonl`: **does not exist until real adjudication**.

## Pilot reviewer packets versus canonical records
Sampler emits `example_id`, `current_user_utterance` and an `annotation` object whose `value_spans` and `cue_spans` start as `null`. Actual reviewers fill **both** nested lists (empty list means reviewed negative) and set `annotation.status=ANNOTATED`. The `normalize_review_packet.py` command maps these into canonical `id`, `value_spans`, `cue_spans` root keys as *non-gold independent reviewer outputs*. The `annotation_agreement.py` helper compares A and B. Only **human adjudication** can set `ADJUDICATED` and create gold.

## Canonical adjudicated example schema (minimum)
```json
{
 "id":"EXAMPLE-001",
 "source":{"dataset":"SGD","split":"train","dialogue_id":"d1","turn_index":4,"service":"Flights_1"},
 "dialogue_family_id":"d1",
 "history":[{"speaker":"USER","utterance":"Two people to Berlin on Friday."}],
 "current_user_utterance":"Actually Paris, but keep Friday.",
 "value_spans":[{"start":9,"end":14,"text":"Paris","label":"NEW_VALUE"},{"start":25,"end":31,"text":"Friday","label":"KEPT_VALUE"}],
 "cue_spans":[{"start":0,"end":8,"text":"Actually","label":"UPDATE_CUE"},{"start":20,"end":24,"text":"keep","label":"KEEP_CUE"}],
 "transitions":[],"links":[],"difficulty":"L2",
 "annotation":{"status":"ADJUDICATED","guideline_version":"v0.1","reviewers":["reviewer_A","reviewer_B"],"adjudication_log_id":"sample-documented"}
}
```
**Note:** This is a crafted *synthetic example* for schema testing, not a real SGD annotation. The offsets must be verified by code (and adjusted if validation fails); never include it in gold metrics.

## Controlled vocabularies
Layer VALUE: NEW_VALUE, OLD_VALUE, KEPT_VALUE, REFERENCE. Layer CUE: UPDATE_CUE, CANCEL_CUE, KEEP_CUE, RESTORE_CUE. `O` and BIO expansions are computed at tokenization time. Operations: ADD, UPDATE, DELETE, KEEP, RESTORE, CANCEL_INTENT, UNRESOLVED. No implicit span label for invisible actions.

## Model prediction JSONL
One record/example: `id`, `value_spans`, `cue_spans`, `model_run_id`; each span `[start,end,label]`. Predictions do not carry `annotation.status`, and evaluation checks every prediction ID matches exactly one gold ID. Inputs at inference are text/history only.

## Required metadata
- dataset source URL + commit hash, original file SHA-256;
- cleaning script/version, annotation guideline version, reviewer agreement, adjudication log;
- split manifest SHA-256, model checkpoint hash/version, tokenizer alignment strategy;
- permitted licensing/provenance before publication.

## Validation policy
All text slicing must match stored surfaces, text never silently re-normalized. Unknown label => fail; duplicate example ids => fail; same-layer span overlap => fail; future context turn => fail when source indices supplied; links to absent history => unresolved/error. Gold status not implicit.

## v0.6 stricter validated provenance

Canonical gold MUST include `source.dataset="SGD"`, `source.split="train"`, nonempty service/dialogue ID, nonnegative `source.turn_index`, `dialogue_family_id` equal to official source dialogue ID, plus `annotation.reviewers` with at least two distinct real reviewer identifiers and a nonempty `annotation.adjudication_log_id`. Evidence of actual independent reviews and resolution logs must be retained separately; **strings alone never prove human work**. If `history[].turn_index` is present, every history entry must provide it in strict increasing order below the current turn index.

The frozen gold manifest includes `gold_content_sha256` and per-split gold label supports. The final evaluator refuses changed gold, altered partition manifests, extra train predictions, or missing test predictions.
