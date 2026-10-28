# Gold dataset release gates — LOCKED until evidence exists

**Current state: NOT GOLD. No human review source files, adjudication logs, locked real-data test or experimental metrics are included.**

A genuine gold release must include the following artifacts **with actual, verifiable values and immutable files**:

1. Official raw SGD source file manifest, SHA256 hashes, source commit, licensing/attribution evidence.
2. Sampler rationale with class/level candidates, true dataset counts and eligibility/exclusion log. No future user/system turns exposed to the reviewer or model.
3. **Two genuine independent human annotations** per included example, with real reviewer IDs and review logs. People must have produced them; field names alone cannot establish this.
4. Real disagreement table and signed-off adjudication decisions; decisions must cite actual current spans and prior context, including explicit uncertainty.
5. Gold schema version + exact offsets + polarity/scope + state transitions only where evidenced. Count per value label, cue label, operation and L1–L5 difficulty.
6. Separate real train/dev/test groups with source dialogue family IDs and hashes. Store synthetic in a different namespace; no synthetic template descendants or AI-draft suggestions ever copied into real test gold without human verification.
7. No leakage across family, paraphrase duplicates, template derivations or metadata. Freezing scripts from v0.6 must be run and inspected; **academic readiness is not inferred by merely generating a manifest**.
8. A baseline plus history/no-history and real-only/synthetic-augmented ablations, same frozen test, macro/per-class/complexity breakdown, honest failure analysis. Avoid overstating low-support labels.
9. Public repo acknowledgments, CC BY-SA review for adaptations, team contributions and runnable reproducibility commands. No fake human contributions.

## Suggested *initial* annotation acquisition priorities (revisit after REAL mining)
Rare spans currently absent from AI suggestions: `OLD_VALUE`, `KEPT_VALUE`; also explicit KEEP, negated CANCEL, resolved distant RESTORE references, and the ADD vs UPDATE boundary. Collect genuine positive evidence *before* declaring eight-class success. `OLD_VALUE` is often absent from the current turn by design; lack of it on real data can be an intrinsic task limitation. Lower the claim or adjust a documented taxonomy only on real evidence.

## Stop if any of these occurs
Gold labels auto-copied from AI without independent verification; review identities fabricated; raw SGD train/dev/test used as if interchangeable; synthetic challenge reported as real held-out test; hidden test used for tuning; no class support but per-class F1 claimed; synthetic texts described as crowdworker-authored SGD. These are **research-invalidating errors**.

## Release decision
`python scripts/audit_research_dataset.py --require-academic-gold` deliberately exits nonzero for this version. An agent must not bypass this gate by editing `academic_gold_ready` from `False` to `True` in code. It must implement evidence-based checks against actual review files when those exist. There is no shortcut to independent human validation.
