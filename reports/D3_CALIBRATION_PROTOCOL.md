# D3 Calibration Protocol — 2026-10-28

**Purpose:** rule alignment practice for the two reviewers BEFORE the main annotation pass.  
**Material:** `data/annotations/d3_calibration_v0.1/calibration_sample.jsonl` — 10 TRAIN-section examples (not from the sealed test pool).  
**Status of the answers below:** guideline teaching material authored from the documented rules (DP-1/DP-2, R1–R12). **NOT human gold, NOT counted in agreement statistics, NEVER merged into any gold file.**

## Procedure (≈1 hour)

1. Both reviewers annotate the 10 items **independently** with the normal tools (blind to this key).
2. Meet and compare against the worked expectations below. Every mismatch is discussed until the *rule* is clear (not just the answer).
3. If a rule seems wrong or an expectation is debatable, record it as a guideline issue for the owner — the guideline is v0.2, not frozen.
4. Record which IDs were used for practice in `calibration_index.json`; agreement reporting will show statistics **with and without** these IDs.

## Focus checks (the two hardest distinctions)

### DP-1 — refusal/deferral ≠ CANCEL
- Bucket `CANCEL`/`POSSIBLE_CANCEL` practice items mostly contain **refusals** ("Not now.", "No, not now. Thanks.") → expected: **no CANCEL_CUE, no cancellation transition**.
- True cancel = withdrawing a previously given instruction ("cancel the hotel booking") → `CANCEL_CUE` + `CANCEL_INTENT`.
- Third-party cancellation ("my kids cancelled") → no cue; only a value change if re-stated.

### DP-2 — topic return ≠ value restore
- Bucket `RESTORE` practice items mostly contain **task resumption** ("Back to the bus tickets, I'll need 4 tickets.") → expected: **no RESTORE_CUE**; values as NEW_VALUE/ADD.
- True restore = reverting to a previously mentioned **slot value** ("the earlier flight was better") → `RESTORE_CUE` + `RESTORE`.
- Rule of thumb: the object of the sentence is a *slot value* → restore; a *task* → topic return.

### Also verify
- **KEEP**: "Let's keep looking" = discourse → no cue; "I need the same" = retention → `KEPT_VALUE` (+`KEEP_CUE` only with an explicit keep phrase).
- **ADD vs UPDATE**: first-mentioned slot info = ADD/NEW_VALUE; changing a previously given value = UPDATE (+`OLD_VALUE` only if the user *says* the old value).
- **REFERENCE**: "that one" pointing to a prior offer → `REFERENCE` + link if the referent is explicit.
- Offsets: `utterance[start:end] == text` always; minimal cue phrase; complete value mention.

## Worked expectations (teaching key — do not treat as gold)

| # | Practice bucket | What to look for | Expected handling |
|---|---|---|---|
| 1 | CANCEL | deferral of an offer | no CANCEL_CUE; no transition (or UNRESOLVED) |
| 2 | RESTORE | task resumption | no RESTORE_CUE; new values as NEW_VALUE/ADD |
| 3 | KEEP | explicit retention vs discourse | KEPT_VALUE only with explicit retention |
| 4 | UPDATE | explicit revision with new value | UPDATE_CUE minimal + NEW_VALUE complete |
| 5 | MIXED | two signals in one turn | annotate BOTH layers separately per signal |
| 6 | HARD_NEGATIVE | no cue at all | reviewed-negative (`[]`) is the correct answer |
| 7 | REFERENCE | deixis to prior offer | REFERENCE span + link target if explicit |
| 8 | NO_CONTEXT | first turn, no cue | ADD/NEW_VALUE if values are given |
| 9 | STATE_CHANGED | implicit revision (no cue word) | NEW_VALUE (+OLD_VALUE only if spoken); often NO cue |
| 10 | POSSIBLE_CANCEL | negation/pattern trap | check scope; usually not a cancellation |

*(Item numbers refer to `calibration_index.json` order; the exact bucket of each practice item is recorded there for the coordinator — reviewers should NOT open that file before annotating.)*

## Exit criteria (calibration is "done" when)

- Both reviewers can apply DP-1 and DP-2 consistently on the practice items;
- All rule disagreements are resolved into guideline clarifications (or logged as open guideline issues);
- The owner confirms to proceed to the main pass. **Calibration items stay in the main pool** (they are normal examples); agreement stats will disclose their influence.
