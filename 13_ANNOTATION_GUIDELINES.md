# 13 — Human Annotation Manual (Draft v0.2, 2026-10-28)

**Status:** Draft v0.2 — updated with **measured D0 evidence** from the real SGD train audit (16,142 dialogues; see `reports/D0_D1_FACTUAL_FINDINGS.md`). Taxonomy narrowed per decision log in `11_RISKS_AND_DECISIONS.md`. **NOT frozen:** finalize only after the D2 pilot and reviewer feedback.

**Use only after D0/D1 feasibility evidence and review. Current taxonomy is provisional.** This is for reviewers, not an automatic label generator.

## Context visible to reviewer
Full relevant **past** USER/SYSTEM messages + current USER utterance, original unmodified text. Never future turns; hide sampling heuristics and current SGD state. Each example has unique `id`, source ids, service if known. Two reviewers work independently before adjudication.

## Reviewer quick-start — how to fill your packet (D2 pilot, 100 items)

**Setup (owner coordinates):**
1. Two reviewers get **one file each**: `data/annotations/pilot_v0.1/annotator_A_UNLABELED.jsonl` (reviewer A) and `annotator_B_UNLABELED.jsonl` (reviewer B). The files are identical; that is intended. **Do not open the other reviewer's file and never open `PRIVATE_sampling_manifest.jsonl`** (it contains sampling hints that would bias you).
2. Work independently. Do not discuss individual items until both are done. Uncertainty is data: when unsure, annotate your best judgment and record it in `uncertainty_notes`.
3. Each line is one JSON example. **Only edit the `annotation` object and add your `reviewer_id`**; never touch `source`, `history`, `current_user_utterance`, `dialogue_family_id`.

**Per example, fill:**
- `annotation.status`: `"ANNOTATED"` when finished (leave `"UNLABELED"` only for items you truly skip — skipping must be rare and noted).
- `annotation.reviewer_id`: your identifier (real person, e.g. `reviewer_A_eser`).
- `annotation.value_spans` / `annotation.cue_spans`: a **list** (use `[]` when you reviewed and found nothing — `[]` means "reviewed negative"; `null` means "not reviewed"). Each span: `{"start": <int>, "end": <int>, "label": <LABEL>, "text": <exact substring>}`.
- `annotation.transitions`: list of `{"operation": "ADD|UPDATE|DELETE|KEEP|RESTORE|CANCEL_INTENT|UNRESOLVED", "slot": ..., "before": ..., "after": ...}` — only when the utterance supports it. This is a **separate layer**, not BIO.
- `annotation.links`: reference links you can see (`REFERENCE` span → target), else `[]`.
- `annotation.difficulty`: `L1|L2|L3|L4|L5` (see `02_NLP_TASK_DESIGN.md`).
- `annotation.uncertainty_notes`: free text for anything ambiguous.

**Recommended tool:** `python scripts/annotation_entry_helper.py --packet <your file> --reviewer-id <your id> --out <filled file>` walks you through the examples interactively — you type the exact phrase, it computes and verifies the offsets, enforces the label vocabulary and overlap rules, and saves each example as you go (`--resume` continues an interrupted session). Manual editing of the JSONL is still allowed; the rules above are identical either way. The helper reads only your blind packet and generates **no** labels.

**Offset rules (validated strictly by `scripts/validate_annotations.py`):**
- Zero-based, **half-open** `[start, end)`, counted in Python characters of `current_user_utterance` — `utterance[start:end]` must equal your `text` **exactly**.
- Find offsets mechanically, not by counting by eye:
  `python -c "u='Actually, I want it in Paris on Friday.'; print(u.find('Paris'))"` → then `end = start + len('Paris')`.
- Cue spans = **minimal complete cue phrase** ("change", "Actually", "the same"); value spans = **complete mentioned value** ("Paris", "twelve in the afternoon").
- Different layers may overlap (`UPDATE_CUE` over `NEW_VALUE` is fine); **same-layer overlap is not allowed**.
- Never annotate the old value as `OLD_VALUE` unless the user actually **says** it in this utterance.

**Worked example** (real schema demo from `examples/UNREVIEWED_annotation_example.jsonl`, utterance `Actually Paris, but keep Friday.` — synthetic fixture, not gold; spans shown in the packet format you fill):

```json
"annotation": {
  "status": "ANNOTATED",
  "reviewer_id": "reviewer_A_eser",
  "value_spans": [
    {"start": 9,  "end": 14, "label": "NEW_VALUE",  "text": "Paris"},
    {"start": 25, "end": 31, "label": "KEPT_VALUE", "text": "Friday"}
  ],
  "cue_spans": [
    {"start": 0,  "end": 8,  "label": "UPDATE_CUE", "text": "Actually"},
    {"start": 20, "end": 24, "label": "KEEP_CUE",   "text": "keep"}
  ],
  "transitions": [{"operation": "UPDATE", "slot": "city", "before": null, "after": "Paris"}],
  "links": [],
  "difficulty": "L2",
  "uncertainty_notes": ""
}
```
Slice check: `utterance[9:14] == "Paris"`, `utterance[25:31] == "Friday"`, `utterance[0:8] == "Actually"`, `utterance[20:24] == "keep"` — your `text` fields must pass exactly this check. Here the retention of "Friday" has an **explicit** keep word ("keep"), so `KEEP_CUE` is warranted (rule R10). In many real items there is no such word ("Yes, I like the same." → `KEPT_VALUE` only, no `KEEP_CUE`) — those judgment calls are exactly what this pilot measures.

**Time budget:** roughly 1.5–3 minutes per item; ~4–6 hours for 100 items. Do it in two sittings if needed, but never while comparing with the other reviewer.

**When done:** return your file unchanged in structure to the project owner. Next steps (run by the pipeline, not by you): `normalize_review_packet.py` → `annotation_agreement.py` (disagreement report) → **human adjudication** of disagreements → gold validation. Your raw files stay immutable.

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

## Decision procedures for the two hardest distinctions (CTO check 3, 2026-10-28)

### DP-1: refusal / deferral ≠ CANCEL (mined evidence: the CANCEL pool is dominated by refusals)

Ask: **is the user withdrawing or stopping a previously given instruction?**
- "Not now." / "No, not now. Thanks." / "Yes but not now" → **deferral/refusal of a system offer** → NO `CANCEL_CUE`, no transition (or `UNRESOLVED` if a pending instruction is left ambiguous). `[126_00002 t10]`, `[14_00023 t14]`, `[46_00077 t6]`
- "Cancel the hotel booking." / "Forget that, don't book it" → withdraws a prior instruction → `CANCEL_CUE` on the minimal cue + transition `CANCEL_INTENT` (rare in SGD — expect few)
- Third-party cancellation ("my kids cancelled, I only need 2") → the *consequence* is a value change (`party_size` → `NEW_VALUE` if re-stated), NOT a `CANCEL_CUE` (R5)
- Hypothetical/policy questions ("if I decide to cancel…") → nothing to label (R4)
- Negated cancel ("Don't cancel the flight") → `cue_polarity=NEGATED`; zero natural corpus support — diagnostic only (R6)

### DP-2: topic return ≠ value restore (mined evidence: the RESTORE pool is dominated by topic return)

Ask: **is the user reverting a slot/entity to a previously mentioned value, or merely resuming an earlier task/topic?**
- "Back to the bus tickets, I'll need 4 tickets." / "go back and book 3 tickets" / "go back to getting tickets for this" → **task/topic resumption** → NO `RESTORE_CUE`; the values stated are `NEW_VALUE` (or `ADD` if first fill). `[70_00006 t18]`, `[73_00069 t16]`, `[101_00093 t8]`
- "Go back to the earlier flight." / "Actually the first one was better." → re-selects a **previously mentioned value** → `RESTORE_CUE` + transition `RESTORE` (genuine L4 — rare)
- Rule of thumb: restore = the **object of the sentence is a slot value being reverted**; topic return = the object is a **task** ("tickets", "reserving rooms"). If in doubt, label neither and write `UNCERTAIN:` in `uncertainty_notes`.

### Uncertainty marking convention (all cases)
When a case is genuinely ambiguous: annotate your best judgment, set `difficulty`, and start `uncertainty_notes` with **`UNCERTAIN:`** plus the reason. Do this instead of skipping. Post-annotation triage will collect these flags; pre-annotation case flagging is deliberately avoided in blind packets because it would bias reviewers.

### Additional data (Frames) — evaluated, not yet acquired
Microsoft Frames (see `24_EXTERNAL_DATASET_RESEARCH.md`) is the planned external source for enriching true L4/L5 RESTORE cases. Acquisition requires the official portal agreement (`LICENSE_REVIEW_REQUIRED` until then) and any imported examples form a **separate frozen pool** (`lock_prospective_holdout.py --source-release-id`, never mixed with the SGD lock). **Adding new data must never modify the existing locked holdout** (`real_sgd_heldout_lock.json` is immutable).

### Scope note on the two-annotator standard
Two genuinely independent human annotators + adjudication is **our own research standard** (data-quality bar for this project). It is **not** a verified, instructor-mandated P2 requirement — we have no confirmed P2 guideline text to that effect. We keep the standard because annotation quality is the core of the contribution.

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
