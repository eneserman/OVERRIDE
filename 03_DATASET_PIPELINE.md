# OVERRIDE — Dataset Engineering, Annotation & Reproducibility

**Document:** `03_DATASET_PIPELINE.md`  
**Version:** 0.2 | **Date:** 2026-10-27  
**Team:** Developers · NLP Project 2  
**Status:** DATA PIPELINE DESIGN + WORKING READ-ONLY AUDIT CODE; **NO REAL SGD CORPUS AUDIT COMPLETED**

> **Core guarantee:** OVERRIDE is a **Python/CLI-first academic NLP repository**, not a website. The primary deliverable is a reproducible *token classification* pipeline. No web, mobile application or frontend is required by the supplied Project 2 instructions. Present findings in PPTX using terminal predictions, evaluation tables and static figures. If a UI is proposed later, it is expressly outside the assessed core.

## 0. Mandatory reading and integrity

Read with `00_DESIGN_AUDIT.md`, `01_REQUIREMENTS.md` and `02_NLP_TASK_DESIGN.md`. Keep three notions separate:

1. **Upstream observed SGD annotations**: turn texts, services, slot spans, per-service state snapshots and intents.
2. **Heuristic candidates/pseudo-labels**: comparisons of observed state snapshots plus cue keyword searches; **NOT gold labels**, never appropriate for claimed test F1.
3. **Developers gold labels**: spans and links reviewed against the full accessible conversation by human annotators, with versioned guidelines and adjudication.

Do not misstate number of training examples, correction types, gold labels, or accuracy. The initial dataset has not been downloaded or counted in this working environment. One source file could not be fetched here due to external-network restrictions. The accompanying local script has been **unit tested on synthetic toy data only**.

## 1. Research goal and auditable hypotheses

- **H1 (primary):** Context-aware token classification improves **strict exact-span F1** for revision-related cues/value/reference spans over a same-data, context-free system.
- **H2 (secondary):** Conditioned on gold span input vs predicted span input, explicit links and dialogue transitions can be computed without leaking future user utterances.
- **H3 (diagnostic):** L3–L5 (cancellation, multi-turn restoration, complex split references) degrade more than L1–L2, but only report this if sufficient independently adjudicated examples exist; otherwise describe the diagnostic cases without statistical generalization.

**Primary prediction task:** Given prior turns + current USER turn, assign labels to *current-turn tokens*, not a dialogue-level class alone. The two-layer label taxonomy is provisional in `02_NLP_TASK_DESIGN.md` and is frozen only after a pilot. `KEEP` with no explicit current text must be represented in state metadata, not as a fictitious span.

**Critical evaluation control:** Ordinary first-time slot filling can vastly outnumber real corrections. Always publish **revision-only** and **non-revision negative** metrics separately; never use good basic slot extraction scores as proof of revision detection.

## 2. Official source and licenses

- Source: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
- Schema: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/dstc8.md
- License text: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/LICENSE.txt
- Original paper: Rastogi et al. (2020), *Towards Scalable Multi-Domain Conversational Agents: The Schema-Guided Dialogue Dataset*.
- Repo license: **CC BY-SA 4.0** for SGD/SGD-X. Credit the source and changes; include appropriate notices; assess share-alike duties for adapted text and redistributions. License your original code separately and transparently.
- Dataset repository archived/read-only in April 2026; pin a git commit (`git rev-parse HEAD`) and preserve SHA-256 for all downloaded source files. Do not use a floating dataset version in the final experiment.

**Proposed agent-side acquisition** (requires access to GitHub in the *agent environment*, not this assistant environment):

```bash
git clone https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd
cd data/upstream/sgd && git rev-parse HEAD && cd ../../..
```

The repository may contain different subdirectories: **read `train/`, `dev/`, `test/` independently**. Original `frames[].slots` and `frames[].state` are not necessarily present in all released test examples; do not invent omitted gold annotations. Do not treat a `state` field as something that may be supplied to a model at inference time.

Source inventory should contain: `dataset`, `upstream_url`, `pinned_commit`, `split`, `file_name`, `sha256`, `license`, `collection_timestamp`, and `transformation_version` (timestamp measured at collection, not invented in advance).

## 3. Source schema contract

| Original field | Intended use | Warning |
|---|---|---|
| `dialogue_id` | group identity for dedup/splitting | May need dialogue-family grouping for paraphrases |
| `services` / `frames[].service` | compare states within the **same service** | Cross-service comparisons yield spurious “changes” |
| `turns[].speaker`, `turns[].utterance` | chronological context and current USER text | Never label system utterances as user instruction revisions |
| `frames[].slots` (`start`, `exclusive_end`, `slot`) | non-categorical mention spans | Categorical values often lack token offsets |
| `frames[].state.slot_values` | source supervision for candidate mining | Aliases are possible; a string change is not proof of user correction |
| `frames[].state.active_intent` | potential intent-change candidates | Intent changes ≠ cancellation unless human validated |
| `frames[].state.requested_slots` | metadata, not correction span gold | Must not be used as future/oracle model input |
| `frames[].actions` (system) | user response/option context | Must never be mistaken for user-proposed revisions |

SGD's state `slot_values` can list multiple **equivalent** surface variants. The source does not provide gold `UPDATE_CUE`, `RESTORE_CUE`, `KEEP_CUE`, `OLD_VALUE`, `REFERENCE` as our task defines them.

## 4. Pipeline design: strict stages

### D0 — Inspect only, before any transformation

Run `scripts/audit_sgd.py` over **official train only** first. Compute real dialogue/turn counts, frames, service/domain distribution, offset validity, state comparison coverage and rough lexical cue frequency. Pin source checksums. Its JSON/CSV reports are descriptive only.

```bash
python scripts/audit_sgd.py \
  --sgd-root data/upstream/sgd \
  --split train \
  --out reports/sgd_train_audit
```

Smoke-test only (NOT full-corpus results):

```bash
python scripts/audit_sgd.py --sgd-root data/upstream/sgd \
  --split train --limit-files 1 --out reports/sgd_smoke
```

Unit tests require only Python standard library:

```bash
python -m unittest discover -s tests -v
```

**Audit implementation outputs:**

- `sgd_audit_summary.json`: raw source hashes, descriptive counts and explicitly stated limitations.
- `service_counts.csv`: service coverage.
- `UNREVIEWED_candidate_examples.jsonl`: capped candidate sample with clear `NOT_GOLD` provenance.

**Do not** train on the candidate file or publish its counts as occurrences of verified corrections. Do not report a limited-file smoke test as a full dataset analysis.

### D1 — Candidate mining (pilot sampling code implemented; real SGD execution pending)

For each USER turn with a source `state` field: compare with the **previous observed USER state for the same service**. Keep the source turn and service IDs, lexical mention spans and the preceding system offer where applicable.

Candidate types, explicitly **non-gold**:

- `SLOT_ADDED_CANDIDATE`: first observed value in a slot.
- `SLOT_CHANGED_CANDIDATE`: no textual overlap between previous/new value sets.
- `ALIAS_OR_STATE_VARIANT_CANDIDATE`: partially overlapping value variants; semantic change unknown.
- `SLOT_CLEARED_CANDIDATE`: previously observed slot no longer present.
- `POSSIBLE_REVISION_CUE`, `POSSIBLE_KEEP_CUE`, `POSSIBLE_CANCEL_CUE`, `POSSIBLE_RESTORE_CUE` from lexical searches (not label truth).
- `NO_CHANGE_CONTROL`: unchanged same-service snapshots, plus text negatives.

**False-positive exclusions to human-review, not silently drop:** first service activation; domain switch; system-presented alternate selected for first time; equality under normalization; alias differences; negation scope (`do NOT cancel`); correcting a system guess rather than own instruction; state disappearing due to intent/session reset.

Do not assume reappearance of an old slot value means explicit `RESTORE`. Evidence must include an actual user utterance and uniquely resolvable history referent. Record uncertain cases as `AMBIGUOUS` / `UNRESOLVED`.

### D2 — Create annotation sampling plan (code implemented; independent review pending)

Target first **100** candidate/control instances for *pilot* (planning target only), selected across domains and difficulty. Oversample likely changes to learn the taxonomy, but also include unchanged negatives, service switching and lexical cue false positives. Record the **selection probability/strata**; do not use artificially balanced pilot prevalence to claim population frequency.

Suggested pilot strata: explicit value replacement; value add; cancellation polarity; explicit keep; restore/reference; unchanged/negation/service switch. If a class is missing in real train data, document absence instead of fabricating prevalence.

Source text plus conversation history should be visible to annotators; any candidate hints must be hidden during independent annotation when practical to reduce confirmation bias.

**Implemented preparatory tool (`scripts/prepare_annotation_pilot.py`):** This generates stratified, deterministic **unlabeled** annotator A/B packets from raw SGD **train**, plus a private heuristic sampling manifest and counted summary. It hides state-delta/cue hints from annotators and never emits gold labels. Run only after the full D0 real-data audit:

```bash
python scripts/prepare_annotation_pilot.py \
  --sgd-root data/upstream/sgd \
  --out data/annotations/pilot_v0.1 \
  --sample-size 100 --seed 42 --context-turns 8
```

The sampler prioritizes possible revision/keep/cancel/restore and negative-control strata, approximately round-robin, at most one example per dialogue. It intentionally **does not** estimate population prevalence. Its output is unreviewed even when a slot changed. See `04_HUMAN_ANNOTATION_PILOT.md` and `AGENT_D1_D2_PILOT_PROMPT.md` for the full contract.

### D3 — Human-gold annotation and adjudication (planned)

1. Write `annotation_guidelines.md` and freeze version `v0.1` before independent marking.
2. Both annotators mark a meaningful overlap (preferably all 100 pilot cases if feasible) **independently**.
3. Annotate token/character spans per Layer V and C in `02_NLP_TASK_DESIGN.md` with `[start,end)` half-open offsets, text assertions and optional service/slot links.
4. Independently identify revision **operation**, target slot/intent, history reference, scope and ambiguity. These are **separate labels/relations**, not forced into BIO.
5. Store `annotator_id`, `guideline_version`, annotation timestamp, source dialogue+turn ID and reasons for ambiguous decisions.
6. Measure boundary agreement (exact-span intersection/union), per-category agreement and operation agreement; define how partial overlaps are treated. A chance-corrected statistic may be added where meaningful, without inventing one.
7. Adjudicate disagreements; preserve individual versions and the final consensus labels. Never make test corrections based on model predictions.
8. Pilot decision: if sparse/ambiguous classes cannot support reliable assessment, move them to a **labeled diagnostic challenge suite**, preserve primary task, and explicitly update taxonomy with approval. 

**Gold rule:** No example is gold until reviewed/adjudicated according to the written protocol. Weak labels are never counted as gold in held-out test metrics.

### D4 — Freeze gold subset and splits

- Group by `dialogue_id` and a **dialogue-family ID** for rephrasings/derived variants.
- Separate independent examples at dialogue level, preventing the same conversation/rephrase family across train, validation and test.
- Keep official SGD `dev`/`test` outside custom gold training; no official test gold for our new labels exists automatically.
- Pre-register random seed, assignment algorithm, exact split manifest hashes, and class counts; annotate new test cases blind to model results.
- Do not split token sequences from the same dialogue across folds. Freeze held-out test before tuning or inspecting model errors.
- Report overlaps and near duplicates. Preserve **hard negatives**, not only successful correction cases.

Target additional **400–600** human-reviewed gold examples only after a successful pilot and resourcing check. A small genuine high-quality annotated set may be more credible than a large fabricated one. Record actual counts (not target counts) at every milestone.

### D5 — Convert clean annotations to token labels

- Load tokenizer with saved name/version (for pretrained Transformer, use `return_offsets_mapping=True`).
- Explicitly map **character spans** to word/subword tokens and document how whitespace, Unicode and punctuation are handled.
- For each head separately, build BIO targets `B-...`, `I-...`, `O`; loss is computed for the **current USER turn only**.
- Mask special tokens, history context and ignored subword positions as `-100` if using first-subtoken label strategy; don't score them.
- Overlapping labels across heads remain distinct; overlapping within the same head must trigger validation failure or be handled by a declared span-based extension, **not overwritten**.
- Reject invalid offsets, span/text mismatches, unknown label names, bad BIO transitions and any source ID without documented provenance.
- Publish mapping statistics (examples, current-turn tokens, class support, rejected spans, truncation counts). No silent record loss.

### D6 — Model inputs without leakage

- `last-turn` and `context-aware` receive the **same current USER utterance**; add prior chronological USER/SYSTEM turns only in context condition.
- Encode full prior text or allowed **previously predicted** state; **never give current/future gold SGD state or gold current-turn spans** to the test-time system.
- Preserve current-turn tokens when truncating context; store number of dropped history turns/tokens.
- If an oracle prior-gold-state condition is demonstrated as upper bound, label it **ORACLE — NOT COMPARABLE** to normal input.
- Do not use system actions from turns *after* current user turn.

### D7 — Evaluate, archive, reproduce

- Primary: per-class precision/recall/F1, micro/macro span-F1, **strict exact-character-span F1**; value layer and cue layer separately.
- Explicit revision-positive vs revision-negative false-positive behavior; unchanged-turn controls and confusable negation.
- Secondary: transition accuracy, target-slot correctness, reference linking/abstention, provided **gold exists** for these evaluations.
- Stratify by L1–L5, domain, history distance, explicit/implicit revision and rare classes; report denominators.
- Compare rule baseline, CRF and Transformer on the **identical gold test split**. Ablate history window using same model/settings when feasible.
- Publish JSON config, trained checkpoint metadata, seeds, exact data hashes, environment specification, commands and machine-readable results. Never invent a `PASS` gate or scores.

## 5. Annotation schema for new human-reviewed records (proposed)

```json
{
  "id": "override_gold_example_id",
  "source": {"dataset": "SGD", "split": "train", "dialogue_id": "original_id", "turn_index": 4, "service": "Service_1"},
  "history": [{"speaker": "USER", "utterance": "Earlier utterance"}],
  "current_user_utterance": "Actually, change to Paris, but keep Friday.",
  "value_spans": [{"start": 20, "end": 25, "text": "Paris", "label": "NEW_VALUE", "slot": "destination"}],
  "cue_spans": [],
  "transitions": [{"operation": "UPDATE", "service": "Service_1", "slot": "destination", "old_value": null, "new_value": "Paris", "evidence_span_ids": [], "resolution": "ANNOTATOR_REVIEW_REQUIRED"}],
  "links": [],
  "difficulty": "L1",
  "annotation": {"status": "UNREVIEWED_EXAMPLE", "guideline_version": "v0.1", "annotators": [], "adjudicator": null}
}
```

The JSON is an **illustrative schema sketch, not gold**. Agent must validate actual indices and ensure `current_user_utterance[start:end] == text`. Change this sketch if necessary to avoid storing invalid offsets; this example's `Paris` slice should be validated before reuse in code or papers.

## 6. Artifact directory convention (Python/CLI only)

```text
OVERRIDE-PROJECT/
  00_DESIGN_AUDIT.md
  01_REQUIREMENTS.md
  02_NLP_TASK_DESIGN.md
  03_DATASET_PIPELINE.md
  data/
    upstream/sgd/         # official pinned source, CC BY-SA attribution
    intermediate/         # heuristic candidates, NEVER gold
    annotations/          # independent human labels, then adjudicated gold
    processed/            # deterministic BIO datasets + split manifests
  scripts/
    audit_sgd.py          # ALREADY IMPLEMENTED + UNIT TESTED on synthetic fixture
    prepare_annotation_pilot.py  # IMPLEMENTED + SYNTHETIC-TESTED; not yet run on real SGD
    ...                   # future alignment and training scripts
  tests/
    test_audit_sgd.py     # ALREADY IMPLEMENTED (synthetic records)
    test_prepare_annotation_pilot.py  # synthetic-only sampling validation
  reports/
    ...                   # actual audit, label counts, evaluation (not yet populated)
  configs/
  src/override/
  README.md
  LICENSE
  contributions/
```

`README.md`, `LICENSE`, model/training scripts, actual datasets, figures and final public repository are **planned, not completed**. Avoid auto-creating dozens of unnecessary empty files. The final repository must contain only materials required to reproduce and explain the work.

## 7. Academic safeguards and hard gates

| Gate | Need to show to declare PASS | Status now |
|---|---|---|
| D0 | **Real** SGD train audit JSON, pinned commit, source file checksums | NOT RUN (external source not downloaded here) |
| D1 | Provenance-preserving unreviewed candidate inventory; false positives sampled | CODE READY, REAL DATA NOT RUN |
| D2 | Pilot sampling plan with real counts and strata | CODE READY, REAL DATA NOT RUN |
| D3 | Independent human annotation and adjudication evidence | NOT RUN |
| D4 | Frozen dialogue-grouped gold splits and duplicate audit | NOT RUN |
| D5 | Label alignment tests on adjudicated real records | NOT RUN |
| D6 | No current-gold/future-state inference leakage, matched experiment datasets | NOT RUN |
| D7 | Real per-class scores, failure analysis, checkpoint/config/repro commands | NOT RUN |

**STOP RULE:** No full training until D0–D4 and useful class coverage have been established. No claim that L4/L5 generalize unless there are sufficient adjudicated examples.

## 8. Agent instructions for next step (precise, limited)

**First task for coding agent:**

1. Confirm Python version and clone upstream SGD at a pinned commit, record exact clone URL, commit and hashes.
2. Execute `python -m unittest discover -s tests -v`, then `python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit`.
3. Open `sgd_audit_summary.json`; inspect at least several candidates per candidate group manually, including false positives and negatives. Do not change upstream raw JSON.
4. Produce `reports/D0_D1_FACTUAL_FINDINGS.md` with **measured counts only**, selected examples and limitations; include whether offsets are valid and class balance is plausible.
5. STOP and return evidence for human decision before finalizing cue labels or training models. Agent must not call pseudo-labels gold or auto-mark quality gates PASS.

## 9. External sources

1. https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
2. https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/dstc8.md
3. https://github.com/google-research-datasets/dstc8-schema-guided-dialogue/blob/master/LICENSE.txt
4. https://ojs.aaai.org/index.php/AAAI/article/view/6394

**Next intended phase, subject to successful real data audit:** execute the implemented blinded pilot sampler, obtain independent human annotation and adjudication, then freeze a trustworthy gold set before model experiments. **Not a website.**
