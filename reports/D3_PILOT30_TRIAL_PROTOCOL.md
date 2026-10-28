# D3 Pilot-30 Trial Protocol — independent double annotation before the full pass (2026-10-28)

**Purpose:** a small, real, independent double-annotation trial to validate the guidelines and measure per-class agreement **before** committing 820 records × 2 reviewers (1,640 judgments). CTO instruction: *"önce küçük bir kalibrasyon ve pilot anlaşma kontrolü yapmak, saatler süren hatalı etiketlemenin önüne geçer."*

## Material

| Item | Value |
|---|---|
| Packets | `data/annotations/d3_pilot30_v0.1/reviewer_A_BLIND.jsonl` / `reviewer_B_BLIND.jsonl` (byte-identical, **SHA-256 `3a6d7e771cf2c8f7fc5dc2d4b01182085989dad3547435f195096194f0aa18ef`**) |
| Items | **30**, TRAIN partition only, **disjoint from the 10 calibration items**, stratified across private buckets (coordinator index `pilot30_index.json` — bucket labels never shown to reviewers) |
| Rules | `13_ANNOTATION_GUIDELINES.md` v0.2 (R1–R12, DP-1, DP-2, `UNCERTAIN:` convention) |

## Procedure

1. **Calibration first** (10 items, discussed together) — rule alignment before the trial.
2. **Trial:** both reviewers annotate all 30 items **independently** (blind; no discussion; no AI drafts; no private manifests). Trial annotations are the **final** independent annotations for these 30 items — they are made before any post-trial discussion, so they remain valid independent judgments.
3. **Analysis** (coordinator):
   ```
   python scripts/normalize_review_packet.py --input data/annotations/d3_pilot30_v0.1/reviewer_X_filled.jsonl --reviewer-id reviewer_X_ISIM --out data/annotations/d3_pilot30_v0.1/reviewer_X_canonical.jsonl
   python scripts/annotation_agreement.py --a .../reviewer_A_canonical.jsonl --b .../reviewer_B_canonical.jsonl --exclude-ids data/annotations/d3_calibration_v0.1/calibration_index.json --out reports/D3_PILOT30_AGREEMENT.json
   ```
   Review, per class: exact-span matched/only-A/only-B/F1 (`span_level_agreement_by_label`), example-level agreement, `uncertainty_flagged` lists, and the disagreements list. The **primary** score excludes the 10 calibration items (they were discussed together → not independent); both variants are in the report.
4. **Decision meeting:** walk every disagreement; classify issue types (`boundary|class|target|polarity|ambiguity`); decide:
   - **guideline fix** → version bump + affected example IDs recorded in the change log (`13_ANNOTATION_GUIDELINES.md`), re-annotation of affected items under the new version. **Locked test selection never changes.**
   - **acceptable ambiguity** → adjudicate with reason; keep `UNCERTAIN:` notes.
5. **Go / narrow decision:** if per-class agreement is acceptable and rules are clear → proceed to the **full pass** (remaining 427 merged records + the 363 sealed test records afterwards). If not → revise guidelines, repeat a small trial; do not push hours of annotation on unstable rules.

## What we will examine (CTO list)

- per-class **exact-span agreement** (especially UPDATE vs ADD, KEPT_VALUE vs NEW_VALUE),
- the hard rules: **CANCEL ≠ refusal**, **RESTORE ≠ topic return** (expect near-zero true positives; confirm reviewers apply DP-1/DP-2 consistently),
- **uncertainties** (`UNCERTAIN:` flags): frequency and patterns,
- workload reality check: actual minutes/example to plan the 1,640-judgment full run.

## Integrity rules (unchanged)

No gold before human annotation + adjudication; AI drafts are never human work; test packets stay unopened during this trial (the trial uses train-partition items only); test labels remain sealed from development; no D5 training.
