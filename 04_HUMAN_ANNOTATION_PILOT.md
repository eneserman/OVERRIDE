# OVERRIDE — Pilot Annotation Protocol and Data Quality Gates

**Document:** `04_HUMAN_ANNOTATION_PILOT.md`  
**Version:** v0.1 · 2026-10-27  
**Status:** Pilot design + local sampling script tested on synthetic fixtures. **NO independent human annotations or real SGD statistics yet.**  
**Delivery format:** Python command-line research project, public GitHub repository + PPTX. **No website required.**

## 1. Goal, not a fabricated result

Create a small independently annotated pilot from **official SGD TRAIN** conversations to discover whether the proposed revision span labels can be reliably identified and learned. The primary task is **current-user-turn token/span classification conditioned on prior conversation**. Dialogue state changes and reference resolution are separate secondary tasks. Never equate one with the other.

The dataset source already provides dialogue text, service frames, dialogue state and selected slot spans. **It does NOT supply Developers' proposed `NEW_VALUE`/`OLD_VALUE`/`KEPT_VALUE`/`REFERENCE` or correction cue gold annotations.** Automatic state differencing and string matching are **candidate-mining tools**, not human gold. See `02_NLP_TASK_DESIGN.md` for complete provisional definitions.

## 2. Steps and terminal commands

### D0 — Real data inventory: prerequisite (NOT YET DONE)

```bash
# Clone official upstream in the coding agent's computer and capture its exact commit:
git clone https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd
git -C data/upstream/sgd rev-parse HEAD
python -m unittest discover -s tests -v
python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit
```

Do not say D0 passed unless `reports/sgd_train_audit/sgd_audit_summary.json` contains actual full-train data counts, hashes, and zero blocking errors, with any remaining warnings documented. Audit read-only; do not rewrite upstream files.

### D1–D2 — Mine and sample for a blinded human pilot (code implemented; REAL DATA NOT RUN)

```bash
python scripts/prepare_annotation_pilot.py \
  --sgd-root data/upstream/sgd \
  --out data/annotations/pilot_v0.1 \
  --sample-size 100 --seed 42 --context-turns 8
```

Produces:

| File | Purpose | Who may see it |
|---|---|---|
| `pilot_sampling_summary.json` | True counts of heuristic candidate strata and selection policy | NLP engineer/reviewer |
| `PRIVATE_sampling_manifest.jsonl` | Private sampling hints and state-delta candidates; **not ground truth** | NLP engineer only; **not annotators** |
| `annotator_A_UNLABELED.jsonl` | Independent annotation input, empty spans (`null`) | Annotator A |
| `annotator_B_UNLABELED.jsonl` | Identical independent annotation input, empty spans (`null`) | Annotator B |

Every example includes the current user utterance and prior-turn text only. It does **not** include the current turn's SGD state, future turns, mined cue labels or a guessed gold annotation. This prevents anchoring annotators to heuristic candidates. Keep code/output sample manifest private from annotators until adjudication. Both annotators receive the **same IDs** to compare judgments.

Pilot sampling is deterministic, approximately round-robin by candidate stratum, and enforces **at most one selected example per dialogue**. The resulting proportions are deliberately **not representative** of the original conversation population. Do not calculate prevalence from this sample. The miner may return fewer than 100 if source constraints demand it. The gold test split will later be frozen independently at dialogue level.

## 3. Provisional annotation taxonomy (must be frozen after pilot)

### Layer V — semantic span of mentioned values and references

- `NEW_VALUE`: stated target value that is proposed as current, whether this is a new addition or an update. Examples: **Paris** in “Make it Paris”; **three people** in “Change to three people.”
- `OLD_VALUE`: stated value explicitly rejected/replaced. Example: **Berlin** in “Not Berlin, Paris.”
- `KEPT_VALUE`: explicitly stated value to preserve. Example: **Friday** in “Keep Friday.” Do not hallucinate a `KEPT_VALUE` span when preservation is only implicit.
- `REFERENCE`: an overt phrase referring to an earlier choice/value without naming it. Example: **the first option** in “Go back to the first option.”

### Layer C — operation signaling in current utterance

- `UPDATE_CUE`: linguistic instruction to substitute/correct a value. Example: **instead of** in “Instead of Berlin, use Paris.”
- `CANCEL_CUE`: cancellation or removal instruction. Example: **cancel** in “Cancel the hotel booking.”
- `KEEP_CUE`: explicit preservation signal. Example: **keep** in “Keep Friday.”
- `RESTORE_CUE`: explicit return to a prior value/state. Example: **go back to** in “Go back to the first option.”

The current proposal is **two BIO layers**, one per type family. They can overlap **across layers**. Overlap **within** a layer must be escalated or represented with an explicitly reviewed span-based extension. Do not silently overwrite labels. An operation can exist without an overt cue span (`ADD` based on context, etc.). Label boundaries are the smallest complete contiguous span carrying the meaning, excluding surrounding punctuation unless relevant.

### Dialogue transitions — separate structured annotations, NOT token classes

For each slot/intent transition, record one of `ADD`, `UPDATE`, `DELETE`, `KEEP`, `RESTORE`, `CANCEL_INTENT`, `UNRESOLVED` and provenance/evidence. The state resolver later uses previous **predicted** state or history; no test-time gold state. A state equality alone is not an explicitly spoken `KEEP`, and a string reappearing from turn 1 is not automatically `RESTORE`.

## 4. Ambiguity and negative examples (critical)

| Utterance and context | Required annotator judgment |
|---|---|
| “No, not Berlin. Paris.” after an explicit Berlin request | Old/new spans, correction cue if overt, `UPDATE` if target identified |
| “Not cancel the flight — cancel the hotel.” | The first cancellation is **negated**; do not mark as an asserted flight cancellation |
| “Keep Friday.” | Explicit `KEEP_CUE` + `KEPT_VALUE` only if Friday refers to that slot |
| “Go back to the first one.” without earlier candidate options | `REFERENCE` but target `UNRESOLVED`; don't invent the value |
| “What about 6 pm?” after “six in the evening” | Possibly same value; no forced update without domain-aware equivalence check |
| User selects one option offered by the system for the **first time** | Could be first fill/ADD, not correction of prior user instruction |
| Same-service frame missing after intent switch | Not automatically a cancellation or deletion |
| “No, that's not correct.” without a resolvable target | Do not force an `UPDATE` or invent an `OLD_VALUE` |
| “Change hotel, not flight.” | Respect contrast and scope; one cue may reference different targets |
| “Keep everything else the same.” | `KEEP_CUE` can be labeled, but no invisible `KEPT_VALUE` spans |

Use case type `NEGATIVE_CONTROL`, `UNRESOLVED` or `AMBIGUOUS` in metadata where appropriate; **absence of spans must mean a human-labeled true negative only after annotation**, not a default empty field.

## 5. Review instructions and gold annotation protocol

1. Two reviewers independently read the relevant current user utterance and prior chronological conversation, without private heuristic hints and without looking at each other's annotations.
2. Each marks `[start,end)` character offsets relative to the **exact unmodified current user utterance**, surface text, layer label, optional `(service,slot)` and cue polarity (`ASSERTED`, `NEGATED`, `UNCERTAIN`).
3. For every span, verify programmatically `utterance[start:end] == surface_text`. Zero-length spans, negative offsets and invalid BIO transitions are prohibited. Character offsets must remain valid after any text normalization (prefer avoiding normalization during annotation).
4. Annotate transitions, linked history references, uncertainty and scenario level L1–L5 **only when justified by the available context**. Use `NOT_APPLICABLE`, `AMBIGUOUS` or `UNRESOLVED`, never guess.
5. After **both** independent outputs are complete, compute exact-span agreement (and per-class agreement/confusions where sufficient data exists). Discuss disagreements and record the reason for each adjudicated decision. Do not secretly overwrite either annotator's original results.
6. Freeze an adjudicated `pilot_gold_v0.1.jsonl` with guideline version, contributor IDs, source IDs, adjudicator, timestamp, sample manifest hash and resolution log. This file **does not exist yet**.
7. Report count of reviews per class, negative controls, ambiguous records, rejected examples and label distributions. Before model training, decide whether rare L3–L5 labels must remain exploratory challenge cases rather than supervised training targets.
8. GitHub contribution files and actual diffs must match work performed by each team member; AI-generated text alone is not evidence of a student's understanding or contribution.

## 6. Go/no-go criteria (quality-based, not invented scores)

**GO to full annotation plan only when:** official train provenance and hashes are recorded; sample is generated reproducibly; both reviewers can apply stable rules to a pilot; offset errors are resolved; no critical within-layer overlap is silently dropped; important labels have documented support; and disagreements have a written resolution. Record denominators; don't rely solely on vague accuracy.

**NARROW or NO-GO when:** real multi-turn corrections are too rare, `RESTORE` examples lack resolvable references, annotators routinely disagree on core cue/value types, class rarity makes a credible test impossible, or the proposed correction task collapses into trivial lexical detection. Report honest limitations, ask the project owner to approve narrowing the label space, and **do not train a misleading full model**.

An initial 100 examples is a **pilot target**, not a gold corpus or a sufficient final benchmark by itself. A larger human-validated corpus must be planned based on *observed* per-class support and available human annotation effort.

## 7. Dataset split and scientific experiment obligations

- Apply official SGD train data only to candidate mining and custom training gold creation. Dev/test gold from SGD does **not** automatically provide OVERRIDE gold for these novel labels.
- Freeze original dialogue-family groups across custom train/validation/test; prevent paraphrase leakage.
- Compare last-turn-only vs history-aware systems on precisely the **same** adjudicated held-out examples and evaluation code.
- Report strict span-level F1 of both BIO heads separately, rare-class support, false positives on negatives and results by L1–L5 difficulty.
- State transition and historical reference performance are **secondary**, measured only if verified structured gold exists.
- Never present candidate-mining percentages as model accuracy or gold-label prevalence.

## 8. Responsible repo publication

Source: [Google SGD](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue), **CC BY-SA 4.0** (follow license and attribution obligations, including adaptations). Document upstream commit and SHA-256 values. Code can use a compatible separately stated license. The user's supplied first-project instructions requested raw+clean datasets; publishing them must still respect upstream licenses and document changes. Ensure no local API keys, private annotator identity data or unstated copyrighted sources are committed.

## 9. Stage status (2026-10-27)

| Stage | Status |
|---|---|
| D0 Official full-train SGD audit | **NOT RUN** in this environment |
| D1 Mining and sampling code | **IMPLEMENTED** (`scripts/prepare_annotation_pilot.py`) |
| D1–D2 Running on real SGD | **NOT RUN** |
| D2 Blind annotation queue | **CODE READY**, real queues not created |
| D3 Independent human labeling / adjudication | **NOT STARTED** |
| D4 Gold freezing and held-out split | **NOT STARTED** |
| D5–D7 Training / evaluation | **BLOCKED until preceding gates** |

This is an academic Python/CLI pipeline—not a website product specification.
