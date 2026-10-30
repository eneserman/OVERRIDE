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
| **Implementation (code)** | The locked evaluation entry point accepts this reference only via the explicit `--accept-consensus-reference` flag (`annotation.status=CONSENSUS_REFERENCE`, gated; strict ADJUDICATED-only default preserved and covered by regression tests `tests/test_consensus_reference_v08.py`). Full-gold validation spans official splits `train,dev,test`. Without the flag every entry point still refuses the consensus rows — the deviation can never be applied silently. |

## DEV-002 — Dialogue family key must include the official SGD split

| Field | Value |
|---|---|
| **Recorded** | 2026-10-30, during the single D6 access (after the model freeze `2702a45`, before any prediction or score exists) |
| **What happened** | `build_test_reference.py` aborted (fail-closed, nothing written): 5 family IDs (`10_00028`, `16_00094`, `17_00090`, `20_00011`, `23_00076`) occur both in gold v1.3 (official `train`) and in the holdout (official `dev`/`test`). |
| **Verification** | Raw SGD (`data/upstream/sgd`, pinned commit `e852981a`): SGD restarts dialogue numbering per split; 4,269 of 16,152 dialogue IDs exist in more than one split. The 5 pairs are different dialogues (different services and first turns, e.g. train `10_00028` Events_2 vs dev `10_00028` Media_2+Weather_1). No dialogue is shared; gold v1.3 contains only official-train rows and the holdout only official dev/test rows. |
| **Deviating decision** | Family identity becomes `(official split, dialogue_id)`. Test reference rows carry `dialogue_family_id = "<official split>::<dialogue_id>"`; the leakage check compares train-side families as `train::<id>`. Train/dev gold v1.3 is not changed. |
| **Why it is defensible** | It is a correctness fix of an identity key, not a change of membership, labels, metric or models; the 363 locked IDs and their texts are re-verified against the lock as before; the fix is decided without any model output on the test. |
| **Implementation (code)** | `scripts/build_test_reference.py` (namespaced keys) + regression test `tests/test_test_reference_family_key.py`; committed before the reference is rebuilt. |

## Log

| ID | Date | Clause | Summary | Status |
|---|---|---|---|---|
| DEV-001 | 2026-10-29 | §3 step 1 (adjudicate holdout) | 60/63 test disputes → consensus reference instead of adjudication; 3 resolved by rule | REGISTERED before D5 |
| SCOPE-001 | 2026-10-30 | claims scope (not a membership or metric change) | Taxonomy narrowing, Option A + KEPT_VALUE out of scope (`D5_TAXONOMY_NARROWING_PROPOSAL.md` §4) | ADOPTED before any holdout access |
| DEV-002 | 2026-10-30 | family identity in the test-reference leakage check | SGD dialogue IDs repeat across official splits; family key = official split + dialogue ID | REGISTERED during D6, before any prediction |
