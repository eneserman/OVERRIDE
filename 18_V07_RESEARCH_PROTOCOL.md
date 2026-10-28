# OVERRIDE v0.7 — Research-grade dataset protocol

**Status: BUILD VERIFIED, NOT ACADEMIC GOLD.** This is an evidence-first workflow. Neither an AI annotator nor a deterministic generator replaces independent human annotation and adjudication. No performance score, professor approval or 'perfect' result is claimed.

## 1. Research question and falsifiable hypothesis
Given the current user message and preceding dialogue, can a token classifier locate explicit old/new/preserved values, references and correction/keep/cancel/restore cues? H1: dialogue history improves exact-span F1 on *real, human-adjudicated context-dependent examples* compared with current-turn-only input. H2: synthetic warm-start improves real low-resource performance compared with no synthetic warm-start. Both may prove false and must be tested; synthetic template evaluation is **not** evidence for H1/H2.

## 2. Evidence tiers — never combine denominators silently

| Tier | In this package | Status | Permitted use | Prohibited claim |
|---|---:|---|---|---|
| Real SGD turns | 100 | Unlabeled review packets | Sampling/annotation pilot | '100 gold labels' |
| AI A/B on those real turns | 100 × 2 | AI_DRAFT | Triage; debugging; comparison suggestions | 'two human annotators', 'inter-annotator agreement' |
| Generated train | 504 | SYNTHETIC_PROGRAMMATIC | Warm-start, training ablation | 'real SGD training labels' |
| Generated dev | 126 | SYNTHETIC_PROGRAMMATIC | Engineering tuning only | 'independent real-world dev' |
| Generated challenge | 126 | SYNTHETIC_PROGRAMMATIC | Held-out template regression sanity tests | 'research-grade external test' |
| Human-adjudicated real SGD gold | **0** | Missing | Must be produced before claims of measured generalization | Pretending completed |

## 3. Defensible label semantics
Two independent heads, **VALUE** (`NEW_VALUE`, `OLD_VALUE`, `KEPT_VALUE`, `REFERENCE`) and **CUE** (`UPDATE_CUE`, `CANCEL_CUE`, `KEEP_CUE`, `RESTORE_CUE`). A span can be emitted only when its words occur in the current user utterance, with verified `[start,end)` offsets. `OLD_VALUE` is not magically projected from history into the current text. `KEPT_VALUE` applies only when the kept value is explicit in the current turn. 'Keep everything else' has a KEEP cue but not invented KEPT spans.

Cue polarity is not inferred from label alone: `Don't cancel` has CANCEL_CUE + `polarity=NEGATED` but **must never** produce `CANCEL_INTENT`. State operations (`ADD`, `UPDATE`, `KEEP`, `RESTORE`, `CANCEL_INTENT`, `UNRESOLVED`) are separately predicted/reasoned; token tags are not state changes. Mere topic switch is not necessarily cancellation, and selecting a system proposal is not necessarily revision.

**Scope warning:** Some synthetically generated example templates, including negations and elliptical references, remain human-reviewable semantic judgments. Their programmatic offsets are correct, but **that does not prove semantic validity**. Do not report the synthetic labels as independently validated.

## 4. Nonnegotiable human review protocol
1. Show the **unlabeled official SGD messages** and only past context to two identifiable reviewers. Keep the private sampler hints and AI suggestions out of initial reviews. Reviewers must not discuss examples before submission.
2. Both reviewers mark every example (explicit negative allowed), two layers, cue polarity, operation, target history index and uncertainty. Save immutable, timestamped original files. Avoid fabricated identities.
3. Align by source id, SHA256 of current message + history. Check exact offsets and independent record completeness, compute per-class exact span agreement (not just overall accuracy), cue polarity, and operation disagreement.
4. Adjudicate *all* disagreements with a decision, rationale and reviewer evidence. Also audit a stratified sample of agreements to catch shared rule errors. Unresolved cases stay unresolved and are not forced into fake certainty.
5. Make gold only after actual review evidence and documented resolution. Gold class support, confidence and conflicts must be disclosed. If human review is impossible, present the outcome honestly as **AI-assisted weak supervision**, not validated human gold.
6. Obtain an independent human-read **real SGD** test set (different dialogue families from train/dev) before any academic generalization claims. Freeze the raw test, do not inspect model test errors repeatedly for tuning. If dev/test source folders from SGD are used, preserve the official split boundaries as an additional safeguard.

## 5. Feasibility and stop/go gates
- **Gate A — format**: JSONL parse, unique ids, source provenance, all spans match slices, class vocabulary, backward-only links, all synthetic layers present. **PASS in packaged generator.**
- **Gate B — real data sampling**: real official SGD downloaded and checksummed, multi-domain/multi-level candidates mined with `scripts/mine_sgd_revision_candidates.py`. **NOT DONE** in the present environment.
- **Gate C — human gold**: authentic independent reviews + adjudication logs, semantic spot checks, per-class/level counts. **NOT DONE**.
- **Gate D — support**: predeclare per-class targets after mining pilot (suggest starting investigation around 30 adjudicated examples for each important span class and enough positives/negatives per difficulty level). Targets are *design targets*, not arbitrary guarantees of statistical power. If coverage low, reduce supported claims/scope and report sparse classes.
- **Gate E — non-leaking test**: family-disjoint real test, locked manifest hash, no synthetic template descendants or source-dialogue siblings across train/dev/test. **NOT DONE**.
- **Gate F — reproducibility & experiments**: baseline CRF, transformer contextual/non-contextual, at least 3 seeds if compute allows, same real gold test, error cases, class/level F1, state consistency, ablations, software versions, license, commits. **NOT DONE**.

No `PASS` on A alone qualifies as a passing grade on B–F.

## 6. Evaluation reporting requirements
Primary: exact-match entity/span precision, recall, F1 per label, each head and micro/macro, computed on human-adjudicated **real test only**. Secondary: cue polarity, supported state-transition accuracy, and pronoun/referent resolution, only where actual gold exists. Report positive counts, actual examples, confidence intervals or bootstrap uncertainty when useful, missing classes as **not measurable**, failures and exclusions; never substitute 0% for unavailable gold.

Experimental controls: identical train/test/seed for 'context-aware vs no history'; identical eligible real gold for 'synthetic warm start vs real-only'; explain long-context truncation; mask history tokens for current-turn token loss; whole-dialogue split. Synthetic challenge F1 always clearly labeled **synthetic diagnostic** and segregated from main results.

## 7. Licensing, provenance and redistribution
Original Google SGD: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue ; CC BY-SA 4.0; cite Rastogi et al., AAAI 2020. Attribution, licence notice, adaptation indication and downstream share-alike review are required. Never imply official SGD supplies OVERRIDE revision gold. Synthetic code/text is separately generated; `source.dataset=SYNTHETIC_COMPOSITION`. Current 100 source-pilot examples are derived from user-provided files; official raw upstream hash not independently verified in this execution environment.

## 8. Ethical/research integrity
No fabricated human reviewers, never rename `AI_SIMULATION` to `HUMAN`, and do not call synthetic examples 'real conversations'. Declare AI assistance in methodology. Document exact handling of unreconciled cases. A challenge split generated from disjoint templates but a common generator is **not** proof of out-of-distribution robustness.
