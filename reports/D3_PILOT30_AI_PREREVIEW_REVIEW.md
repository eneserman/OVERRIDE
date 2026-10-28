# Pilot-30 AI Pre-Review — Private Quality Diagnosis vs Guide v0.2 (2026-10-28)

**Status:** PRIVATE QUALITY REVIEW — the AI drafts are `AI_SIMULATION` (one model, two policies). **Not human annotations, not inter-annotator agreement, not gold.** They are never shown to reviewers (kept local, gitignored) and never used as labels. Human gold remains **0**; real agreement is **not measured** until the two humans finish.

Reviewed: `OVERRIDE_PILOT30_AI_PRE_REVIEW/` (2 draft JSONLs, comparison CSV, diagnostic JSON) against `13_ANNOTATION_GUIDELINES.md` v0.2 (R1–R12, DP-1, DP-2) and the mining expectations.

## 1. Integrity check first

| Item | Finding |
|---|---|
| Input identity | 30 records, all `UNLABELED`, IDs/utterances identical to our pilot-30 packet ✓ |
| SHA reconciliation | AI package reports file-byte SHA `50445862…` = **exact** byte SHA of `d3_pilot30_v0.1/reviewer_A_BLIND.jsonl` ✓. My earlier recorded `3a6d7e77…` was the **content** (LF-normalized serialization) hash — Windows text-mode writes store CRLF. Both hashes now recorded; **content identical**, no integrity issue. |
| Test-packet link | Blind test packet bytes hash to `921dcd5d…` = the **locked pool SHA in the holdout manifest** — packets are byte-identical to the locked pool ✓ |
| Provenance of drafts | `AI_DRAFT`, `ai_draft_only: true`, `human_gold_count: 0`, `transitions` left empty by design ✓ (no invented state changes) |

## 2. Guide compliance of the AI drafts (both policies)

| Rule | Result |
|---|---|
| **DP-1** refusal/deferral ≠ CANCEL | ✅ **6/6 refusal items** ("Not now…", #2 #5 #13 #17 #23 #30) got **zero** `CANCEL_CUE` from both policies |
| **DP-2** topic-return ≠ value-restore | ✅ **3/3 topic-return items** (#3 "go back to booking tickets", #22 "back to the hotel issue", #25 "back to that ticket") got **zero** `RESTORE_CUE` from both policies |
| No invented transitions / gold | ✅ |

So the two hardest rules are applied consistently by both AI policies — and both will be stress-tested by the humans' independent judgments (that is the real measurement).

## 3. Class-coverage diagnosis (the CTO's core finding, confirmed)

Labels with observable support in the 30 current turns (A ∪ B suggestions): **NEW_VALUE, REFERENCE, UPDATE_CUE** only.  
Labels with **zero observable support**: `OLD_VALUE`, `KEPT_VALUE`, `KEEP_CUE`, `RESTORE_CUE` (and no true `CANCEL_CUE` — all cancel-bucket items are refusals).

| Mining bucket in pilot-30 | What the text actually shows |
|---|---|
| RESTORE / POSSIBLE_RESTORE (3 items) | all **task resumption** ("back to booking tickets", "back to the hotel issue") — DP-2 negatives |
| CANCEL / POSSIBLE_CANCEL (4 items) | all **refusals** ("Not now.") — DP-1 negatives |
| KEEP / POSSIBLE_KEEP (3 items) | duration ("keep it until March 5th") or discourse ("let's keep looking") — R9 negatives |
| UPDATE / STATE_CHANGED (4 items) | genuine explicit/implicit revisions — the real positives |

**Conclusion (matches the CTO verdict):** pilot-30 is a good **quality diagnostic** and agreement trial for *observable* labels + negative handling, but it **cannot** justify a schema-wide GO for all 8 labels. `OLD_VALUE`/`KEPT_VALUE`/`KEEP_CUE`/`RESTORE_CUE` remain untested here — and per D0/D1 the corpus itself offers little true support for RESTORE/CANCEL regardless.

## 4. The 6 disputed items — guide-based analysis

| # | Dispute (B-only span) | Guide v0.2 view | Verdict |
|---|---|---|---|
| 3 | `REFERENCE@[23,38)` on "go back to booking tickets" | DP-2 correctly blocks RESTORE, but the target is a **task**, not a slot value; guide has **no rule** for task-reference | **GUIDE GAP** (candidate v0.3 rule) |
| 22 | `REFERENCE@[43,54)` on "back to the hotel issue" | same as #3 | **GUIDE GAP** |
| 16 | `UPDATE_CUE@[5,9)` on "If I only keep it until March 5th…" | no explicit cue word; guide restricts `UPDATE_CUE` to explicit cue phrases → B over-labels | rule clarity issue (implicit revision → value-only) |
| 11 | 2× `NEW_VALUE` on "I like that, but let's keep looking. I'd prefer something cheaper" | complete-mention + first-fill vs change (R11/ADD-vs-UPDATE) boundary | human call needed |
| 26 | `NEW_VALUE@[48,59)` on "I need something in New York City…" | first-fill value mention boundary (R11) | human call needed |
| 27 | `NEW_VALUE@[38,48)` on "Make it 1 ticket for later today from Long Beach." | ADD vs UPDATE per slot (ticket count = update; Long Beach = add) — multi-slot split rule | human call needed |

**Pattern:** all 6 disagreements sit in exactly three rule zones — (a) task-reference (new gap), (b) implicit-cue labeling, (c) ADD-vs-UPDATE / complete-mention boundaries. These are the zones to watch in the human pilot.

## 5. Candidate guideline v0.3 changes (DECIDE at pilot review; nothing changed yet)

1. **Task-reference rule:** "go back to X-task / back to the X issue" → neither `RESTORE_CUE` nor `REFERENCE`; treat as topic resumption with no span (or an explicit `TASK_RESUME` note in `uncertainty_notes`).
2. **Implicit-cue rule (explicit wording):** `UPDATE_CUE` only for explicit cue words/phrases; implicit revisions get value spans only.
3. **ADD vs UPDATE worked examples:** multi-slot turns ("Make it 1 ticket … from Long Beach") split per slot.

Per CTO rule: any adoption is versioned in the change log with affected example IDs; **the locked test selection never changes**.

## 6. What the human pilot-30 will actually decide

- Real **agreement** on observable labels (NEW_VALUE, UPDATE_CUE, REFERENCE) and on negatives (the DP-1/DP-2 traps) — the AI split shows these zones are judgeable;
- Whether humans agree with each other more than the two AI policies did (6/30 disagreement rate is a *diagnostic baseline*, NOT a target or a human score);
- Whether the guideline gaps in §5 cause friction (then REVISE before the full 820-record run);
- Real minutes/example to judge full-run feasibility.

## 7. Status (unchanged)

Human gold **0** · human agreement **not measured** · test labels **sealed** (access log: 0) · holdout lock intact · D5 **not started**. This review is private diagnosis material; it is not annotation evidence and cannot be reported as data quality.
