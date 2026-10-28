# 13 — Human Annotation Manual (Draft v0.1)

**Use only after D0/D1 feasibility evidence and review. Current taxonomy is provisional.** This is for reviewers, not an automatic label generator.

## Context visible to reviewer
Full relevant **past** USER/SYSTEM messages + current USER utterance, original unmodified text. Never future turns; hide sampling heuristics and current SGD state. Each example has unique `id`, source ids, service if known. Two reviewers work independently before adjudication.

## Two independent span layers
VALUE: `NEW_VALUE`, `OLD_VALUE`, `KEPT_VALUE`, `REFERENCE`. CUE: `UPDATE_CUE`, `CANCEL_CUE`, `KEEP_CUE`, `RESTORE_CUE`. Mark minimal complete words for cues, complete mentioned value for values; offsets zero-based exclusive end relative to current USER utterance. Different layers may overlap; overlapping labels in same layer escalate to reviewer (don't overwrite).

## Annotating cases (source language: English)
- `Actually, Paris instead of Berlin`: `Paris` NEW, `Berlin` OLD, `instead of` UPDATE_CUE. Antecedent slot needs prior context; if missing, target unknown.
- `keep Friday`: `keep` KEEP_CUE, `Friday` KEPT_VALUE only if it refers to old date.
- `keep everything else`: `keep` KEEP_CUE; **no invented kept value span**.
- `go back to the first option`: `go back to` RESTORE_CUE, `the first option` REFERENCE; if multiple first options, link unresolved.
- `Don't cancel the flight; cancel the hotel`: text includes negated `cancel` and asserted `cancel`. Label cue boundaries in both if the guidelines allow overt cues; attach `cue_polarity=NEGATED/ASSERTED`, link only asserted cancellation to transition; do not cancel the flight.
- `No, that's wrong`: may express correction without an explicit value; do not fabricate one or the target.
- `What about 6 pm?` after `six in the evening`: note potentially semantically equivalent; do not assume UPDATE.
- System-offered new option selected by USER for first time: likely ADD/SELECT, not necessarily correction.

## Transition/referent layer is separate
`ADD, UPDATE, DELETE, KEEP, RESTORE, CANCEL_INTENT, UNRESOLVED` are **not** additional BIO classes. For each transition, save `(service,slot/intent, before, after, evidence span IDs, context turn target, resolution status)` where supported. Annotator can mark ambiguous/unresolved; do not force a gold state transition.

## Annotation record minimum
`id`, `source`, `history`, `current_user_utterance`, `value_spans`, `cue_spans`, `transitions`, `links`, `difficulty`, `annotation.status`, `guideline_version`, independent reviewer identity; every span has `start`, `end`, `text`, `label`. `ANNOTATED` != `ADJUDICATED`. A record is gold only after 2 reviews and recorded adjudication, unless a documented exception is agreed *before* training.

## Adjudication and review log
For every disagreement: example ID, reviewer A/B raw span set, source context, issue type (`boundary`, `class`, `target`, `polarity`, `ambiguity`), decision and reason. Keep both original annotations immutable. Calculate exact-span agreement and operation agreement; no invented inter-annotator statistics.

## QA checklist
Offsets equal Python slice; no invalid span length; all labels from frozen vocabulary; cue polarity asserted/negated/uncertain where annotated; history links point backward to real message; within-head overlap rejected; no class empty marked as automatically negative; all 100 pilot examples if available labeled independently or documented shortfall. Unresolved cases retained and counted.
