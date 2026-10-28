# D3 Leakage Audit v0.8 — 2026-10-28 (CTO check 2)

**Status:** EVIDENCE RECORD (not gold). Machine-readable companion: `reports/D3_LEAKAGE_AUDIT_V08.json`. Scope: namespaced IDs alone are NOT trusted — this audit covers full-dialogue fingerprints, normalized text matching, near-duplicate similarity, history repeats and cross-pool families.

## 1. Full-dialogue fingerprint collisions across official splits — **0**

Every raw SGD dialogue (train 16,142 / dev 2,482 / test 4,201) was hashed as its canonical turn sequence (`speaker + normalized utterance`, SHA-256):

| Pair | Identical dialogues | Identical user-turn sequences |
|---|---|---|
| train ∩ dev | **0** | **0** |
| train ∩ test | **0** | **0** |
| dev ∩ test | **0** | **0** |

No dialogue (or user-turn sequence) recurs across official partitions, despite the dialogue-**ID** collisions (train∩dev 2,481 IDs etc., naming artifact only). Identity is therefore keyed on (split, source file SHA-256, turn index), and content fingerprints confirm the partitions are genuinely disjoint.

## 2. Current-utterance text matching (D3 train side vs LOCKED holdout)

| Tier | Pairs found | Action |
|---|---|---|
| Exact normalized match (casefold + whitespace) | 27 rows | **removed from train** (L1) |
| Near-duplicate, token Jaccard ≥ 0.9 | 14 pairs ↔ 10 rows | **removed from train** (L2) |
| Similar, Jaccard 0.8–0.9 | 12 pairs | **retained, listed in JSON for human inspection** |
| After removal | **0 exact / 0 ≥0.9** | re-verified ✓ |

All L2 matches were punctuation/case/word-order variants of boilerplate (`"Not now, thanks"` ↔ `"Not now. Thanks."`; `"I'd like a movie to watch."` ↔ `"I'd like to watch a movie."`). Removing them train-side protects the locked test at trivial cost; the holdout itself was never touched.

## 3. History-message repeats

62 history strings are shared between D3 and holdout contexts; **56 look like system templates** (`"Do you want to make a reservation?"`, `"Good to know."`), 6 user-like. Assessment: context-side template overlap is corpus-inherent (SGD system language is templated); the model's **targets are current user turns**, which are now disjoint at every checked tier. **Residual risk disclosed:** a model may memorize system templates; this affects context features equally for all systems and does not leak test targets. Not removable without gutting the corpus.

## 4. Cross-pool family collisions (pilot vs mining)

7 train dialogues (`101_00093, 107_00055, 74_00030, 79_00098, 85_00063, 98_00086, 99_00039`) contribute turns to **both** the 100-example pilot and the mining pool. Risk: related turns of one dialogue landing in different gold partitions. **Mitigation (check 4):** the frozen train-side split plan groups by dialogue family across BOTH pools (454 families → 409 `train_gold` / 45 `dev_gold`, `reports/D3_TRAIN_DEV_SPLIT_PLAN.json`), so every turn of a dialogue lands in exactly one partition.

## 5. Semantic-leakage statement

No identical full dialogues, no identical user sequences, no exact or ≥0.9-similar current utterances remain between the D3 train side and the locked holdout. The inspected 0.8–0.9 tier (12 pairs, JSON) is boilerplate-shaped and retained by decision. The known SGD dialogue-ID collision is handled by namespaced identity + content fingerprints. Residual risks: system-template history overlap (inherent) and unmeasured deep-semantic paraphrase similarity (stdlib-only tooling; flagged for human spot-check during annotation).
