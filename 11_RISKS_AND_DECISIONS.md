# 11 — Risk Register / Decision Log

**All status labels mean planned mitigation unless evidence exists.**

| ID | Risk | Severity | Mitigation / evidence needed | Owner gate |
|---|---|---|---|---|
| R01 | Other group chooses same project/dataset | CRITICAL | recheck current P2 sheet, preserve snapshot, seek instructor clarification for conflicts | G0 |
| R02 | SGD spans do not contain OVERRIDE labels | CRITICAL | honest candidate mining + A/B human annotation, no pseudo-label-as-gold | G1–G2 |
| R03 | Restore/keep cases too rare | HIGH | frequency report, diagnostic-only challenge, narrowing decision with owner | G2 |
| R04 | Gold current/future state leaks to model | CRITICAL | explicit input allowlist, unit checks, chronological context, parity tests | G3–G5 |
| R05 | Dataset is trivial lexical keyword task | HIGH | hard negatives, no-change controls, label-specific exact span-F1 | G4 |
| R06 | Annotation ambiguity/within-head overlap | HIGH | span adjudication, agreement report, two-head BIO plus overlap abort | G2 |
| R07 | Underpowered evaluation | HIGH | disclose class support, document confidence limitations, no F1 claim for zero support | G5 |
| R08 | Source license/raw data upload mismatch | HIGH | record upstream CC BY-SA 4.0, separate code license, review republication | G6 |
| R09 | Beautiful but irrelevant website consumes time | MED | website removed from scope, CLI + real evidence is assessed output | G0 |
| R10 | AI agent invents benchmarks, commits or contributors | CRITICAL | exact command logs and file hashes, reviewer sign-off and verifiable git diff | all |
| R11 | P1 rubric mistaken for P2 rule | HIGH | requirements source register differentiates P1 vs P2 | G0 |
| R12 | Dataset sampler enriches positives & biases prevalence | HIGH | label selection policy; never use pilot prevalence as corpus estimate | G2 |

## Locked decisions
- Project name: OVERRIDE; team Developers; English SGD as initial source; CLI-only assessed deliverable.
- Primary evaluation: VALUE/CUE strict span extraction; state edits and reference links separately.
- No finalized task labels, model metrics, grade prediction or source frequencies until evidence.
- L1–L5 kept as scope/diagnostics with rare categories conditional.

## Decision log (dated entries: `old decision -> evidence -> new decision`)

- **2026-10-28 — Code license adopted.**
  `old decision:` MIT template only in `legal_templates/`, adoption pending copyright-holder approval; root LICENSE absent. `evidence:` project owner approval given 2026-10-28 (course P1 rubric expects a LICENSE in a public repo). `new decision:` **root `LICENSE` published = unmodified standard MIT text, code only**; SGD data remains CC BY-SA 4.0 and must never be described as MIT-licensed (`15_DATA_LICENSE_AND_ATTRIBUTION.md` governs data).

- **2026-10-28 — Taxonomy narrowing after real D0 audit.**
  `old decision:` all 4 CUE classes (UPDATE/CANCEL/KEEP/RESTORE) treated as potentially trainable BIO heads, L1–L5 all in scope, negated-cancel edge case E05 in guidelines. `evidence:` real train audit (commit `e852981a`, `reports/D0_D1_FACTUAL_FINDINGS.md`): explicit-cue revision pool ≈2,462 turns (raw regex 14,308 is ~80% bare-"No" false positives); CANCEL pool 117 turns but explicit user-directed cancels near-absent (hypotheticals + third-party cancellations dominate); **negated-cancel = 0/164,982 user turns**; RESTORE genuine support in the tens (187/208 "back to" hits are travel sense). `new decision:` **primary trained heads stay VALUE + CUE but `UPDATE_CUE`/`KEEP_CUE`(+`NEW_VALUE`/`OLD_VALUE`/`KEPT_VALUE`) are the trainable scope; `CANCEL_CUE` restricted to explicit user-directed instructions (expect tiny support, class may be demoted after pilot); `RESTORE_CUE` (L4) and E05 negated-cancel become a hand-verified DIAGNOSTIC set, separately reported, never used to inflate macro-F1.** Pilot stratification proceeds with these expectations; final call after D2 pilot + human review. This narrows L3–L5 to diagnostics; it does not change the research question.

- **2026-10-28 — Source pin and redistribution policy.**
  `old decision:` SGD to be downloaded and pinned before D0. `evidence:` clone + audit executed; commit `e852981ae34990f4358979625854259302feaa78`, CC BY-SA 4.0 confirmed from `LICENSE.txt`. `new decision:` raw SGD stays OUT of the public repo (`data/upstream/` gitignored); only hashes, aggregate counts and license/citation notes are published; annotated derivatives require the `15_DATA_LICENSE_AND_ATTRIBUTION.md` redistribution review before any release.

## Open decisions and release conditions
- P2 updated rubric and deadline unknown: do not infer.
- Number of team members, student IDs and GitHub usernames unknown: contribution files templates only.
- Training encoder and hardware config TBD after data feasibility.
- Final taxonomy, class support and annotation budget must be approved following D0–D2 real pilot.

Document each real change in a dated entry with `old decision -> evidence -> new decision`, not silent scope drift.
