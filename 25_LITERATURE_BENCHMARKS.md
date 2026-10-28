# 25 — Published reproducible baselines, not our own results

The table below is **literature evidence**. No OVERRIDE model was trained to obtain these values. JGA ≠ span F1. Dataset versions/annotation corrections change results substantially; comparing across dataset versions or claim types would be invalid.

| Paper / repository | Model | Dataset | Metric | Reported score | URL |
|---|---|---|---|---:|---|
| Kim et al. ACL 2020 | SOM-DST | MultiWOZ 2.1 | Joint Goal Accuracy | 53.01% | https://aclanthology.org/2020.acl-main.53/ |
| Kim et al. ACL 2020 | SOM-DST | MultiWOZ 2.0 | Joint Goal Accuracy | 51.72% | https://aclanthology.org/2020.acl-main.53/ |
| Heck et al. SIGDIAL 2020 | TripPy | MultiWOZ 2.1 | Joint Goal Accuracy | >55% (paper abstract) | https://aclanthology.org/2020.sigdial-1.4/ |
| Ye et al. / MultiWOZ 2.4 repo | SOM-DST | MultiWOZ 2.4 | Joint Goal Accuracy | 66.78% | https://github.com/smartyfh/multiwoz2.4 |
| Ye et al. / MultiWOZ 2.4 repo | TripPy | MultiWOZ 2.4 | Joint Goal Accuracy | 64.75% | https://github.com/smartyfh/multiwoz2.4 |
| Ye et al. / MultiWOZ 2.4 repo | TRADE | MultiWOZ 2.4 | Joint Goal Accuracy | 55.05% | https://github.com/smartyfh/multiwoz2.4 |

Important: later repositories may list additional follow-up baselines from newer work; the table attributes exact **repository entries** instead of claiming every number was generated in the original 2022 paper. None is a valid reference line for an OVERRIDE exact-span F1 plot.

## Proper OVERRIDE comparable experiments
- Rule regex vs classical token-level classifier vs pretrained encoder token head, **all trained/reported on the same OVERRIDE gold split**.
- Current-turn-only vs same architecture with dialogue history; hold training budget, hyperparameters and seeds fixed.
- Real-only vs synthetic-then-real; *identical* final real gold eval; synthetic-only scores are diagnostics.
- Class support and per-difficulty L1-L5 results, strict exact span F1 separately for VALUE and CUE, reference-link accuracy only when annotated.
- Holdout must be prospective, sealed, human-annotated, independently checked and not repeatedly tuned on.

## Unknown and prohibited claims
- `our_real_test_f1`: **NOT MEASURED**
- `our_context_gain`: **NOT MEASURED**
- `our_model_beats_SOM_DST`: **NOT COMPARABLE** without common gold and metric
- `perfect_gold_quality`: **NOT ESTABLISHED** without real review and audit evidence.
