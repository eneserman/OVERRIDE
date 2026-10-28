# OVERRIDE — Course Requirements and Evidence Register

**Version:** 1.0 | **Date:** 2026-10-27 | **Status:** SOURCE-BASED REQUIREMENTS; P2 RUBRIC NOT YET VERIFIED  
**Team:** Developers | **Course:** NLP — Project 2  
**Purpose:** Prevent an AI coding agent from silently treating older Project 1 rules as verified Project 2 grading rules.

## 1. Source hierarchy and provenance

| ID | Source | Applies to | Confidence | What it establishes |
|---|---|---|---|---|
| P2-A | Instructor's “About project 2 datasets, downstream tasks, and presentations” announcement, supplied in chat | P2 | Direct | Token classification focus; group records dataset + downstream task in P2 sheet; novelty/difficulty and technical depth emphasized; duplicate tasks constrained |
| P2-B | Blackboard P2 sheet screenshot supplied in chat | P2, as of screenshot | Direct but time-sensitive | Group Developers at row 17 was blank; recorded topics: Turkish-English code-switching LID, punctuation restoration, financial PII BIO |
| P2-C | Blackboard assignment submission screenshot supplied in chat | P2 submission | Direct | Submit **GitHub URL first**, then **PPTX** |
| P2-D | Instructor's later spoken warning relayed by the student | P2 | User-reported; treat as binding until clarified | If students in the same section submit the same project, both receive zero |
| P1-A | Instructor's “Project Instructions” announcement, expressly for first project / TEXT CLASSIFICATION, supplied in chat | **P1, NOT AUTOMATICALLY P2** | Direct for P1, precedent only for P2 | 50% presentation + 50% repo, subscales, public GitHub structure, exact submission expectations, presentation time details |
| COURSE | POS/NER slide deck supplied in chat | Course reference | Direct | POS, NER, BIO, HMM/CRF/Transformer examples; **not** a Project 2-specific grading contract |

**Discrepancy policy:** If old P2 announcement permits up to three groups for one *task* while a newer warning says same project within a section gets zero, apply the **more restrictive no-collision practice**. Only the instructor can definitively interpret what counts as “the same”. Dataset uniqueness is separately a P1 rule and safest to enforce for P2 as well.

## 2. Confirmed P2 constraints (do not reinterpret)

1. The learning focus is **TOKEN CLASSIFICATION** (not an ordinary text-level classifier). Our **primary trained and evaluated task must predict token/span labels**.
2. Register Developers' precise **dataset** and **downstream task** in the P2 Google Sheet. The screenshot from 2026-10-27 is **not** a live status check.
3. The instructor discourages basic POS and narrow NER baselines, saturated/easy benchmarks, tiny pre-sanitized datasets, minimal class variety, or unexplained synthetic data; difficult, well-justified tasks and careful cleaning have better prospects.
4. Provide substantive technical explanation of methodology, dataset origin, annotation quality, task difficulty, models, comparisons, limitations and evaluation. Questions/comments can challenge these choices.
5. P2 assignment submission entry starts with the GitHub repository URL, followed by PPTX presentation material.
6. **Collision risk is a stop condition:** Before final P2 registration and again before submission, check all visible current P2 selections; if topic/dataset similarity is not obvious, obtain instructor confirmation. Do not claim absolute uniqueness from a screenshot.

## 3. P1 presentation and repo rubric — quality standard only, not validated P2 scale

- P1 overall: **Presentation 50%; implementation repository 50%**.
- P1 presentation factors: **Technical depth 50%, fluency 25%, pace 25%**; questioning can modify technical-depth judgment.
- P1 time rules: **<2 min = 6; 2–3 min = 5; 3:00–3:15 = 3; by 3:30 = 0/interrupted** (as stated by instructor). Do **not** state these as confirmed P2 limits without checking.
- P1 repository factors: **Correctness 20%, data novelty 30%, problem/task novelty 30%, rigor 20%**.
- P1 data-novelty remarks: direct clean Kaggle 2/5; direct Hugging Face 3/5; independently cleaned non-tiny data with reproducible script may obtain higher scores; duplicating another group's dataset risks zero in P1.
- P1 required public repo content: README explaining directories/scripts; documented preprocessing with runnable script; training scripts if any; raw + cleaned data; `LICENSE`; one `contributions/STUDENT_NAME_STUDENT_ID_GITHUB_USERNAME.md` per student, backed by actual GitHub commit diffs. An external source license may require attribution/share-alike and may restrict redistribution; obey the license and obtain instructor permission if raw data cannot be published lawfully.
- P1 penalizes extra unnecessary files and unreadable, non-functional code. Do not fake results, commits, training traces, datasets, or team contributions.

**Safe project policy:** Build to these repo and research standards, but do not label the exact P1 percentages and time limits as P2 assessment facts.

## 4. OVERRIDE academic deliverables

**Primary output (non-negotiable):** per-token or exact-character-span identification of user-stated revision cues and values/references, scored on held-out adjudicated examples.

**Secondary outputs:** role/slot linkage, state transitions, history-reference resolution and optional terminal/JSON traces. A website or mobile app is NOT required by the provided course instructions. Secondary outputs cannot substitute for primary token-classification evaluation.

**Research proof requirements:**
- Published SGD provenance, raw schema inspection, data license and documented transformation.
- New annotation guidelines, annotator agreement, adjudicated gold labels, split manifest and class counts.
- Rule/CRF/Transformer comparison; at least one last-message vs context-aware ablation on exactly matched examples.
- Span-level P/R/F1, per-class counts/F1, difficult-case results and honest error analysis.
- Reproducible scripts with frozen config, deterministic seeds where possible, checksums and tests.
- Presentation that can be explained and defended without reading from slides.

## 5. Delivery format — CLI/code first (confirmed project decision)

- Project output will be a **Python implementation repository** with preprocessing, training, evaluation, inference and machine-readable reports; no React, Next.js, Streamlit, mobile or web-server requirement is assumed.
- Demo is a reproducible **terminal command** loading the trained model and highlighting/printing labeled spans plus optional state-change trace. PPTX may use recorded terminal evidence and static figures.
- Adding a polished web interface is **out of scope** until research/evaluation requirements are complete and the project owner explicitly reauthorizes it. The instructor did not request an app or website.
- Read `03_DATASET_PIPELINE.md` before building a training pipeline; pseudo-labeled candidate extraction is not equivalent to validated gold.

## 6. Known gaps / NOT YET CONFIRMED

- P2's **exact presentation time limit**, numeric rubric, deadline and number of team members.
- Updated live P2 sheet selections; whether SGD/OVERRIDE or a substantially similar revision task has been selected by another group.
- How many naturally occurring SGD examples support each planned new label and L1–L5 scenario.
- Annotator agreement and actual cleaned example counts.
- Hardware training budget, model performance, license compliance of any additional dataset.

These are **blockers to verify**, not assumed facts. The coding agent may gather evidence but must not mark them completed without artifacts.

## 7. Acceptance checklist for academic readiness

- [ ] **A0:** Current P2 sheet checked; no known project or dataset collision (instructor consulted if uncertain).
- [ ] **A1:** Pilot confirms viable token-classification label frequencies and agreement; annotation guideline is frozen.
- [ ] **A2:** Versioned, defensible gold data with sources, offsets, test split and reproducible cleaning.
- [ ] **A3:** Working primary token/span model, baseline and matched context ablations.
- [ ] **A4:** Credible results including negative controls, rare classes, failure cases and no gold-state inference leakage.
- [ ] **A5:** Clean public repo and legally distributable raw/clean data or documented instructor-approved alternative.
- [ ] **A6:** Real team member contribution reports + diff evidence.
- [ ] **A7:** Confirmed P2 time/rubric, PPTX rehearsal and GitHub-first submission.

**Status as of 2026-10-27: these acceptance checks have NOT been performed.**
