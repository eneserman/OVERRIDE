# OVERRIDE — NLP Task Design & Annotation Contract

**Project:** OVERRIDE — Context-Aware Instruction Revision & Conflict-Aware Token Classification  
**Group:** Developers | **Course:** NLP Project 2 (Token Classification)  
**Document:** `02_NLP_TASK_DESIGN.md` | **Version:** 0.3 (CLI delivery clarification) | **Status:** DESIGN SPECIFICATION — NOT IMPLEMENTED  
**Language of benchmark:** English (Google SGD baseline corpus). Turkish examples are explanatory only; Turkish generalization is not claimed.

> **Integrity rule:** This document must be read with `01_REQUIREMENTS.md` and `00_DESIGN_AUDIT.md`. It describes proposed methods and expected behavior, not completed model training, newly verified labels, achieved scores, or validated dataset size. All unverified requirements must be confirmed by a pilot before being reported as facts.

## 1. Objective and research hypothesis

**Primary task:** Given the **current user utterance plus conversation history**, predict character/token spans indicating new and rejected values, explicitly retained values, backward references, and revision-related cues. The main evaluation is **token/span classification**, as required by Project 2.

**Secondary task:** Convert predicted spans, dialogue state history, and reference-resolution results into explicit **state transitions**: `ADD`, `UPDATE`, `DELETE`, `KEEP`, `RESTORE`, `CANCEL_INTENT`, or `UNRESOLVED`. The secondary task is scored separately and must not be presented as part of the token model unless experimentally demonstrated.

**Research question:** Does including conversation history improve exact span identification and correct revision interpretation relative to models that see only the latest user message, especially for long-distance references and partially preserved constraints?

**Controlled comparison:** Same train/dev/test dialogues; context-free baseline versus context-aware model; identical annotation protocol; comparable evaluation.

**Non-goals:** General-purpose memory for every chatbot; obeying or executing instructions; real bookings or financial transactions; claiming all conversational contradictions are solvable; treating heuristically derived labels as gold annotations.

## 2. Scope locked with the project owner

| Level | Scenario | Example (illustrative) | Required behavior |
|---|---|---|---|
| L1 | Explicit single-slot replacement | “Not Berlin; Paris.” | Mark rejected/new values and update target slot. |
| L2 | Partial update + preservation | “Make it three people, keep Friday.” | Change count; preserve date. |
| L3 | Cancellation / clearing | “Cancel the hotel booking request.” | Identify cancellation cue and target intent; do not assume other intents are cancelled. |
| L4 | Restore earlier value | “Go back to the first city I mentioned.” | Resolve the backward reference only when a unique historical target exists. |
| L5 | Multiple turns, mixed revisions | “Use the second option but retain the first date.” | Resolve separate references, keep unchanged constraints, flag unresolved links. |

**Important:** L4–L5 are *target challenge sets*, not claims that Google SGD directly annotates them. They require new examples and human-reviewed referent links. Evaluation must report number of examples per level.

## 3. Existing dataset vs original annotation work

### 3.1 Confirmed from official Google SGD documentation

- SGD includes `dialogue_id`, `services`, `turns`, `speaker`, `utterance` and per-service `frames`.
- `frames[].slots` provide **character offsets for non-categorical slot mentions only**: `start`, `exclusive_end`, `slot`.
- User-turn `frames[].state` includes `active_intent`, `requested_slots`, and `slot_values`.
- Categorical slot values may not have a span in `frames[].slots`; their state value must not be fabricated into a token span.
- Non-categorical state `slot_values` may contain multiple equivalent utterance variants, not a strictly canonical single string.
- Original SGD has predefined train/dev/test splits. It does **not** provide our desired gold correction-cue, preservation-cue, RESTORE, or backward-reference labels.

Official source: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue  
Technical representation: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/dstc8.md  
Dataset license: CC BY-SA 4.0 (check original LICENSE and attribution when publishing transformations). The upstream repository was archived in April 2026 and is read-only.

### 3.2 Original Developers contribution (to be implemented)

1. Detect candidate state changes from adjacent **user-turn state snapshots per service**, not arbitrary consecutive turns from unrelated services.
2. Distinguish slot update from adding new information, reworded equivalent values, confirmations, cancellations, and unresolved cases.
3. Add *human-verified* cue spans, old/new value roles, explicit preservation spans, and backward-reference links.
4. Audit mismatched and missing offsets, duplicate dialogues, ambiguous transitions, and splits without leakage.
5. Create a new **difficulty-stratified challenge subset** (L1–L5), with provenance, human annotation guidance, and adjudication logs.

> **Crucial:** Comparing `state_before != state_after` only yields a **candidate**. It does not prove that the user explicitly corrected something; a service switch, initial slot fill, equivalent rephrasing, or system-suggested value can produce similar effects.

### 3.3 Data feasibility gate (hard stop for full training)

Before approving the final taxonomy or training budget, inspect **real** SGD JSON and report, by service and dialogue:
- number of observed user turns, non-categorical text offsets, categorical-only values, and changes in active intent or slot states;
- `ADD`, likely `UPDATE`, potential `DELETE`, unchanged/`KEEP` candidates; **do not call these gold revision types**;
- explicit lexical correction cues, explicit keep/cancel/restoration expressions, and long-distance reference candidates;
- false-positive samples, service-switch artifacts, aliases, negative examples and genuinely unresolvable references;
- estimated human annotation effort and reliable per-class held-out support.

If meaningful `RESTORE`/`KEPT_VALUE`/rare cues are absent, **downgrade them to a separately reported hand-validated challenge task**. Do not fabricate abundant gold labels or quietly repurpose a generic slot-filling corpus into the desired task. If explicit revision examples are too sparse to train a credible model, stop and narrow the scientific question with project owner approval before proceeding.


## 4. Two-layer token annotation — proposed v0.2

Two **provisional** BIO heads keep **what text is mentioned** distinct from **how revision is signaled**. Each head has its own `O` label, avoids impossible single-label overlap, and can be trained/evaluated independently. Final mapping must be frozen **after a pilot**.

### 4.1 Layer V — value and reference spans (four categories)

| Type | Definition | Example span |
|---|---|---|
| `NEW_VALUE` | Explicitly proposed value for a slot (whether first fill or revised value); the `ADD` vs `UPDATE` distinction is made using context | **Paris** in “Change Berlin to Paris” |
| `OLD_VALUE` | Explicitly mentioned value being rejected/replaced | **Berlin** in the same utterance |
| `KEPT_VALUE` | Explicitly repeated value asserted to remain unchanged | **Friday** in “Keep Friday” |
| `REFERENCE` | Expression referring to a historical value/option without explicitly naming its value | **the first city I mentioned** |

BIO labels: `O`, and `B-*/I-*` for each of four types (9 labels total). A span has **exclusive-end** character offsets and associated slot/service metadata when resolvable.

Do **not** label implicit retained values as `KEPT_VALUE` when no mention exists in the current text. Unstated preservation belongs to dialogue-state evaluation.

### 4.2 Layer C — operation cue spans (four categories)

| Type | Definition | Example span |
|---|---|---|
| `UPDATE_CUE` | Explicit signal of revision/substitution | “**instead of** Berlin” |
| `CANCEL_CUE` | Explicit signal to cancel/clear an intent or value | “**cancel** the request” |
| `KEEP_CUE` | Explicit signal to retain existing information | “**keep** Friday” |
| `RESTORE_CUE` | Explicit signal to recover an earlier state | “**go back to** the first option” |

BIO labels: `O`, plus four `B-*/I-*` pairs (9 labels total). `ADD` may be an **implicit state transition** without a lexical cue, so it is not invented as an additional token category. Multiple operation targets are represented with separate annotations in the transition graph.

### 4.3 Span boundary rules

1. **Zero-based, half-open character offsets:** `[start, end)` must exactly satisfy `utterance[start:end] == annotated_surface` in Python.
2. Do not include surrounding punctuation/whitespace unless linguistically part of a selected cue.
3. Multiword cue: keep the complete smallest contiguous signal (`instead of`, `go back to`).
4. Value mentions are labeled based on **their role in the current revision**, not simply slot type (`Berlin` can be NEW in one turn and OLD in another).
5. Unresolvable references are still marked as `REFERENCE` if explicitly mentioned; `target = null`, `resolution_status = UNRESOLVED`.
6. Ambiguous expressions go to annotation review; do not silently force a confident role.
7. Separate the user utterance being tagged from system utterances used as context; do not train the primary tagging head on system messages as if they were user revisions.
8. Multi-service identical words need a `(service, slot)` link; value string matching alone is insufficient.
9. If a value mention and an operation cue overlap, preserve them in **separate BIO layers**; document any within-layer overlapping spans and route them to a span-based representation or manual adjudication.
10. Preserve exact raw utterances, offsets and language; normalize whitespace/text only if character alignment is rebuilt and verified. Never align labels against a silently modified string.

## 5. Dialogue transition and reference schema (separate from BIO)

Each transition contains:

- `service`, `slot`, optional `intent`, `operation` (`ADD | UPDATE | DELETE | KEEP | RESTORE | CANCEL_INTENT | UNRESOLVED`)
- `before` / `after` values; `turn_id`; `source_span_ids` from the current message, if any
- `reference_target` = `{dialogue_id, turn_id, service, slot, value}` or `null`
- `resolution_status` = `RESOLVED | AMBIGUOUS | MISSING_CONTEXT | NOT_APPLICABLE`
- `evidence` (`sgd_state_diff_candidate | sgd_slot_span | human_gold | generated_reviewed`)

**Cue polarity and scope:** For every operation cue, record `polarity = ASSERTED | NEGATED | UNCERTAIN`, and link it to a target `(service, slot/intent)` or `null`. For example, in “Don't cancel the flight, cancel the hotel”, both words “cancel” may be lexically detected, but **only the hotel cancellation is an asserted transition**. A cue is not proof of executed user intent; context and scope must be resolved.

**No circular gold-state dependency:** In end-to-end inference, the system may access **previously predicted** state or explicit dialogue context, not the current gold state or an annotation derived from the answer. A separate `oracle_previous_state` evaluation is allowed only if clearly labeled and never compared as equivalent to end-to-end inference.

**KEEP interpretation:** State equality alone is not an explicit user instruction to keep a slot. Track `keep_source = explicit | implicit`, and score explicit preservation separately from background unchanged slots.

**RESTORE interpretation:** Current value equals an *earlier, non-immediately-prior* value **and** the utterance/referent supports a reversion. Equality alone is not sufficient. If the prior target is not uniquely identifiable, use `UNRESOLVED`, not a guess.

**CANCEL interpretation:** Cancelling a booking intent is different from deleting one slot value. The scope must be annotated. Do not infer a real-world external cancellation; the dataset contains conversational state, not action confirmation.

**Equivalent values:** Normalize only by documented per-slot/domain rules (e.g., spoken forms); compare equivalent aliases before claiming an UPDATE. Never automatically parse relative dates against today's actual date; the original SGD documentation uses its own fixed convention for relative dates.

## 6. Proposed serialized training example

The JSON below is an **illustrative new annotation record**, not a direct export from SGD. The example includes validated character offsets relative to the exact current user utterance. It remains illustrative, **not** human-verified gold.

```json
{
  "example_id": "override_demo_001",
  "provenance": "illustrative_not_gold",
  "dialogue_id": "demo_dialogue",
  "turn_id": 2,
  "service": "Flights_demo",
  "history": [
    {"turn_id": 0, "speaker": "USER", "utterance": "Book for Berlin on Friday for two people."}
  ],
  "utterance": "Actually, not Berlin. Make it Paris for three people, but keep Friday.",
  "spans_value": [
    {"label": "OLD_VALUE", "text": "Berlin", "start": 14, "end": 20, "slot": "destination"},
    {"label": "NEW_VALUE", "text": "Paris", "start": 30, "end": 35, "slot": "destination"},
    {"label": "NEW_VALUE", "text": "three people", "start": 40, "end": 52, "slot": "passengers"},
    {"label": "KEPT_VALUE", "text": "Friday", "start": 63, "end": 69, "slot": "date"}
  ],
  "spans_cue": [
    {"label": "UPDATE_CUE", "text": "not", "start": 10, "end": 13, "polarity": "ASSERTED"},
    {"label": "UPDATE_CUE", "text": "Make it", "start": 22, "end": 29, "polarity": "ASSERTED"},
    {"label": "KEEP_CUE", "text": "keep", "start": 58, "end": 62, "polarity": "ASSERTED"}
  ],
  "transitions": [
    {"slot": "destination", "operation": "UPDATE", "before": "Berlin", "after": "Paris"},
    {"slot": "passengers", "operation": "UPDATE", "before": "two", "after": "three"},
    {"slot": "date", "operation": "KEEP", "before": "Friday", "after": "Friday", "keep_source": "explicit"}
  ]
}
```

**Agent contract:** In actual artifacts every span must have numeric offsets, and data validation must fail if surface text disagrees with offsets. The *illustrative* spans can be unit-tested, but must never be counted as an annotation corpus. Cue boundaries (e.g. whether “not” is sufficient or “Actually, not” is preferred) are **provisional until adjudication**. Fields identifying categorical slots without direct spans must not be fabricated.

## 7. Mandatory scenario and edge-case matrix

| ID | Scenario | Example | Expected result / caveat |
|---|---|---|---|
| E01 | Direct replacement | “Not Paris, Rome.” | Old/new value roles, update. |
| E02 | Equivalent paraphrase | “6 pm” → “six in the evening” | No update if same normalized meaning. |
| E03 | Add new slot | “Also add breakfast.” | `ADD` transition; label value span only if textual. |
| E04 | Explicit keep | “Change city but keep Friday.” | Preserve date; update only targeted city. |
| E05 | Implicit keep | “Change city to Rome.” | Other slots unchanged in state; no invented KEEP token span. |
| E06 | Cancellation scope | “Cancel the hotel, not the flight.” | Cancel hotel intent only; contrast/negation checked. |
| E07 | Restore | “Go back to the first city.” | Historical reference; restore if uniquely resolvable. |
| E08 | Multiple references | “Second hotel, first date.” | Independent reference links. |
| E09 | Missing antecedent | “Choose the third one.” (no options available) | Mark reference; unresolved, do not hallucinate. |
| E10 | Ambiguous referent | Two “first options” in different services | `AMBIGUOUS` unless service context disambiguates. |
| E11 | Service switch | Flight state → hotel state | Avoid false changed-slot labels from unrelated services. |
| E12 | System suggestion | Agent proposes city, user says “No, Rome.” | Correctly infer target from preceding system turn. |
| E13 | Compound negation | “Don’t cancel the flight, cancel the hotel.” | Negated cue must not trigger flight cancellation. |
| E14 | Long-distance reference | “Use the city from four messages ago.” | Evaluate with/without sufficient context. |
| E15 | Multiple candidates in one turn | “Paris or Rome — actually Rome.” | Final selection and rejected alternative distinguishable. |
| E16 | Implicit correction | “It’s three of us.” (previously two) | Candidate update from state; human gold required. |

**L4/L5 audit:** New manually authored or otherwise lawfully sourced examples must be labeled and checked; do not report them as naturally occurring SGD gold.

## 8. Annotation protocol and quality control

1. Write `annotation_guidelines.md` with examples, counterexamples, slot-link rules, and ambiguity policy.
2. Obtain candidate examples from official SGD **train** data, preserving original IDs/provenance; keep official dev/test untouched for baseline comparison.
3. Prepare an initial **pilot of 100 candidate instances**, deliberately including positives, negatives, slot-alias cases, service switches and cancellation/reference candidates. This is a **target**, not a measured number.
4. Two independent annotators label an overlapping subset blind to each other's choices; record span-level agreement and operation-label agreement (do not report a made-up Cohen's kappa).
5. Adjudicate disagreements and update the written guidelines; retain pre- and post-adjudication versions.
6. Build a larger cleaned and human-verified evaluation subset only if the pilot demonstrates feasible class coverage. A proposed **400–600** audited examples is a planning target, not a guaranteed sample size.
7. Separate manual gold labels from weak/heuristic pseudo-labels in filenames, records and evaluation. The held-out test set must be **human adjudicated**, fixed before model selection, and never expanded with model-picked successes.
8. Annotation disagreements must be recorded with exact-spans agreement (and category agreement), rates, sample counts and guideline versions; do not infer gold trustworthiness from dataset size.
9. A category with too few independently adjudicated held-out examples must appear as **diagnostic / insufficient support**, not as a reliable standalone F1. Pre-register support thresholds after pilot and show raw denominators.
10. If L4/L5 data are too sparse or ambiguous for statistical evaluation, report as a small diagnostic challenge set and **do not claim** generalization on these levels.
11. Document all exclusions with counts, rationale and script versions; avoid selective removal of difficult negative examples.

## 9. Modeling experiment contract

**B0 — Non-oracle rule baseline:** Lexical cues, known slot metadata, and available prior **predicted** state only. At test time, **never** derive predictions from the current turn's gold SGD `frames[].state`, or use future user/system turns. A gold-state oracle may be reported separately, never as a fair primary baseline.

**B1 — CRF token classifier:** Current user message + engineered context features; train separate or joint value/cue heads consistently.

**B2 — Transformer token classifier:** Context-conditioned encoder (e.g. BERT family) with history segment boundaries and a loss mask so only current USER utterance tokens are scored. Train both BIO layers; treat subword alignment consistently (`-100` ignored label for non-first subtokens, or another explicitly documented scheme).

**Context input protocol:** Preserve chronological `USER/SYSTEM` boundaries, current turn and truncation policy; when context exceeds max tokens, **always retain the current utterance**, record how many earlier turns were dropped, and apply loss/metrics only to current user text. In controlled no-context experiments, do not leak current gold slot state through feature engineering.

**Ablations:** `last-turn only`, `last two turns`, `full available context truncated to a documented token budget`; `with/without state metadata`; optional `with/without human-reviewed challenge augmentation` (no test-derived labels in training).

**Fairness:** Same example IDs and gold labels across conditions; frozen splits; baseline/model parameter reporting; seeds where feasible; at least one fully reproducible training and evaluation command.

**Source of truth:** A model's confidence score is not ground truth. Hand-authored demo cases and selected illustrative examples must not be mixed with held-out evaluation results.

## 10. Evaluation — independent metrics

**Primary (token/span):** per-class precision/recall/F1, macro-F1 (over actually evaluated classes), micro-F1, strict exact-span F1 (correct boundaries *and* label). Report value-layer and cue-layer separately, plus frequency/support of each class. Token accuracy alone is not sufficient.

**Secondary (state):** transition-type macro-F1; slot-update accuracy; joint dialogue state accuracy if the necessary verified gold exists; referent link accuracy on unambiguous adjudicated examples; coverage and abstention accuracy on ambiguous cases.

**Robustness:** metrics broken down by L1–L5, service/domain, reference distance, explicit vs implicit updates, same vs different slot lexical forms.

**Analysis:** confusion matrix for operation labels; false positives on unchanged data; exact boundary errors; state errors caused by entity/slot mix-ups; examples with missing contextual evidence.

**Statistical reporting:** Include confusion/mistake examples and bootstrap confidence intervals by **dialogue** when sample size allows. Record negative examples and false-positive rates for unchanged turns; do not only report positive corrections.

**Avoid misleading aggregate claims:** Report counts and uncertainty for rare L4/L5 categories. Compare models only when the evaluation subset and metric definitions are identical.

## 11. Split and leakage policy

- Respect upstream SGD train/dev/test partitions for comparisons with known benchmark annotations.
- Partition custom annotated examples at **dialogue / dialogue-family level**, not independent sentence level; all paraphrases of the same dialogue must remain in one split.
- Never annotate official evaluation examples and feed their labels into training.
- Deduplicate by normalized utterance + dialogue context fingerprint and audit near-duplicates.
- Historical context is permitted at inference; **future turns are not**.
- The reference resolver must operate only on already seen turns and documented system options.
- Version datasets and scripts so the exact gold set can be reproduced and audited.

## 12. Engineering interfaces

Recommended module boundaries:

```text
src/override/
  ingest_sgd.py           # raw schema/data readers
  derive_candidates.py    # heuristics; labels are NOT gold
  validate_spans.py       # offset, BIO and overlap validators
  annotate_contract.py    # human-reviewed annotations schema
  tokenize_align.py      # text offsets -> model tokens
  baselines.py            # rules + CRF
  train_transformer.py    # context-aware model training
  evaluate.py             # primary + secondary metrics
  infer.py                # current user utterance -> labeled spans
  state_resolver.py       # transitions/references/abstention
  render_trace.py         # optional text/JSON traces for terminal reports
```

The actual project may reorganize modules, but their responsibilities and separation of evaluation from inference are contractual.

## 13. Acceptance gates — do not mark PASS without evidence

- [ ] **G0 Project rules:** Update P2 collision check and verify P2-specific deadlines/rubric. P1 grading details are not automatically P2 rules.
- [ ] **G1 Data inspection:** Inspect raw SGD samples and count per-domain candidate revisions; establish which fields have usable spans.
- [ ] **G2 Schema review:** Two annotators test a small pilot; finalize definitions and boundary rules; quantify ambiguous labels.
- [ ] **G3 Gold set:** Human-reviewed examples with provenance, offsets, versioned guidelines and leakage-safe splits.
- [ ] **G4 Baseline:** At least one fully reproducible baseline with valid per-class metrics.
- [ ] **G5 Context experiment:** Controlled context-free vs context-aware comparison on the same test examples.
- [ ] **G6 Difficult cases:** L1–L5 counts and outcomes, with honest reporting for sparse/unsupported cases.
- [ ] **G7 Correctness:** Automated unit tests for offsets, token alignment, transition semantics and history linkage.
- [ ] **G8 Public repo:** Clean README, preprocessing scripts, training/evaluation scripts, contributions files per member backed by actual GitHub commits, license and legally shareable raw/clean data.
- [ ] **G9 Demo:** Never claim a manually hard-coded preview is a real model result. Demo must load the trained model artifact.
- [ ] **G10 Presentation:** Model choices, datasets, failures and findings are explainable within P2's confirmed time limit.

## 14. Decisions and open investigations

### Locked

- Follow `01_REQUIREMENTS.md` for confirmed P2 rules vs historical P1 grading precedent.
- Project name `OVERRIDE`, group `Developers`, primary coursework area **token classification**.
- Both explicit corrections and multi-turn reference-based revisions are in research scope.
- Token/span prediction remains separate from state transition + historical reference resolution.
- No fictional performance metrics; no fabricated pre-labeled dataset fields.

### Provisional — pilot may change

- Two-layer BIO scheme (four value/reference types and four cue types).
- SGD as the main source, with new human-reviewed annotations.
- 100-instance pilot, then target 400–600 audited examples if data supports it.
- CRF vs context-aware Transformer experiments.
- Optional formatted terminal trace/static diagram only **after** primary experiment quality gate; **no website is part of the agreed deliverable**.

### Blockers to verify before declaring final readiness

- Real distribution of explicit corrections vs implicit state updates in SGD.
- Whether sufficient naturally occurring, gold-verifiable L4/L5 examples exist; otherwise create a clearly labeled original challenge suite.
- Data annotation agreement and transition link reliability.
- Whether dataset licensing/derivative publication complies with CC BY-SA 4.0 attribution/share-alike and other source terms.
- Current P2 group selections and instructor-specific Project 2 requirements.

## 15. References and attribution

1. Google Research, *The Schema-Guided Dialogue Dataset* (official dataset repository): https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
2. Dataset representation, state semantics and evaluation conventions: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/dstc8.md
3. Rastogi et al. (2020), *Towards Scalable Multi-Domain Conversational Agents: The Schema-Guided Dialogue Dataset*: https://ojs.aaai.org/index.php/AAAI/article/view/6394
4. Original SGD / SGD-X licensing: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/LICENSE.txt

---

**Implemented next artifact:** `03_DATASET_PIPELINE.md` describes the auditable corpus pipeline and a read-only `scripts/audit_sgd.py` (unit tested on synthetic fixtures). Real SGD auditing, human labeling and model training remain **NOT DONE**. Consult it before giving the coding agent further tasks.
