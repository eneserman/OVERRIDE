#!/usr/bin/env python3
"""OVERRIDE annotation entry helper — human data entry facilitation ONLY.

A real human reviewer supplies every label; this tool never guesses, prefills
or generates annotations. It removes mechanical error: the reviewer types the
exact phrase, the tool computes and verifies the character offsets, enforces
the label vocabulary and same-layer overlap rules, and validates each saved
example against the same contract used downstream (normalize_review_packet +
validate_annotations).

It reads ONLY the blind packet file. It never reads
PRIVATE_sampling_manifest.jsonl (sampling hints would bias the reviewer).

Usage:
  python scripts/annotation_entry_helper.py \
      --packet data/annotations/pilot_v0.1/annotator_A_UNLABELED.jsonl \
      --reviewer-id reviewer_A_eser \
      --out data/annotations/pilot_v0.1/reviewer_A_filled.jsonl

  --resume   continue an interrupted session (skips example_ids already in
             --out and appends; never rewrites existing rows).
  --only ID  work on a single example (re-review after an error).

Keyboard flow per example: V/C = add value/cue span, T = transition,
L = link, D = difficulty, N = uncertainty note, S = save and next,
K = save as reviewed-negative (no spans), Q = quit (progress is kept).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from validate_annotations import read_jsonl, validate_rows
from normalize_review_packet import normalize

VALUE_LABEL_ORDER = ("NEW_VALUE", "OLD_VALUE", "KEPT_VALUE", "REFERENCE")
CUE_LABEL_ORDER = ("UPDATE_CUE", "CANCEL_CUE", "KEEP_CUE", "RESTORE_CUE")
DIFFICULTY_ORDER = ("L1", "L2", "L3", "L4", "L5")
OPERATION_ORDER = ("ADD", "UPDATE", "DELETE", "KEEP", "RESTORE", "CANCEL_INTENT", "UNRESOLVED")

DIFFICULTY_HINTS = {
    "L1": "explicit replacement of one value",
    "L2": "partial keep + change",
    "L3": "cancellation / removal of an instruction",
    "L4": "restore to an earlier choice (diagnostic)",
    "L5": "multi-turn mixed revision (diagnostic)",
}


class EntryError(ValueError):
    """Raised for user-correctable input problems."""


def find_occurrences(utterance: str, phrase: str) -> list[int]:
    """Return every start offset of the exact substring `phrase`."""
    if not phrase:
        raise EntryError("empty phrase")
    starts = []
    idx = utterance.find(phrase)
    while idx != -1:
        starts.append(idx)
        idx = utterance.find(phrase, idx + 1)
    return starts


def make_span(utterance: str, phrase: str, label: str, occurrence: int = 1,
              allowed_labels: tuple[str, ...] = VALUE_LABEL_ORDER + CUE_LABEL_ORDER) -> dict:
    """Build a validated span dict from the exact phrase the human typed."""
    if label not in allowed_labels:
        raise EntryError(f"unknown label {label!r}; allowed: {', '.join(allowed_labels)}")
    starts = find_occurrences(utterance, phrase)
    if not starts:
        raise EntryError(f"phrase {phrase!r} does not occur in the utterance")
    if occurrence < 1 or occurrence > len(starts):
        raise EntryError(f"occurrence {occurrence} out of range (found {len(starts)})")
    start = starts[occurrence - 1]
    end = start + len(phrase)
    if utterance[start:end] != phrase:  # defensive; should never trigger
        raise EntryError("internal slice mismatch; please report this")
    return {"start": start, "end": end, "text": phrase, "label": label}


def check_same_layer_overlap(spans: list[dict]) -> None:
    ordered = sorted(spans, key=lambda s: (s["start"], s["end"]))
    for prev, cur in zip(ordered, ordered[1:]):
        if cur["start"] < prev["end"]:
            raise EntryError(
                f"same-layer overlap: '{prev['text']}' [{prev['start']},{prev['end']}) "
                f"vs '{cur['text']}' [{cur['start']},{cur['end']}) — split or drop one")


def fill_record(record: dict, reviewer_id: str, value_spans: list[dict], cue_spans: list[dict],
                transitions: list[dict], links: list[dict], difficulty: str | None,
                uncertainty_notes: str) -> dict:
    """Return the packet record with the human's annotation filled in.

    The result is validated exactly like downstream code will consume it:
    normalized through normalize_review_packet.normalize() and checked with
    validate_annotations.validate_rows(require_gold=False). It is therefore
    guaranteed non-gold `ANNOTATED`, never `ADJUDICATED`.
    """
    if not reviewer_id or not reviewer_id.strip():
        raise EntryError("reviewer_id is required (real reviewer identity)")
    if difficulty is not None and difficulty not in DIFFICULTY_ORDER:
        raise EntryError(f"difficulty must be one of {', '.join(DIFFICULTY_ORDER)}")
    check_same_layer_overlap(value_spans)
    check_same_layer_overlap(cue_spans)

    filled = {
        "annotation": {
            "status": "ANNOTATED",
            "guideline_version": record.get("annotation", {}).get("guideline_version"),
            "reviewer_id": reviewer_id.strip(),
            "value_spans": value_spans,
            "cue_spans": cue_spans,
            "transitions": transitions,
            "links": links,
            "difficulty": difficulty,
            "uncertainty_notes": uncertainty_notes,
        },
    }
    merged = dict(record)
    merged.update(filled)

    canonical = normalize([merged], reviewer_id.strip())
    result = validate_rows(canonical, require_gold=False)
    if result["status"] != "PASS":
        raise EntryError("record rejected by contract: " + "; ".join(result["errors"][:8]))
    return merged


def write_jsonl(path: str, rows: list[dict]) -> None:
    """Write rows; refuse to touch an existing file (protect human work)."""
    if os.path.exists(path):
        raise EntryError(f"refusing to overwrite existing file: {path}")
    with open(path, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path: str, row: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- interactive

def show_example(rec: dict) -> None:
    print("\n" + "=" * 72)
    print("EXAMPLE", rec.get("example_id"), "| dialogue", rec.get("source", {}).get("dialogue_id"),
          "| turn", rec.get("source", {}).get("turn_index"), "| service", rec.get("source", {}).get("service"))
    print("-" * 72)
    for h in rec.get("history", []):
        print(f"  [{h.get('turn_index')}] {h.get('speaker')}: {h.get('utterance')}")
    utt = rec.get("current_user_utterance", "")
    print("-" * 72)
    print("CURRENT USER UTTERANCE (annotate THIS text only):")
    print("  " + utt)
    ruler1 = "".join(str(i // 10 % 10) if i % 5 == 0 else " " for i in range(len(utt)))
    ruler2 = "".join(str(i % 10) if i % 5 == 0 else "." for i in range(len(utt)))
    print("  " + ruler1)
    print("  " + ruler2)


def prompt_span(utt: str, label_order: tuple[str, ...]) -> dict | None:
    for i, lab in enumerate(label_order, 1):
        print(f"    {i}. {lab}")
    raw = input("  label number (ENTER=cancel): ").strip()
    if not raw:
        return None
    try:
        label = label_order[int(raw) - 1]
    except (ValueError, IndexError):
        print("  !! invalid label number")
        return None
    phrase = input("  exact phrase as written in the utterance (ENTER=cancel): ").strip()
    if not phrase:
        return None
    try:
        starts = find_occurrences(utt, phrase)
        occurrence = 1
        if len(starts) > 1:
            print(f"  phrase occurs {len(starts)} times at offsets {starts}")
            occurrence = int(input("  which occurrence number? ").strip() or "1")
        span = make_span(utt, phrase, label, occurrence)
    except (EntryError, ValueError) as exc:
        print("  !!", exc)
        return None
    print(f"  -> {span['label']}: '{span['text']}' [{span['start']},{span['end']})")
    return span


def prompt_transition() -> dict | None:
    for i, op in enumerate(OPERATION_ORDER, 1):
        print(f"    {i}. {op}")
    raw = input("  operation number (ENTER=cancel): ").strip()
    if not raw:
        return None
    try:
        operation = OPERATION_ORDER[int(raw) - 1]
    except (ValueError, IndexError):
        print("  !! invalid operation number")
        return None
    slot = input("  slot / intent (optional): ").strip()
    before = input("  before value (optional): ").strip()
    after = input("  after value (optional): ").strip()
    return {"operation": operation, "slot": slot or None,
            "before": before or None, "after": after or None}


def prompt_link() -> dict | None:
    phrase = input("  reference phrase in utterance (ENTER=cancel): ").strip()
    if not phrase:
        return None
    target = input("  what it refers to (short text): ").strip()
    return {"phrase": phrase, "target": target or None}


def review_one(rec: dict, reviewer_id: str) -> dict | None:
    show_example(rec)
    value_spans: list[dict] = []
    cue_spans: list[dict] = []
    transitions: list[dict] = []
    links: list[dict] = []
    difficulty: str | None = None
    notes = ""
    while True:
        print("\n  current: V=%d C=%d T=%d L=%d D=%s" % (
            len(value_spans), len(cue_spans), len(transitions), len(links), difficulty or "-"))
        cmd = input("  [V]alue [C]ue [T]ransition [L]ink [D]ifficulty [N]ote [K]eep-empty [S]ave [Q]uit > ").strip().lower()
        if cmd == "v":
            span = prompt_span(rec.get("current_user_utterance", ""), VALUE_LABEL_ORDER)
            if span:
                try:
                    check_same_layer_overlap(value_spans + [span])
                    value_spans.append(span)
                except EntryError as exc:
                    print("  !!", exc)
        elif cmd == "c":
            span = prompt_span(rec.get("current_user_utterance", ""), CUE_LABEL_ORDER)
            if span:
                try:
                    check_same_layer_overlap(cue_spans + [span])
                    cue_spans.append(span)
                except EntryError as exc:
                    print("  !!", exc)
        elif cmd == "t":
            tr = prompt_transition()
            if tr:
                transitions.append(tr)
        elif cmd == "l":
            lk = prompt_link()
            if lk:
                links.append(lk)
        elif cmd == "d":
            for i, d in enumerate(DIFFICULTY_ORDER, 1):
                print(f"    {i}. {d} ({DIFFICULTY_HINTS[d]})")
            raw = input("  difficulty number (ENTER=cancel): ").strip()
            if raw:
                try:
                    difficulty = DIFFICULTY_ORDER[int(raw) - 1]
                except (ValueError, IndexError):
                    print("  !! invalid number")
        elif cmd == "n":
            notes = input("  uncertainty / comment: ").strip()
        elif cmd == "k":
            # reviewed-negative: human explicitly saw nothing labelable
            try:
                return fill_record(rec, reviewer_id, [], [], [], [], difficulty, notes)
            except EntryError as exc:
                print("  !!", exc)
        elif cmd == "s":
            try:
                return fill_record(rec, reviewer_id, value_spans, cue_spans,
                                   transitions, links, difficulty, notes)
            except EntryError as exc:
                print("  !!", exc)
        elif cmd == "q":
            return None
        else:
            print("  ?? unknown key")


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Human annotation entry helper (labels come from the human only)")
    ap.add_argument("--packet", required=True, type=Path, help="UNLABELED blind packet jsonl")
    ap.add_argument("--reviewer-id", required=True, help="real reviewer identifier")
    ap.add_argument("--out", required=True, type=Path, help="filled output jsonl (must not exist unless --resume)")
    ap.add_argument("--resume", action="store_true", help="append to --out, skipping already recorded example ids")
    ap.add_argument("--only", help="review a single example id")
    args = ap.parse_args()

    rows = read_jsonl(args.packet)
    if not rows:
        print("packet is empty")
        return 1

    done_ids = set()
    if args.resume and os.path.exists(args.out):
        for row in read_jsonl(args.out):
            done_ids.add(row.get("example_id"))
        print(f"resume: {len(done_ids)} examples already in {args.out}")
    elif os.path.exists(args.out):
        print(f"refusing to overwrite existing file: {args.out} (use --resume to continue)")
        return 1

    pending = [r for r in rows if r.get("example_id") not in done_ids
               and (args.only is None or r.get("example_id") == args.only)]
    print(f"{len(pending)} examples to review. Remember: work independently; "
          f"never open PRIVATE_sampling_manifest.jsonl.")
    try:
        for rec in pending:
            filled = review_one(rec, args.reviewer_id)
            if filled is None:
                print("quit: progress for completed examples is kept in", args.out)
                return 0
            append_jsonl(args.out, filled)
            print("  saved ->", args.out)
    except (EOFError, KeyboardInterrupt):
        print("\ninterrupted: completed examples are kept in", args.out)
        return 0
    print("all done. Next: scripts/normalize_review_packet.py per reviewer, then annotation_agreement.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
