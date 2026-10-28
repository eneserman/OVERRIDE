# 08 — Testing, Quality Gates and QA

## What test status means
Current tests are synthetic unit tests for data tools. They are **not** validation of real SGD or model quality. A gate cannot be marked `PASS` unless outputs and evidence files exist.

## Gates
| Gate | Required evidence | Blocking? |
|---|---|---|
| G0 scope/collision | screenshot or recorded contemporaneous P2 task/dataset check; course requirement register | Yes for final registration |
| G1 source | pinned upstream commit, SHA-256, unchanged data, audit summary and false-positive review | Yes for annotation |
| G2 pilot | blind A/B annotations, offset validator, disagreements, adjudication log, per-class support | Yes for gold freeze |
| G3 gold/splits | frozen hashes, dialogue-family independence, no near duplicate or rephrased leakage | Yes for ML |
| G4 baseline | measurable nontrivial task, sufficient positives/negatives, repeatable baseline | Yes for expensive training |
| G5 model | real train logs, exact same test and inputs allowed by ablation contract | Yes for claimed research conclusion |
| G6 delivery | public repo, license review, contributor diffs, presentation evidence | Yes for submission |

## Test layers
- Unit: state diffs classify candidates only; offset validation; no cue inference from string reappearance; negative operation polarity metadata.
- Integration: source audit, annotation packet blind fields, A/B review packet normalization/agreement, annotations validation, deterministic splits, evaluation CLI.
- ML: small synthetic tensor shape/label masking sanity checks plus real-train/dev correctness when gold exists; deterministic seed checks.
- Scientific: pretrained weights not confused with trained results; no test-set tuning; baselines share evaluation code; no zero-support class treated as evidence.

## Repro commands
```bash
python -m unittest discover -s tests -v
python -m compileall -q scripts tests
```
Commands for the real dataset are in `README.md`; only report they passed after execution against actual data.

## Review questions for each pull request
What changed? Which test failed before and passed after? Source data or offsets changed? Potential license breach? Does diff contain credentials, generated reports, fake scores, model weights? Does the code permit gold leakage or private hint leakage? Can another team member reproduce on a fresh checkout?

## v0.6 additional regression gates

1. Reject future or out-of-order history messages.
2. Reject incomplete / fake gold provenance (non-SGD source, repeated reviewer IDs, missing adjudication log ID).
3. Confirm both reviewers are comparing the same text, history, and source.
4. Never overwrite any non-empty annotation output directory.
5. Require content-bound gold SHA-256 and test-only frozen evaluation.
6. A preflight PASS is a software handoff check, **not** model accuracy or readiness to submit.
