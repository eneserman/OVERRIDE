#!/usr/bin/env python3
"""Build the declared synthetic training set (reports/SYNTHETIC_DATA.md) and its quality report.

Input: real SGD contexts (`synth_contexts.py`) and AI-authored turns (`data/synthetic/authored_*.jsonl`: context_id,
utterance, spans as [text, label] pairs; each text must occur exactly once). Offsets are computed here, never typed.
Every record is marked `annotation.status = SYNTHETIC_AI`; the human gold files are never touched.

Quality checks (fail-closed): unknown context, label outside the vocabulary, span text missing or ambiguous, same-layer
overlap, duplicate utterance, utterance identical to any real SGD user turn in the gold files, and near-duplicates
(token Jaccard >= 0.8) among synthetic turns. Diversity statistics are written to the report.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402

AUTHOR = "Claude Opus 5.5 (AI), declared synthetic"


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def distinct_n(texts: list[str], n: int) -> float:
    grams = [tuple(w[i:i + n]) for w in map(words, texts) for i in range(len(w) - n + 1)]
    return round(len(set(grams)) / len(grams), 4) if grams else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contexts", type=Path, nargs="+", required=True)
    ap.add_argument("--authored", type=Path, nargs="+", required=True)
    ap.add_argument("--gold", type=Path, nargs="+", required=True, help="human gold, for the copy check")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    contexts = {c["context_id"]: c for p in args.contexts for c in read_jsonl(p)}
    real_turns = {r["current_user_utterance"].strip().lower() for p in args.gold for r in read_jsonl(p)}
    rows, errors = [], []
    for path in args.authored:
        for a in read_jsonl(path):
            cid, utt = a["context_id"], a["utterance"]
            if cid not in contexts:
                errors.append(f"{cid}: unknown context")
                continue
            value, cue = [], []
            for text, label in a["spans"]:
                if utt.count(text) != 1:
                    errors.append(f"{cid}: span text {text!r} occurs {utt.count(text)} times")
                    continue
                start = utt.index(text)
                span = {"start": start, "end": start + len(text), "label": label, "text": text}
                if label in VALUE_LABELS:
                    value.append(span)
                elif label in CUE_LABELS:
                    cue.append(span)
                else:
                    errors.append(f"{cid}: unknown label {label}")
            for layer in (value, cue):
                layer.sort(key=lambda s: s["start"])
                if any(x["end"] > y["start"] for x, y in zip(layer, layer[1:])):
                    errors.append(f"{cid}: same-layer overlap")
            if utt.strip().lower() in real_turns:
                errors.append(f"{cid}: utterance copies a real SGD turn")
            c = contexts[cid]
            rows.append({"id": f"SYN-{cid[4:]}", "source": {"dataset": "SGD-context+synthetic-turn",
                                                           "dialogue_id": c["dialogue_id"], "service": c["service"],
                                                           "source_file": c["source_file"], "split": "train",
                                                           "turn_index": c["next_turn_index"]},
                         "dialogue_family_id": c["dialogue_id"], "history": c["history"],
                         "current_user_utterance": utt, "value_spans": value, "cue_spans": cue,
                         "annotation": {"status": "SYNTHETIC_AI", "author": AUTHOR,
                                        "guideline_version": "v0.2.3"}})
    utts = [r["current_user_utterance"] for r in rows]
    dupes = [u for u, k in Counter(u.lower() for u in utts).items() if k > 1]
    errors += [f"duplicate utterance: {u!r}" for u in dupes]
    near = [(a, b) for a, b in combinations(utts, 2)
            if (sa := set(words(a))) and (sb := set(words(b))) and len(sa & sb) / len(sa | sb) >= 0.8]
    errors += [f"near-duplicate: {a!r} / {b!r}" for a, b in near]
    if errors:
        print("\n".join(errors))
        raise SystemExit(f"ABORT: {len(errors)} problems, nothing written")

    labels = Counter(s["label"] for r in rows for s in r["value_spans"] + r["cue_spans"])
    cues = Counter(s["text"].lower() for r in rows for s in r["cue_spans"])
    starts = Counter(" ".join(words(u)[:2]) for u in utts)
    gold_utts = [r["current_user_utterance"] for p in args.gold for r in read_jsonl(p)]
    report = {"records": len(rows), "services": len({r["source"]["service"] for r in rows}),
              "records_without_spans": sum(not (r["value_spans"] or r["cue_spans"]) for r in rows),
              "label_counts": dict(labels.most_common()), "cue_phrases": dict(cues.most_common()),
              "most_common_openings": dict(starts.most_common(10)),
              "max_share_of_one_opening": round(starts.most_common(1)[0][1] / len(rows), 4),
              "distinct_1": distinct_n(utts, 1), "distinct_2": distinct_n(utts, 2),
              "human_gold_distinct_1_same_size": distinct_n(gold_utts[:len(rows)], 1),
              "human_gold_distinct_2_same_size": distinct_n(gold_utts[:len(rows)], 2),
              "near_duplicates_jaccard_0_8": 0, "copies_of_real_turns": 0}
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
