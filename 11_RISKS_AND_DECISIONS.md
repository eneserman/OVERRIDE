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

## Open decisions and release conditions
- P2 updated rubric and deadline unknown: do not infer.
- Number of team members, student IDs and GitHub usernames unknown: contribution files templates only.
- Training encoder and hardware config TBD after data feasibility.
- Final taxonomy, class support and annotation budget must be approved following D0–D2 real pilot.

Document each real change in a dated entry with `old decision -> evidence -> new decision`, not silent scope drift.
