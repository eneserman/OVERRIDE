# D3 — Gold v1.1 decisions (LOCKED 2026-10-30)

**Status: LOCKED at the owner's request, before any test access and before D5 is rerun.**
Scope: the 4 mechanical findings (A1–A4) and the 26 audit disagreements (B1–B26) listed in the
local joint decision sheet. Gold v1 is not edited; gold v1.1 is a new file built from it.

## 1. Result

| Item | Value |
|---|---|
| Decisions | 30 (A1–A4, B1–B26) |
| Gold changes | **3 records** (A1, A3, A4); 27 decisions leave gold v1 unchanged |
| Frozen audit score | unchanged: 22/48 = 0.458 (`D3_GOLD_V1_AUDIT_RESULT.json`) |
| Gold v1 SHA-256 | `1f7c286ead45aa80b226ec664b83e4a7604add136e27939f429cc93602cc5924` (untouched) |
| Gold v1.1 SHA-256 | `6f0181c59ca46d9642edb9e030642e8dcf4098a44ecb01061dfc872d4f9b37b3` (`data/gold/train_dev_gold_v1_1.jsonl`, local/gitignored) |
| Validator | `validate_annotations.py --require-gold --allowed-splits train` → PASS, 457/457, 0 errors |
| Builder | `scripts/build_gold_v1_1.py` (asserts the exact v1 "before" state per record; 457 rows, exactly 3 differ) |

## 2. The three changes (all in the train partition)

| ID | Record | v1 | v1.1 | Rule |
|---|---|---|---|---|
| A1 | `SGD-7bb4b2f1283e503502` | `NEW_VALUE "a hotel with 3 rooms"` [20-40] | `NEW_VALUE "a hotel"` [20-27] + `NEW_VALUE "3 rooms"` [33-40] | F1 (`with + N` is split) |
| A3 | `sgd_3324bf1e7d2ec8ca4acf` | `KEPT_VALUE "the same day"` [41-53] | `REFERENCE "the same day"` [41-53] | C6 |
| A4 | `SGD-90cfacf6a275f8d7f3` | `KEPT_VALUE "the same day"` [26-38] | `REFERENCE "the same day"` [26-38] (other spans and `UPDATE_CUE` unchanged) | C6 |

Changed rows carry `adjudication_log_id = D3-ADJ-2026-10-30-V1_1` and an appended `decision_reason`.

## 3. Decision table

A1 **D** · A2 **G** · A3 **D** · A4 **D** · B1–B26 **G** (all 26, including B17 and B26 — see §4).
G = gold v1 kept as is; D = the change in §2. No decision is Y.

## 4. B17 and B26 — default rule

Burak's final record: **G** for both. Enes's final record still states **D** for both
(B17: add `NEW_VALUE "Nature preserve"` [68-83]; B26: split `a movie online` into `a movie` [25-32] +
`online` [33-39]) and calls them open. **No joint agreement to change exists, so the registered
default applies: a gold change needs both reviewers; without it gold v1 stays.** If both later
agree on D for either record, that needs a new recorded decision and a new gold version **before**
D5 is rerun; it must not be applied silently.

## 5. Items flagged for a guideline re-check (not blocking)

Enes marked A2, B9, B10, B18, B21 and B26 as worth re-checking against the full text of
`13_ANNOTATION_GUIDELINES.md` (F1, DP-4, C1-r, R10). Both reviewers kept G for all of them
except B26 (§4). They stay G; any later change follows §4.

## 6. Provenance and limits (declared, not verified by the coordinator)

- The reviewers declare the final decision records are their own.
- Earlier drafts existed and were superseded: `D3_GOLD_V1_1_BURAK_ONAYLANDI.md` and
  `D3_GOLD_V1_1_ENES_ONAYLANDI.md` were written in the third person, stated that the author did not
  have the full guideline text, and recorded Burak's approval as relayed by Enes. They are not the
  basis of this record.
- Source records (SHA-256):
  - `D3_GOLD_V1_1_ENES_ONAYLI_YENIDEN_YAZILDI.md` `c761bccd3a55d312d77b9152c38b8f069c2bdf4d9a329cb512cece5bbb8220b4`
  - `D3_GOLD_V1_1_BURAK_ONAYLI_YENİDEN.md` `b8563f6973dfd1eb82d1f4ae4cf7f8bb35803f4e1ea523682db6ec5d3e569048`
  - superseded drafts: `…BURAK_ONAYLANDI.md` `a61f53423cc864fc8185665d12e15fbf78f341a26b4d1bf10e5a1224a7ddb162`, `…ENES_ONAYLANDI.md` `fadd03680302d915a16afba0c8d1730d827f1c29fbdaec81f1f2907bab7ad7e6`
- Enes's earlier draft summary said "4 D"; his table (and final record) has 5 D. The final record is counted.
- Burak's final table was checked mechanically: all 30 example ids match the decision sheet.
- Because 26 of 30 decisions keep gold, the audit is read as: re-annotators marked more spans than gold, and
  after joint review only three gold records change. It does not show gold v1 to be broadly wrong, and the
  decisions were made by two people who share the guideline conventions.

## 7. Next (not done)

1. Re-freeze the train/dev split with the same pre-committed plan on gold v1.1 (membership must be identical).
2. Rerun D5 with the identical committed configuration; new freeze record before any test access.
3. Fix `TEST_ACCESS_LOG` row #2 (owner approval, v1.1 checkpoints), then run D6 once.
4. Taxonomy-narrowing proposal still needs both signatures before the holdout is opened.
