# D1–D2 — Pilot Annotation Preparation (Real Corpus)

**Phase:** D1 candidate mining + D2 blind pilot packet generation | **Date:** 2026-10-28
**Status:** COMPLETE — **STOP for two independent human annotators** | **Decision requested:** GO to human annotation (D3)

All counts below were produced by executed commands. No human labels, gold or model outputs exist yet.

---

## 1. Source and pin

| Item | Value |
|---|---|
| Upstream | https://github.com/google-research-datasets/dstc8-schema-guided-dialogue (official) |
| Pinned commit | `e852981ae34990f4358979625854259302feaa78` (2023-08-07, HEAD of archived upstream) |
| Split used | `train` only (127 files, SHA-256 in `reports/SHA256_SGD_TRAIN_FILES.txt`; identical to values embedded in both audit and pilot summaries) |
| Raw data policy | `data/upstream/` unchanged and gitignored; not redistributed |
| License / attribution | CC BY-SA 4.0; cite Rastogi et al. 2019 (arXiv:1909.05855) |

## 2. Execution log (commands actually run, exit codes)

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `python -m unittest discover -s tests -v` | 0 | `Ran 35 tests — OK` (before and after) |
| 2 | `python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit` | 0 | 16,142 dialogues (see `reports/D0_D1_FACTUAL_FINDINGS.md`) |
| 3 | `python scripts/prepare_annotation_pilot.py --sgd-root data/upstream/sgd --out data/annotations/pilot_v0.1 --sample-size 100 --seed 42 --context-turns 8` | 0 | `Prepared 100 UNLABELED cases from 16142 dialogues` |
| 4 | same command re-run to `C:\...\Temp\opencode\pilot_repro_check` (independent) | 0 | reproducibility check |
| 5 | packet leakage audit (read-only checker, §5) over both A/B packets | 0 | `PROBLEMS= 0` on both |

## 3. Pilot inventory and stratum breakdown

Corpus inventory (`pilot_sampling_summary.json`, `status: UNLABELED_PILOT_ONLY`): 175,780 user-frame records over 16,142 dialogues.

| Stratum (heuristic, NOT gold) | Available records | Selected |
|---|---|---|
| STATE_ADD_OR_CLEAR | 62,608 | 11 |
| NO_CHANGE_CONTROL | 51,799 | 11 |
| FIRST_OBSERVED_CONTROL | 28,760 | 11 |
| POSSIBLE_REVISION | 12,273 | 11 |
| ALIAS_VARIANT | 10,431 | 11 |
| STATE_CHANGED | 8,892 | 11 |
| POSSIBLE_KEEP | 570 | 11 |
| POSSIBLE_RESTORE | 344 | 12 |
| POSSIBLE_CANCEL | 103 | 11 |
| NEGATED_CANCEL | **0** (absent in corpus) | 0 |
| **Total** | 175,780 | **100** (`shortfall: 0`) |

Selection: `seeded_round_robin_across_priority_strata`, seed 42, **max 1 example per dialogue**, `selection_is_not_population_representative: true` (by design — this is an enriched feasibility pilot, never a prevalence sample).

**Uniqueness:** 100 packets ↔ 100 distinct dialogue IDs (verified independently: `UNIQUE_DIALOGUE_TURN= 100`).

## 4. Generated artifacts (private, gitignored — do not publish)

| File | SHA-256 | Role |
|---|---|---|
| `annotator_A_UNLABELED.jsonl` | `55bad855a140650cd279339ab8f19422de8827a7a111e693298a1c0ceda960db` | blind packet, reviewer A |
| `annotator_B_UNLABELED.jsonl` | `55bad855…a960db` (byte-identical to A) | blind packet, reviewer B |
| `PRIVATE_sampling_manifest.jsonl` | `3869bd19f8eeb82b…` | heuristics/strata — **never show to annotators** |
| `pilot_sampling_summary.json` | `f4816bc3e7d8c547…` | counts, hashes, warnings |

A≡B identity is intended (same blind items for two independent reviewers). `annotation.status = UNLABELED`; all `value_spans`/`cue_spans` are `null` ("blank ≠ negative").

## 5. Quality flags — actually verified

- **Reproducibility: PASS.** Independent re-run produced 4/4 byte-identical outputs (annotator A, annotator B, private manifest, sampling summary). Deterministic under seed 42.
- **Leakage audit: PASS (0 problems).** Automated walk of both packets found **no** `state`, `slot_values`, `state_change_candidates`, `change_candidates`, `lexical_flags`, `stratum`, `prior_service_frame`, `operation`, `transition`, `label`, `cue_polarity` keys anywhere; all span layers `null`; `annotation.status=UNLABELED`; **no future turns** (every `history[].turn_index < source.turn_index`).
- **Context window:** ≤8 prior turns per packet (re-verified in construction; no forward context).
- **Provenance:** every record carries `source.dataset=SGD`, `split=train`, `dialogue_id`, `service`, `turn_index` + `dialogue_family_id`.

## 6. False-positive inspection (real samples from the selected 100 — annotators must judge these, not inherit the hint)

| Stratum | Example (unreviewed SGD train text) | What the heuristic saw | Likely truth (to be human-decided) |
|---|---|---|---|
| POSSIBLE_CANCEL | `[84_00039 t30] "…my small brother can't stop talking about it."` | `stop` → cancel regex | **false positive** (discourse "stop talking") |
| POSSIBLE_RESTORE | `[101_00093 t8] "I want to go back to getting tickets for this."` | `back to` | resume-prior-task sense; borderline RESTORE |
| POSSIBLE_REVISION | `[14_00056 t6] "No. Any other options?"` | `no,` | bare refusal + new request; no explicit revision cue |
| POSSIBLE_KEEP | `[79_00098 t10] "…I need the same for 2."` | `same` | genuine retention of ride type (KEPT_VALUE candidate) |
| STATE_CHANGED | `[46_00032 t2] "Ok, how about the weather in Vallejo?"` | `city: sacramento, ca -> vallejo` | implicit revision, no explicit cue (L1/L2 decision needed) |
| ALIAS_VARIANT | `[47_00081 t10] "That's correct. What is the address…"` | `toronto, canada -> toronto\|toronto, canada` | **not a change** (alias expansion) — NO_CHANGE control |
| FIRST_OBSERVED | `[80_00108 t0] "I need a bus"` | — | ADD, not correction |
| STATE_ADD_OR_CLEAR | `[14_00065 t2] "Show me movies in Santa Clara. I would prefer a regular show."` | 2× SLOT_ADDED | first fills → ADD |
| NO_CHANGE_CONTROL | `[81_00040 t18] "Thank you. I'd also like to find an Alfred Hitchcock movie…"` | — | clean negative |

These samples confirm the D0 finding that heuristic strata are **enriched candidate pools with substantial false positives**; human judgment is the only path to gold.

## 7. Legal / licensing

CC BY-SA 4.0 obligations unchanged (see `15_DATA_LICENSE_AND_ATTRIBUTION.md`). Pilot packets contain raw SGD utterances and remain **private**; publication of annotated derivatives requires the redistribution review. No credentials or unrelated downloads included.

## 8. Hard blockers (cannot be solved by code)

1. **TWO genuinely independent human annotators** must label A/B packets per `13_ANNOTATION_GUIDELINES.md` (v0.2, R1–R12 rules). The agent cannot impersonate them; identifiers alone do not prove independence.
2. **Human adjudicator** resolves disagreements (per-item log: `boundary`/`class`/`target`/`polarity`/`ambiguity`).
3. Live **P2 collision check** (Blackboard sheet) before registration/submission — owner action.
4. Team member details for `contributions/` and code LICENSE approval — owner action.

## 9. Recommendation

**GO — to D3 human annotation** with the following recorded expectations:

- 100 blind packets ready; expect high disagreement on borderline strata (POSSIBLE_* pools contain measured false positives) — disagreements are data, not failure.
- Per the narrowed taxonomy (decision log in `11`): `UPDATE_CUE`/`NEW_VALUE`/`OLD_VALUE` are the trainable core; `KEEP` needs explicit language; `CANCEL` is restricted to explicit user-directed instructions; `RESTORE` + negated-cancel remain diagnostic-only. If pilot support for `CANCEL`/`KEEP` collapses after annotation, demote them rather than relabel controls.
- Next artifacts after human review: `normalize_review_packet.py` per reviewer → `annotation_agreement.py` disagreements → adjudication → `data/gold/override_gold_v0.1.jsonl` via `validate_annotations.py --require-gold`. **None of these may be run with fabricated reviews.**

**STOP.** No gold marking, no prefilling, no F1, no training performed or permitted at this gate.
