# D0/D1 — Factual Findings: Real Official SGD Train Audit

**Phase:** D0 (real source audit) + D1 feasibility evidence | **Date:** 2026-10-28
**Status:** COMPLETE (measured, read-only) | **Decision requested:** scope/taxonomy review before D1/D2 pilot packets
**Method:** all numbers below were produced by executing the commands shown; nothing is estimated except where explicitly labelled `estimate`.

---

## 1. Source pin and data access

| Item | Value |
|---|---|
| Upstream | https://github.com/google-research-datasets/dstc8-schema-guided-dialogue |
| Access | Public clone succeeded (`--depth 1`), 2026-10-28 |
| **Pinned commit** | `e852981ae34990f4358979625854259302feaa78` |
| Commit date / subject | 2023-08-07 — "Merge pull request #60 from google-research-datasets/sgdx-intent-bug" (upstream is archived; this is HEAD) |
| Split audited | `train` only (`dev`/`test` not touched; `audit_sgd.py` refuses them without `--allow-eval-split`) |
| Train files | 127 (`dialogues_001.json` … `dialogues_127.json`), 455,309,688 bytes total |
| File hashes | SHA-256 of all 127 files recorded in `reports/SHA256_SGD_TRAIN_FILES.txt` and embedded in `reports/sgd_train_audit/sgd_audit_summary.json` (`source_files_sha256`) |
| License | CC BY-SA 4.0 (`data/upstream/sgd/LICENSE.txt`, verified full text present) |
| Required citation | Rastogi, Zang, Gupta, Sunkara, Khaitan (2019). *Towards Scalable Multi-domain Conversational Agents: The Schema-Guided Dialogue Dataset*. arXiv:1909.05855 |
| Data in repo? | **No.** `data/upstream/` is gitignored; only hashes and aggregate counts are published. |

## 2. Command log (executed, with exit codes)

| # | Command | Exit | Output |
|---|---|---|---|
| 1 | `python -m unittest discover -s tests -v` | 0 | `Ran 35 tests in 0.170s — OK` |
| 2 | `git clone --depth 1 https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd` | 0 | 208 files checked out |
| 3 | `git -C data/upstream/sgd rev-parse HEAD` | 0 | `e852981ae34990f4358979625854259302feaa78` |
| 4 | `python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit` | 0 | `Audit complete: 16142 dialogues` + non-gold warning |
| 5 | ad-hoc read-only scans (see §6 appendix) | 0 | rare-cue and revision-composition counts below |

Unit tests: **35/35 PASS before and after the audit. No test or script defects were exposed by the real source format; therefore zero changes were made to `scripts/` and `tests/` in this phase.** Diff for D0 = this report + `reports/SHA256_SGD_TRAIN_FILES.txt` + `CHANGELOG.md` entry only.

## 3. Measured corpus aggregates (`sgd_audit_summary.json`, status `OBSERVATIONAL_AUDIT_ONLY`)

| Count | Value |
|---|---|
| source files | 127 |
| dialogues / unique dialogue IDs | 16,142 / 16,142 (no duplicates) |
| turns | 329,964 (USER 164,982 / SYSTEM 164,982) |
| user frames | 175,780 |
| state slot entries | 598,617 |
| non-empty slot-state frames | 165,482 |
| same-service state comparisons | 146,138 |
| comparisons with ≥1 candidate | 84,086 |
| first-observed user frame for service (ADD controls, not compared) | 29,642 |
| same-service non-adjacent user frames | 1,829 |
| reported slot span offsets | 242,267 |
| **valid span offsets** | **242,267 (0 invalid, 0 out-of-bounds; `invalid_offset_examples_up_to_10` empty)** |
| services / domains covered | 26 services / 16 domains (largest: Restaurants_1 17,570, Events_2 16,601, Flights_1 15,865 user frames) |

## 4. Candidate coverage (heuristic mining output — NOT gold)

State-change candidates over all 146,138 same-service comparisons:

| Candidate kind | Count | Interpretation |
|---|---|---|
| `SLOT_ADDED_CANDIDATE` | 93,302 | mostly first fills (ADD) + genuine new-value additions |
| `ALIAS_OR_STATE_VARIANT_CANDIDATE` | 24,326 | alias-set expansions; **mostly NOT meaning changes** (see §5.1) |
| `SLOT_CHANGED_CANDIDATE` | 10,475 | primary pool for genuine UPDATE/OLD_VALUE/NEW_VALUE |
| `SLOT_CLEARED_CANDIDATE` | 470 | primary pool for DELETE / possible CANCEL_INTENT |

Lexical cue-flagged user turns (audit regexes):

| Flag | Turn count | Broader manual scan (§6) |
|---|---|---|
| `possible_revision_cue` (actually/instead/rather/change/switch/replace/no) | 14,308 | composition measured: see §5.2 |
| `possible_keep_cue` (keep/remain/unchanged/same) | 499 | 508 turns with `remain*` variant |
| `possible_restore_cue` (back to/original/previous/first one) | 207 | 207 turns; sub-pattern breakdown in §5.4 |
| `possible_cancel_cue` (cancel/delete/remove/stop) | 103 | 117 turns with `cancel*` inflections |

## 5. Manual inspection — examples and false positives (with provenance)

All examples are **unreviewed SGD train text**, shown for feasibility analysis only. None are gold labels.

### 5.1 Alias expansions are not revisions (`ALIAS_OR_STATE_VARIANT_CANDIDATE`, 24,326 hits)

- `[1_00002 t10] "That's right. Do they serve alcohol? And how expensive is the place?"` → `date: '2nd of this month' -> '2nd of this month|tomorrow'`, `time: '17:15' -> '17:15|5:15 pm'`
- `[1_00003 t10] "Yes, that works for me. How pricey are they? What is their contact number?"` → `time: 'half past 6 in the evening' -> '6:30 pm|half past 6 in the evening'`

The state did not change meaning; SGD merely added a surface alias. **These must be annotation controls (`NO_CHANGE`/`KEPT_VALUE` at most), never `UPDATE_CUE`.** The audit's `ALIAS_OR_STATE_VARIANT_CANDIDATE` separation is doing its job.

### 5.2 The revision regex is heavily diluted by bare "No" answers

Measured composition of the 14,308 `possible_revision_cue` turns:

| Sub-class | Count | Example |
|---|---|---|
| explicit cue word (actually/instead/rather/change*/switch/replace) | **2,462** | `[1_00008 t16] "No, change the time to 7 pm and for one person only."` |
| sentence-initial bare "No," (answers, refusals, closings) | **11,460** | `[1_00001 t24] "No, Thanks"`, `[1_00006 t16] "No, that is all."`, `[1_00009 t16] "no thats it"` |
| other `no`-forms | 386 | `no`/`no,` elsewhere in the turn |

**≈80% of revision-flagged turns are not revisions.** The usable revision-cue pool is on the order of **~2.5k turns**, not 14.3k.

### 5.3 Cancellation: hypotheticals and third-party cancellations dominate (117 turns scanned)

- Policy/hypothetical questions (NOT user revisions): `[16_00092 t6] "…Can I get a refund for the ticket if I decide to cancel?"`, `[17_00005 t6] "Would I be able to cancel and get a refund?…"`, `[2_00020 t8] "…in case I have to cancel…"`
- Third-party cancellation causing an implicit revision: `[3_00091 t4] "No, I forgot, my mother-in-law canceled, so I only need reservations for two…"` , `[10_00032 t22] "My kids just cancelled I only need one ticket now."` — these change `party_size`/ticket count but contain **no explicit cancel instruction** toward a booking.
- Outright lexical false positive: `[7_00088 t14] "I need you to stop talking while my song is playing!"` (media command).

**Explicit user-directed booking cancellation ("cancel the hotel") is extremely rare to absent in the sampled scan.** `CANCEL_CUE` as a supervised class is at risk.

### 5.4 Negated cancellation has ZERO corpus support

Regex `\b(?:not|n't|never|do not|don't)\s+(?:cancel|delete|remove|stop)\b` over **all 164,982 user turns** matched **0 turns**. The guideline edge case "Don't cancel the flight" (E05) is **not naturally attested in SGD train**. It can only survive as a hand-constructed diagnostic item, and must not be advertised as corpus-supported.

### 5.5 Restore cues are dominated by the travel sense of "back to" (207 turns)

Sub-pattern counts: `back to` 187, `previous` 11, `original` 9, `first one` 1.

- Travel sense false positives: `[19_00097 t10] "I need to head back to Chicago on the 9th…"`, `[41_00072 t8] "…returning back to my hometown on March 13th."`, `[36_00106 t8] "When does the return get back to New Delhi?"`
- "previous" used in a *revision*, not a restore: `[1_00093 t12] "Instead of the previous time, can you make it at 18:00?"`
- Genuine restore-like candidate (rare): `[36_00079 t4] "I want to go back to Dr. Hamblin Basil again."`

Realistic `RESTORE_CUE` support after manual pruning: **tens of turns, not hundreds**. L4 must stay diagnostic-only.

### 5.6 Keep cues: discourse continuations vs value retention (508 turns scanned)

- Genuine KEPT_VALUE candidates: `[1_00013 t4] "Yes, I like the same."`, `[1_00030 t6] "Ok its fine , i prefer the same."`
- Discourse false positives: `[2_00033 t12] "Okay, let's keep looking then."`, `[5_00103 t4] "Keep going."`, `[2_00061 t2] "And keep it reasonably priced."` (constraint add, not keep)

### 5.7 First slot fills are ADD, not correction

29,642 user frames are the first observation for their service; the audit correctly excludes them from state comparison (they are `ADD` controls). Example of an early fill that is NOT a correction: `[1_00000 t2] "I would like for it to be in San Jose."` → `city: [] -> ['san jose']` (`SLOT_ADDED_CANDIDATE`).

### 5.8 Genuine revision signal (positive evidence)

Explicit corrections with both cue and new value do exist and are cleanly minable:

- `[1_00001 t16] "No, time change to twelve in the afternoon for one people"` → `time: 'afternoon 1:30' -> 'twelve in the afternoon'` + `party_size` add
- `[1_00010 t10] "I'm sorry, I need to change that. I'd like it on the 9th and it will be for 3 people."`
- `[1_00002 t8] "Reserve the table for the 2nd of this month at 17:15."` → `date: 'the 4th' -> '2nd of this month'` (implicit re-specification, no explicit cue)

## 6. Category support table (evidence-based; unverified labels marked)

| Target label | Corpus evidence (measured) | Verdict for pilot |
|---|---|---|
| `NEW_VALUE` (V) | 93,302 `SLOT_ADDED` + 10,475 `SLOT_CHANGED` candidates | **SUPPORTABLE** |
| `OLD_VALUE` (V) | old side of 10,475 `SLOT_CHANGED` + 470 `SLOT_CLEARED`; but old value often not re-uttered | **SUPPORTABLE, subset only** (expect many turns with NEW but no spoken OLD) |
| `KEPT_VALUE` (V) | ≤508 keep-flagged turns, ~half genuine `estimate` | **NARROW** |
| `REFERENCE` (V) | **not measured by this audit** | **UNVERIFIED** |
| `UPDATE_CUE` (C) | 2,462 explicit-cue turns | **SUPPORTABLE** |
| `KEEP_CUE` (C) | subset of ≤508 | **NARROW** |
| `CANCEL_CUE` (C) | 117 turns scanned; explicit user-directed cancels ≈ 0–10 `estimate` | **NARROW → likely NO-GO as trained class** |
| `RESTORE_CUE` (C) | 207 flagged, tens genuine after pruning | **NO-GO as trained class (diagnostic only)** |
| transitions `ADD` | 29,642 first-fill frames | SUPPORTABLE (secondary) |
| transitions `UPDATE` | 10,475 changed candidates | SUPPORTABLE (secondary) |
| transitions `DELETE` | 470 cleared candidates | NARROW (secondary) |
| transitions `KEEP`/`RESTORE`/`CANCEL_INTENT` | see above | NARROW/NO-GO (secondary) |
| L1 (explicit replacement) | abundant (§5.8) | SUPPORTABLE |
| L2 (partial keep + change) | present (`1_00001 t16` changes time, adds party_size) | SUPPORTABLE |
| L3 (cancellation) | mostly implicit/third-party | NARROW |
| L4 (restore) | tens | NO-GO → diagnostic set |
| L5 (multi-turn mixed) | **not measured** | UNVERIFIED |

## 7. Annotation budget estimate (`estimate`, not a promise)

- Pilot target 100: **feasible** via stratified oversampling of `SLOT_CHANGED`/`SLOT_CLEARED`/explicit-cue turns + alias/no-change controls. Expect **shortfall** in `NEGATED_CANCEL` (0 support) and `RESTORE_CUE` (tens). One example per dialogue constraint is compatible: 10,475 changed candidates spread over thousands of dialogues.
- Gold target 400–600: feasible **only if** the taxonomy accepts a dominant UPDATE/NEW_VALUE mass and treats `RESTORE_CUE`/`CANCEL_CUE` as rare diagnostic strata. Do not rebalance by relabeling normal turns (design rule).
- Two independent human reviewers must label the blind packets; nothing in D0 substitutes for that.

## 8. Legal / licensing notes

- SGD is **CC BY-SA 4.0**: attribution + share-alike obligations apply to adaptations containing source text. Aggregates and hashes in this report are fine; **raw/clean dialogue text must not be pushed** to the public repo without the redistribution review in `15_DATA_LICENSE_AND_ATTRIBUTION.md`.
- Cite Rastogi et al. 2019 (arXiv:1909.05855) in README/PPTX.
- Candidate/annotation outputs derived from SGD inherit obligations; reviewer identity notes must stay private.

## 9. Decision

**GO — for the D1/D2 pilot, with mandatory NARROWING:**

1. **GO:** source is pinned and audited; offsets are 100% valid; UPDATE/NEW_VALUE (L1–L2) have strong measured support (10,475 changed + 93,302 added candidates; 2,462 explicit cue turns). A 100-example stratified pilot is feasible now.
2. **NARROW:** `KEPT_VALUE`/`KEEP_CUE` to explicit-retention turns only; `CANCEL_CUE` to explicit user-directed instructions (expect tiny support).
3. **NO-GO (as trained classes):** `RESTORE_CUE` (L4) and negated-cancel (E05) — zero-to-tens support. Keep as a hand-verified **diagnostic set**, separately reported (per `AGENT_D0` boundary rule).
4. **REVIEW REQUESTED before D1/D2 packet generation:** confirm the narrowed taxonomy (or accept diagnostic-only rare classes) and the pilot stratification plan. Per the master prompt's hard gates, this phase **stops here**; no gold labels, no training, no scores were produced.

---

## Appendix — ad-hoc inspection commands (read-only, not repo tooling)

The two inspection one-off scripts live outside the repo (temp dir) so the repository tree stays minimal. Their logic is reproducible with: `python -c "<json+re scan of data/upstream/sgd/train/dialogues_*.json>"` as run on 2026-10-28:

- Scan A: user-turn regex counts for `CANCEL_any`, `NEGATED_CANCEL`, `RESTORE`, `KEEP` + 8 samples each (164,982 user turns scanned).
- Scan B: composition of `possible_revision_cue` flags (explicit cue word vs bare "No" answer) and RESTORE sub-pattern counts.

Raw audit outputs (`reports/sgd_train_audit/`) remain local and unreviewed per `.gitignore`; only aggregates and provenance are published in this report.
