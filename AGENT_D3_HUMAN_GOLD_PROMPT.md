# AGENT D3 — Independent Human Annotation & Adjudication Facilitation

**Prerequisites:** real D0 source audit, D1/D2 blind packets, owner GO, versioned annotation guideline. If any absent, stop with BLOCKED. **An AI agent cannot falsely claim to be two independent human annotators.**

1. Supply blinded A and B packets to two *actual* reviewers. Do not show `PRIVATE_sampling_manifest`, heuristic suggestions, gold SGD state, or each other's decisions.
2. Provide data entry helper only: span offsets `[start,end)`, surface matches, allowed vocabulary, cue polarity, history links, ambiguity rationale; humans supply labels.
3. Import each returned, separately authored annotation dataset without modification. Record IDs, reviewer pseudonyms, guideline version and source provenance.
4. **Format reconciliation (non-gold):** The sampler writes `example_id` and nested `annotation.value_spans`/`annotation.cue_spans`. After each REAL human reviewer fills both nested arrays and sets `annotation.status=ANNOTATED`, run:
   `python scripts/normalize_review_packet.py --input <annotator_A_filled.jsonl> --out <reviewer_A_normalized.jsonl> --reviewer-id <actual_id>` (repeat for B). This maps `example_id`→`id` and moves span lists into the canonical root, **without** creating gold. Keep originals immutable.
5. Run `python scripts/annotation_agreement.py --a <reviewer_A_normalized.jsonl> --b <reviewer_B_normalized.jsonl> --out <agreement.json>` and inspect exact span-level disagreements; create discrepancy report with real example IDs. Preserve both raw annotation versions and logs.
6. Adjudicator (actual reviewer) resolves each disagreement using `13_ANNOTATION_GUIDELINES.md`, including negation/cancellation cases. Do not auto-adjudicate based on a model suggestion.
7. Build `data/gold/override_gold_v*.jsonl` **only** when fully human-adjudicated, then validate with `--require-gold`; retain hidden gold test labels until freeze.
8. Report per-class support, true negatives, unresolved cases, agreement denominators and human labor estimate. Recommend `GO / NARROW / NO-GO` for rare classes.
9. STOP. Never train a model and never claim `RESTORE`/L5 learned if not supported by gold.
