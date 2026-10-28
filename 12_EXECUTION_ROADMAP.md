# 12 — Implementation Roadmap and Dependency Gates

This is a **handoff roadmap**, not a promise of background work. Coding agent must stop at each hard gate and return evidence.

| Phase | Goal | Files/tools | Ready to proceed when |
|---|---|---|---|
| D0 | Acquire/pin SGD, audit source | `audit_sgd.py`, source SHA, D0 prompt | Real logs and counts, no systemic format error |
| D1 | Candidate mining + blind pilot packets | `prepare_annotation_pilot.py`, D1–D2 prompt | Reproducible packets; candidate artifacts private |
| D2 | Pilot independently annotated & adjudicated | `13_ANNOTATION_GUIDELINES.md`, D3 prompt | Class support/agreement and go/narrow/no-go decision |
| D3 | Freeze gold+splits | validator/split scripts and D4 prompt | No leakage, legal sharing, frozen manifest |
| D4 | Baseline and Transformer training | model protocol + D5 prompt | Same test, visible genuine logs |
| D5 | Robust evaluation/ablation | strict span scorer + D6 prompt | Evidence of differences, failure analysis |
| D6 | Repo and PPTX submission | D7 prompt + submission checklist | Public license-reviewed repo, contributions, actual scores |

## Phase reporting contract
Each agent message contains (1) what changed; (2) command and exit code; (3) exact paths; (4) source SHA-256 and split; (5) results that were **measured**; (6) unresolved blockers; (7) explicit `GO / NARROW / NO-GO`. No phase bypass.

## Stop semantics
Agent may prepare downstream templates in advance, but must **not populate training metrics, finished labels, annotated human decisions or pptx results without evidence**. When D0 empirical review shows insufficient examples, stop and propose a narrowed task before any model runs. Do not relabel a heuristic candidate as gold to keep schedule.
