# OVERRIDE — v0.6 /truthmode Technical Audit & Risk Gates

**Scope:** All 50 files from the v0.5 handoff were inspected for structure; source scripts, core annotations contracts, evaluation flow, unit tests, prompts, data licensing statements and submission expectations were checked. This is an **engineering preflight**, NOT a scientific reproducibility certification.

## Overall decision

**HANDOFF: CONDITIONAL PASS** if local tests pass. **MODEL/ACADEMIC SUCCESS: NOT DETERMINABLE YET**. The packet can be given to a coding agent for D0 and step-by-step implementation, but cannot be sent as a finished NLP assignment. Zero risk and full credit are not guaranteed.

## Actual defects addressed in this version

| Ref | Defect in prior v0.5 | v0.6 protection |
|---|---|---|
| V06-01 | No checked bound on history turn indexes in annotation validator | Reject future, duplicate or reversed indexed history |
| V06-02 | Annotation agreement permitted same example ID but differing text/history | Verify same source, history, utterance, family and distinct reviewer IDs |
| V06-03 | Annotation pilot generation might overwrite a partially reviewed output directory | Fail when destination contains any existing files |
| V06-04 | Gold validator accepted `ADJUDICATED` alone without independent-review references | Require unique reviewer IDs, adjudication log ID, SGD/train source and matching dialogue family; human evidence still needs manual audit |
| V06-05 | Split manifest bound only IDs, not gold labels/content | Add stable full-content gold SHA-256 and supports by layer/split |
| V06-06 | Evaluator could be used to report train predictions as a test score | New `evaluate_frozen_test.py` checks gold hash, manifest, ID partition, family assignment and exact test prediction IDs |
| V06-07 | Lacked a single deterministic handoff preflight command | `scripts/preflight_handoff.py` runs syntax/tests, inventories required files and shows scientific blockers |

## Outstanding blockers — cannot be solved by documentation alone

1. **No full real SGD audit completed.** Prior scripts run on synthetic cases; one real official raw-file download attempt in this environment failed. Coding agent must fetch the source and run full D0, pin commit/filename digests, and inspect actual counts and source behavior.
2. **No real human-labeled gold corrections, cancellation, keep or restore spans.** SGD itself provides service slot states, noncategorical spans and different user turns, not OVERRIDE's bespoke supervision. D1–D3 cannot be passed by generating pseudo-labels or having one AI impersonate two reviewers.
3. **Rare L4/L5 cases are an empirical risk.** The initial task scope cannot assume enough examples. Only observable support after pilot authorizes a final supervised taxonomy.
4. **No trained CRF/Transformer models or benchmark metrics.** D5 and D6 are planned; any claimed accuracy now would be invented.
5. **Not a proved original research contribution.** Self-curated, genuinely cleaned/annotated examples and carefully reported ablations are required, and may still not guarantee novelty points.
6. **P2 topic uniqueness not checked live** and exact P2 numerical rubric/slide time not confirmed. The published detailed percentage scale was explicitly for P1.
7. **Release not complete.** No actual public GitHub contributions, licensed final source/data export, code LICENSE, and results-backed PPTX. The chosen software code license awaits real contributors' approval.

## Ordered release gates

- **G0:** `python scripts/preflight_handoff.py` passes; give coding agent master prompt; D0 only.
- **G1:** Real SGD source pinned, complete audited source counts, alias/missing spans noted, repeatability verified.
- **G2:** Blind reviewer packets plus TWO independent real reviewers and documented disagreements; core label support measured.
- **G3:** Frozen taxonomy, valid adjudication evidence and gold split with per-class supports; hashes immutable.
- **G4:** Fair matched rule-based/CRF/Transformer evaluations, no future-turn / gold-state leakage.
- **G5:** Frozen test-only scoring, complete traceable run metadata, per-class error analysis and limitations.
- **G6:** Live P2 collision check, actual public repo and licensing verification, measured PPTX and contribution evidence.

If any gate fails: report **BLOCKED** or **NARROW**, never force progress by inventing labels/results.

## Metrics interpretation

Exact-span F1 alone does not prove correct dialogue-state edits, referent resolution, or that complex backtracking works. These require separate, real gold-based metrics. The enriched reviewer queue is NOT a representative random sample of real conversations; its class proportions must never be passed off as prevalence estimates. Test-set adequacy depends on observed support, not headline number of dialogues.
