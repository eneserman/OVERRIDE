# 13 — Human Annotation Manual (Draft v0.2, 2026-10-28)

**Status:** Draft v0.2 — updated with **measured D0 evidence** from the real SGD train audit (16,142 dialogues; see `reports/D0_D1_FACTUAL_FINDINGS.md`). Taxonomy narrowed per decision log in `11_RISKS_AND_DECISIONS.md`. **NOT frozen:** finalize only after the D2 pilot and reviewer feedback.

**Use only after D0/D1 feasibility evidence and review. Current taxonomy is provisional.** This is for reviewers, not an automatic label generator.

## Context visible to reviewer
Full relevant **past** USER/SYSTEM messages + current USER utterance, original unmodified text. Never future turns; hide sampling heuristics and current SGD state. Each example has unique `id`, source ids, service if known. Two reviewers work independently before adjudication.

## Two independent span layers
VALUE: `NEW_VALUE`, `OLD_VALUE`, `KEPT_VALUE`, `REFERENCE`. CUE: `UPDATE_CUE`, `CANCEL_CUE`, `KEEP_CUE`, `RESTORE_CUE`. Mark minimal complete words for cues, complete mentioned value for values; offsets zero-based exclusive end relative to current USER utterance. Different layers may overlap; overlapping labels in same layer escalate to reviewer (don't overwrite).

## Evidence-based disambiguation rules (D0, measured on 164,982 real user turns)

These rules come from inspecting real unreviewed SGD train text (examples below are **unreviewed source text**, not gold). They resolve the highest-frequency ambiguity classes observed in the corpus:

| # | Observed pattern (real frequency) | Correct handling | Real example (unreviewed SGD train) |
|---|---|---|---|
| R1 | Bare "No"-prefixed answers — **11,460 of 14,308** revision-regex hits (~80% FP) | **NOT** a revision; label no cue | `[1_00001 t24] "No, Thanks"`, `[1_00006 t16] "No, that is all."` |
| R2 | Explicit revision words (actually/instead/rather/change/switch/replace) — **2,462 turns** | genuine `UPDATE_CUE` pool; annotate minimal cue phrase | `[1_00008 t16] "No, change the time to 7 pm and for one person only."` |
| R3 | Alias-set expansions in state (`'17:15' -> '17:15|5:15 pm'`) — 24,326 candidates | **meaning unchanged**: `NO_CHANGE` control, or `KEPT_VALUE` if the user re-confirms; never `UPDATE_CUE` | `[1_00003 t10] "Yes, that works for me. How pricey are they?"` |
| R4 | Refund/policy hypotheticals ("if I decide to cancel") | **NOT** `CANCEL_CUE` — no instruction is being revised | `[16_00092 t6] "Can I get a refund for the ticket if I decide to cancel?"` |
| R5 | Third-party cancellation ("my mother-in-law canceled, so I only need two") | **NOT** `CANCEL_CUE`; the consequent value change (`party_size`) is `NEW_VALUE` only if re-stated; implicit revision, no cue unless explicit change language | `[3_00091 t4] "No, I forgot, my mother-in-law canceled, so I only need reservations for two"` |
| R6 | Negated cancel ("Don't cancel…") — **0 of 164,982 turns in corpus** | keep `cue_polarity=NEGATED` rule below; this construct is **diagnostic-only**, never expected in training mass | (no natural corpus instance; synthetic guideline example only) |
| R7 | Travel-sense "back to / original / previous" — 187 of 208 restore-regex hits | **NOT** `RESTORE_CUE` | `[19_00097 t10] "I need to head back to Chicago on the 9th"` |
| R8 | Genuine restore = re-selecting a previously mentioned entity/option | `RESTORE_CUE` (rare, diagnostic stratum) | `[36_00079 t4] "I want to go back to Dr. Hamblin Basil again."` |
| R9 | Discourse "keep going / keep looking" | **NOT** `KEEP_CUE` | `[2_00033 t12] "Okay, let's keep looking then."` |
| R10 | Explicit retention ("I like the same", "prefer the same") | `KEPT_VALUE` (+`KEEP_CUE` only if an explicit keep phrase heads the value) | `[1_00013 t4] "Yes, I like the same."` |
| R11 | First-observed slot fill for a service — 29,642 frames | `ADD` transition, `NEW_VALUE` span; **not** a correction, no `UPDATE_CUE` | `[1_00000 t2] "I would like for it to be in San Jose."` |
| R12 | "previous X" inside a *new* specification is a revision, not a restore | `UPDATE_CUE` on the cue phrase; value is `NEW_VALUE` | `[1_00093 t12] "Instead of the previous time, can you make it at 18:00?"` |

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
