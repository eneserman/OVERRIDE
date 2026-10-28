# AGENT D5 — Train Reproducible Baselines and Context-Aware Token Models

Prerequisite: G3 approved gold+immutable split. Read `02`, `05`, `06`, `07`, `08` docs and manifest first. If no gold, STOP. No website.

1. Create only necessary modular Python ML code under `src/override/` and `scripts/` (train, infer, data collator, tokenizer offsets, metrics), plus hardware-specific dependency lock.
2. Implement rule baseline and CRF if possible; document if a baseline is infeasible. Then fine-tune a small encoder token classifier, one or two heads, with precise justification of label mapping.
3. Implement last-turn-only and history-aware settings **on exactly the same training/eval example IDs**, with no oracle future/current SGD `frames.state` in inputs.
4. Apply loss masks to history/special/padding and alignment policy to subtokens. Check accuracy of offsets and mask with synthetic tests before GPU training.
5. Report real class supports, sample counts, preprocessing rejects, context truncation and seed(s). Model selection on validation only.
6. Log exact commands/hyperparameters, package versions, hardware, random seeds, runtime, checkpoint hash. Write factual `reports/D5_TRAINING_REPORT.md`.
7. If no significant improvement or major label leakage appears, report it honestly; do not tune test results. STOP before final test evaluation.
