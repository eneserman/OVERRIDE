# 10 — PPTX Storyboard (No invented experiments)

**Important:** Slides should be produced with real data plots after D0–D6; this file is an editable content plan, **not a delivered PPTX**.

## Narrative goal
Make one claim understandable: *past conversation context helps identify which exact phrases express corrections and preservation; this must be proven experimentally rather than assumed.*

| Slide | Purpose | Evidence required |
|---|---|---|
| 1 | OVERRIDE: user revises an instruction | clear 3-turn example with old/new/keep and labeled reference |
| 2 | Problem + novelty | why SGD `state` isn't gold for corrections; proposed two-layer spans |
| 3 | Dataset engineering | source/commit, pilot, A/B annotation, cleaning log, support counts |
| 4 | Methods | RULE/CRF/Transformer, current-only vs history, gold-safe masking |
| 5 | Results | strict VALUE/CUE span F1, hard negatives, L1–L5 supports **actual results only** |
| 6 | Failure analysis + conclusion | one real error, causes, reproducibility and limitations |

## Time discipline
P1 announcement describes strong incentive for short delivery, but P2 time limit is **not verified**. Prepare a <=2-minute rehearsal cut and a longer backup. Never read slide text word-for-word. One human speaker should explain token alignment, why CRF is a baseline and one measured failure; judges may ask why a changed state is not itself a correction.

## Visual proof checklist
Show a real source utterance and `[start,end)` labels; a real annotation disagreement and resolution (redact IDs); real comparison chart with N and split; real command producing result JSON; a terminal inference command if trained. Show `NOT TRAINED` rather than fabricated screenshot if the phase has not been executed.

## Questions to rehearse
1. What are **token** labels versus state-transition labels?
2. How can a RESTORE reference be unresolvable?
3. How do you avoid future/gold state leakage?
4. Why not use token accuracy as main metric?
5. How do two reviewers disagree on negated cancellations?
6. How do you prove data novelty beyond simply filtering SGD?
7. What happens if L4/L5 have fewer than useful test examples?
