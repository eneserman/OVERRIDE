#!/usr/bin/env python3
"""Mechanical guideline v0.2.3 rule scan over canonical annotation rows (flags candidates; decides nothing).

Each flag names the rule and the span; the reviewers decide jointly. Rules checked:
C1-r/F2 leading preposition or approximator inside a value span (except `at least`); F1 unsplit
`for/of/with + N`; C3/G3 bare deixis as REFERENCE; C6 `the same day` as KEPT_VALUE; R1 bare `No` as
UPDATE_CUE; DP-1 refusal/deferral as CANCEL_CUE; DP-2/R7 every RESTORE_CUE (rare, always re-checked);
R9 discourse `keep looking/searching/going` as KEEP_CUE; edge whitespace/punctuation; and spans that do not
start/end on a word boundary (the offset tool picking an occurrence inside another token, e.g. "3" in "5:30").
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NUM = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
LEADING = re.compile(r"^(?:on|from|until|at|around|about)\s", re.I)
UNSPLIT = re.compile(rf"\b(?:for|of|with)\s+{NUM}\b", re.I)
DEIXIS = {"it", "there", "that", "this", "here", "them", "those", "these"}
REFUSAL = re.compile(r"^(?:no|not now|no,? not now|not right now|no thanks?|no,? thank you|not at the moment|not yet)[.,!]?$", re.I)
DISCOURSE_KEEP = re.compile(r"^keep (?:looking|searching|going|trying)", re.I)


def word_char(c: str) -> bool:
    return c.isalnum() or c in ":#$"


def scan_row(row: dict) -> list[dict]:
    utt = row["current_user_utterance"]
    flags = []

    def flag(span, rule, why):
        flags.append({"id": row["id"], "label": span["label"], "start": span["start"], "end": span["end"],
                      "text": utt[span["start"]:span["end"]], "rule": rule, "why": why})

    for span in row.get("value_spans") or []:
        t = utt[span["start"]:span["end"]]
        if LEADING.match(t) and not t.lower().startswith("at least"):
            flag(span, "C1-r/F2", "leading preposition/approximator inside the value span")
        if UNSPLIT.search(t):
            flag(span, "F1", "`for/of/with + N` inside one span")
        if span["label"] == "REFERENCE" and t.lower() in DEIXIS:
            flag(span, "C3/G3", "bare pronoun/locative as REFERENCE")
        if span["label"] == "KEPT_VALUE" and "same day" in t.lower():
            flag(span, "C6", "`the same day` as KEPT_VALUE")
    for span in row.get("cue_spans") or []:
        t = utt[span["start"]:span["end"]]
        if span["label"] == "UPDATE_CUE" and t.strip(" ,.").lower() == "no":
            flag(span, "R1", "bare `No` as UPDATE_CUE")
        if span["label"] == "CANCEL_CUE" and REFUSAL.match(t.strip()):
            flag(span, "DP-1", "refusal/deferral as CANCEL_CUE")
        if span["label"] == "RESTORE_CUE":
            flag(span, "DP-2/R7", "RESTORE_CUE: value restore or topic/travel return?")
        if span["label"] == "KEEP_CUE" and DISCOURSE_KEEP.match(t):
            flag(span, "R9", "discourse `keep looking` as KEEP_CUE")
    for span in (row.get("value_spans") or []) + (row.get("cue_spans") or []):
        t = utt[span["start"]:span["end"]]
        if t != t.strip() or (t and t[-1] in ".,!?;"):
            flag(span, "edge", "leading/trailing whitespace or punctuation")
        s, e = span["start"], span["end"]
        if (s > 0 and word_char(utt[s - 1]) and word_char(utt[s])) or (e < len(utt) and word_char(utt[e - 1]) and word_char(utt[e])):
            flag(span, "offset", "span does not start/end on a word boundary (wrong occurrence?)")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True, nargs="+")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite {args.out}")
    flags = []
    for p in args.input:
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                for f in scan_row(row):
                    f["file"] = p.name
                    flags.append(f)
    args.out.write_text(json.dumps({"status": "RULE_SCAN_FLAGS_NOT_DECISIONS", "flags": flags}, indent=2,
                                   ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"flags": len(flags), "by_rule": {r: sum(f["rule"] == r for f in flags)
                                                       for r in sorted({f["rule"] for f in flags})}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
