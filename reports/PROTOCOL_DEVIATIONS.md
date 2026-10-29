# Protocol Deviations — EVALUATION_PROTOCOL_LOCK v0.8
# Deviations are recorded here explicitly (lock: "Any deviation must be recorded
# as a protocol violation, not silently applied"). Nothing below is hidden from
# the final evaluation report.

## DEV-001 — Test-363 adjudication scope (60 of 63 disputes not adjudicated)

| Field | Value |
|---|---|
| **Recorded** | 2026-10-29 |
| **Phase at recording** | BEFORE any model training/development (D5 not started; zero model outputs exist) |
| **Locked clause** | `EVALUATION_PROTOCOL_LOCK.md` v0.8 §3 step 1: *"Human-annotate and adjudicate the locked holdout (D3 workflow, two independent reviewers) → prospective test gold."* |
| **Deviating decision** | Joint decision of **both reviewers**: of the 63 test disagreements, **3 are resolved** by the F1/F2 rules (take reviewer B's spans: `SGD-473c2fae903c3d2740`, `SGD-afba777aac592e7d5d`, `SGD-01b297fc690c6a0e2b`); the remaining **60 are NOT adjudicated**. Test reference = only spans both reviewers agreed on; each of the 60 records is reported as **UNRESOLVED**. |
| **Who decided** | reviewer_A_BURAK + reviewer_B_ENES (joint, 2026-10-29); coordinator transcribed only, made no label suggestion. Registered in `reports/D3_ADJUDICATION_DECISIONS_FINAL.md` §4 before training. |
| **Why it is defensible** | (a) two independent human annotations exist for all 363 records — the reviewer input to adjudication is complete; (b) the consensus-only reference is stricter, fully mechanical (intersection), and decided without any model output in existence; (c) the frozen test agreement (`36509d5f…`) measures exactly this human consensus; (d) the 60 records are enumerated and reported, never silently dropped or merged. |
| **Impact on claims** | Final test metrics are computed against a **consensus reference**, not an adjudicated gold. The report states: N=363 records, 303 full-agreement records, 60 unresolved (agreed spans only), with per-label counts of excluded one-sided spans. Any statement like "adjudicated test gold" is therefore forbidden; the correct phrase is "double-annotated consensus test reference". |
| **Reversal** | If the reviewers later adjudicate the 60, that produces a NEW reference version (gold v2), reported alongside — never replacing v1 silently, and only if recorded here before use. |

## Log

| ID | Date | Clause | Summary | Status |
|---|---|---|---|---|
| DEV-001 | 2026-10-29 | §3 step 1 (adjudicate holdout) | 60/63 test disputes → consensus reference instead of adjudication; 3 resolved by rule | REGISTERED before D5 |
