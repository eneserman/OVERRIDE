# D3 Adjudication Worksheet — pilot-30 (2026-10-29)

**Frozen input:** `reports/D3_PILOT30_AGREEMENT.json` (SHA-256 `5e409339785f33a36034d728639e3f2fbc7921658aa24dbe1fb4437777884194`) — computed from the first blind independent files. **Adjudication decisions change ONLY the gold, never this score.**

## Categories (mark every decision with one)

| Code | Meaning |
|---|---|
| `BOUNDARY` | same label, different span extent (determiner/NP/modifier) |
| `VALUE_NESS` | vague preference / query target: value or not? |
| `DEIXIS` | pronoun/locative/question-target as REFERENCE or not |
| `TRANSITION_OP` | ADD vs UPDATE (or other op) on the transition layer |
| `FORMAT_MISMATCH` | schema/biçim farkı (A: `{op,value}` vs B: `{op,slot,before,after}`) — **not** a reviewer disagreement |
| `COORDINATOR_ASSUMPTION` | entry made by the coordinator during file assembly, not a reviewer decision |
| `RULE_REVISION` | a decision that changes under a rule clarification (recorded as rule revision, **not** as disagreement) |

## The conventions (C1–C3, guideline v0.2.2) — used to resolve the table

**C1 — Boundary:** include the determiner when it is part of the noun phrase (`"a salon"`, `"a games event"`, `"on that date"`). Restrictive modifiers belong to the value (`"small rental car"` — not just `"small"`).

**C2 — Value-ness:** label only concrete/determinable values. Vague preferences (`"some other places"`, `"something exciting and interesting"`) and query targets inside questions (`"1 stop"` in *"Does it have 1 stop?"*) get **no** value span.

**C3 — Deixis:** bare pronouns and locatives (`"it"`, `"there"`) and question targets (`"the genre"`) are **not** `REFERENCE`. `REFERENCE` requires a specific previously mentioned value/option. **Deictic + noun pointing at a specific prior option IS a reference** (`"that ticket"`, `"back to Dr. Hamblin Basil again"`) — this resolves the position-25 question: `REFERENCE "that ticket"` is correct and does **not** conflict with the topic-return rule (which blocks bare task nouns like *"booking tickets"* and any `RESTORE_CUE`).

## Coordinator-disclosed items (NOT reviewer disagreements)

| Position | Issue | Category | Resolution |
|---|---|---|---|
| 1 | ADD/UPDATE mapping in transitions (`{op,value}` vs `{op,slot,before,after}`) | `FORMAT_MISMATCH` | spans identical; transition schemas normalized in adjudication only |
| 11 | both values marked `UPDATE` (coordinator assumption) vs `ADD` (Enes) | `TRANSITION_OP` + `COORDINATOR_ASSUMPTION` | adjudicate op per DP-5 (first mention = ADD) |
| 20 | empty transition for "1 stop" | `COORDINATOR_ASSUMPTION` → confirmed by C2 | value unlabeled (query target); empty transition correct |
| 25 | `REFERENCE "that ticket"` vs topic-return rule | `RULE_REVISION` (clarified in C3) | label correct; both reviewers agreed |

## The 10 span disagreements (adjudicate under C1–C3)

| # | ID | Zone | A | B | Proposed resolution (C1–C3) | Decision | Reason |
|---|---|---|---|---|---|---|---|
| 1 | SGD-1bff672afd614f473b | DEIXIS | `REFERENCE "the genre"` | — | C3: question target → **no span** | `TBD` | |
| 2 | SGD-3268166bbb220be1 | VALUE_NESS | +`NEW_VALUE "exciting and interesting"` | — | C2: vague preference → **no span** | `TBD` | |
| 3 | SGD-500c5b88b32a4295 | BOUNDARY | `REFERENCE "that date"` | `REFERENCE "on that date"` | C1: determiner/prep excluded → **"that date"** | `TBD` | |
| 4 | SGD-50c2d5c01ea6273b | BOUNDARY | `NEW_VALUE "small rental car"` | `NEW_VALUE "small"` | C1: restrictive modifier belongs → **"small rental car"** | `TBD` | |
| 5 | SGD-71a78f8aba480436 | BOUNDARY | `NEW_VALUE "a salon"` | `NEW_VALUE "salon"` | C1: determiner included → **"a salon"** | `TBD` | |
| 6 | sgd_43f2a82f62150cff | BOUNDARY | `NEW_VALUE "a games event"` | `NEW_VALUE "games event"` | C1: → **"a games event"** | `TBD` | |
| 7 | sgd_667a77ce3c34f0be | VALUE_NESS | +`NEW_VALUE "1 stop"` | — | C2: query target → **no span** | `TBD` | |
| 8 | sgd_a5d726d0e27a59f5 | VALUE_NESS | `NEW_VALUE "some other places"` | — | C2: vague → **no span** | `TBD` | |
| 9 | sgd_a7f975950eb100c6 | DEIXIS + BOUNDARY | `REFERENCE "that"` + `"a garden"` | `"garden"` | C3: "that" bare pronoun → no span; C1: **"a garden"** | `TBD` | |
| 10 | sgd_cb84c0478ba31271 | DEIXIS + BOUNDARY + VALUE_NESS | `NEW_VALUE "a restaurant"` + `REFERENCE "there"` | `REFERENCE "near there"` | C3: "there" locative → no span; C1: **"a restaurant"** (concrete) | `TBD` | |

*(Proposals = rule-based resolution; the human adjudicator (you, with Burak) confirm or override with a reason. Overrides are recorded as `RULE_REVISION` if the rule itself changes.)*

## After the table is signed

1. `scripts/build_adjudicated_gold.py` with the decisions file → gold (train split).
2. Frozen agreement (`5e409339…`) is what gets reported to the instructor — unchanged.
3. Then the full-457 run (assignment ready: `data/annotations/d3_full457_assignment/`, 60 new double + 357 split).
