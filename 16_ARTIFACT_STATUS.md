# 16 — Artifact Inventory & Evidence Status

**Updated 2026-10-27 (v0.6 integrity hardening).** The project is a **documentation/CLI tooling handoff**, not a completed academic implementation.

| Artifact | Status | Evidence |
|---|---|---|
| Requirements and design audit | Complete draft | `00`, `01` docs |
| Two-head token schema and L1–L5 plan | Provisional design | `02` |
| Dataset pipeline and initial tools | Code exists | `03`, `scripts/audit_sgd.py`, `scripts/prepare_annotation_pilot.py` |
| Human annotation pilot plan | Draft | `04`, `13` |
| System/model/eval/QA architecture | Complete design docs | `05`–`12`, `14`–`15` |
| Human review packet converter + agreement | Tested on synthetic fixtures | Does not create human gold |
| Annotation validator / split freezer / scorer | Tested on synthetic fixtures | Python scripts + tests (not model results) |
| Real SGD train D0 audit | **RUN 2026-10-28** | pinned `e852981a`, 127 file hashes, 16,142 dialogues, 242,267/242,267 valid offsets — `reports/D0_D1_FACTUAL_FINDINGS.md` |
| Human-reviewed gold | **NOT CREATED** | independent reviewers and adjudication pending |
| Final label taxonomy | **NARROWED 2026-10-28, not frozen** | D0 evidence + decision log in `11`; pilot/human review pending |
| Model checkpoints and comparison | **NOT TRAINED** | dependent on gold |
| State resolver / actual L4–L5 performance | **NOT IMPLEMENTED** | dependent on gold and sufficient context |
| PPTX with real results | **NOT CREATED** | dependent on experiments |
| Public GitHub + student contribution diffs | **REPO LIVE (2026-10-28), contributions pending** | https://github.com/eneserman/OVERRIDE (public, CI green); real per-student contribution files still template-only |
| P2 collision check | **CHECKED 2026-10-28 (live sheet): no collision** | Avengers=LID, Group8=punctuation, LucidAI=PII, Ultron=event args; SGD unclaimed. Re-check before submission (10 rows empty) |

**Handoff rule:** All design files and downstream phase prompts are now present; the training code, actual human gold, measured models and numerical PPTX must still be produced after real evidence. Agent can receive all files together, but execute prompts D0 → D1/D2 → D3 → D4 → D5 → D6 → D7 only when previous gate is evidenced. Do not fabricate missing artifacts to make inventory green.

**v0.6 changes:** stronger provenance validation, equal-source reviewer checks, overwrite guard, immutable-gold checksum, per-split class supports and safe held-out evaluation. Still NOT a trained model, true human annotations, full SGD audit, verified topic collision check or final submission.


## v0.8 current status (2026-10-28)
Code baseline: EXECUTED ON SYNTHETIC ONLY; measured values in `reports/experiments/V08_MEASURED_SYNTHETIC_BASELINE.json`. Published external DST JGA in literature file, not our results. Full raw SGD: NOT PRESENT. Frames: NOT PRESENT. Authentic human gold and prospective frozen real test: NOT PRESENT. Main model real F1: NOT MEASURED. See `28_V08_EVIDENCE_AUDIT.md`.
