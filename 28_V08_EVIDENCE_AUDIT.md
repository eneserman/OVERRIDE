# 28 — v0.8 evidence and release audit (2026-10-28)

> **LOCAL STATUS OVERLAY (2026-10-28):** the "SGD NOT DOWNLOADED / hash not assertable" claims below are **superseded on this machine** — official SGD is pinned at `e852981a` with per-file SHA-256 (`reports/SHA256_SGD_TRAIN_FILES.txt`, `reports/V08_UPSTREAM_PROVENANCE.json` = `REAL_SOURCE_VERIFIED`; dev 2,482 / test 4,201 dialogues available). Human gold is still **0** and real F1 still **NOT MEASURED**. See `reports/V08_LOCAL_STATUS_RECONCILIATION.md`.

## Audit conclusion
**TECHNICAL RESEARCH HANDOFF: PASS WITH KNOWN LIMITATIONS.**
**REAL HUMAN GOLD DATASET: FAIL / NOT BUILT.**
**FROZEN REAL EVALUATION: FAIL / NOT BUILT.**
**VALIDATED REAL-WORLD OVERRIDE F1: NOT MEASURED.**

The project's provenance, research protocol, source selection and synthetic diagnostic experiments were materially improved. No 'perfect dataset' claim. Below are measurements made in this environment, separated from publisher-reported literature scores.

## Actually executed experiment
- Trained `sklearn.svm.LinearSVC` with lexical token features; separate VALUE/CUE BIO taggers.
- Input: `504 SYNTHETIC_PROGRAMMATIC` training examples (v0.7), `126` synthetic dev and `126` synthetic challenge examples. This is **not** a BERT, CRF or independent real-world benchmark.
- Strict span matching; decode BIO tags for current turn only. History feature ablation adds lexical hints of past context, NOT a Transformer that understands earlier instructions.
- Exact measured single-seed values in `reports/experiments/V08_MEASURED_SYNTHETIC_BASELINE.json`:

| Evaluation | Condition | VALUE exact-span F1 | CUE exact-span F1 |
|---|---|---:|---:|
| Synthetic dev | Current only | 0.5625 | 0.6574 |
| Synthetic dev | History lexical features | 0.6207 | 0.6667 |
| Synthetic held-out-template challenge | Current only | 0.7586 | 0.2500 |
| Synthetic held-out-template challenge | History lexical features | 0.7857 | 0.2609 |

This cue performance is poor on synthetic challenge. **It is evidence for difficulty**, not high-quality gold or success. Do not report these figures as 'OVERRIDE real dataset' or compare directly with published DST JGA.

## Split overlap audit (synthetic only)
`reports/experiments/V08_SYNTHETIC_LEAKAGE_AUDIT.json` checked literal utterance duplicates and pairwise token-set Jaccard >=0.90: 0 in each pair (train/dev, train/challenge, dev/challenge). This does **not** eliminate structural/template, model-development, or semantic leakage from the shared generator. Challenge remains a development diagnostic.

## Local source availability
- One user-provided pilot of 100 SGD train-split messages; AI suggestion packets already generated; NOT blind/gold.
- Full original SGD repo: **NOT DOWNLOADED**. A raw GitHub download in this environment failed. Agent must actually clone and run `scripts/inspect_upstream_provenance.py`.
- Official Microsoft Frames corpus: **NOT DOWNLOADED**. The portal requires user acceptance and license review; no bypass.
- MultiWOZ 2.4 and Taskmaster-1: **RESEARCHED ONLINE, NOT DOWNLOADED**.
- Real learned model evaluation: **NOT PERFORMED**, because real gold does not exist.

## Engineering gates executed
- Python unittest suite: see `reports/experiments/V08_BUILD_CHECK.json`.
- Scientific pre-registration + new immutable candidate lock script: tested with fixtures but **no true external pool yet locked**.
- Source SHA-based audit script and Frames review-packet extractor: tested with synthetic fixtures; production source not validated.
- GitHub/repo license final choice and original raw redistribution still need review.

## Failure gates
The IDE MUST NOT submit a high-confidence project just because `V08_BUILD_CHECK` passes. Accept release only after (i) downloaded official source/provenance, (ii) real blindly sampled/disjoint heldout, (iii) authentic independent review and adjudication, (iv) adequate class/difficulty coverage, (v) actual CRF/Transformer training and reproducible runs, (vi) real test F1 and honest failure analysis. If conditions fail, reduce claims and report limitations.
