#!/usr/bin/env python3
"""D5 baselines (B0/B1/B2) — surface systems, no learning.

B0 empty          : predicts nothing (documents the record-level accuracy trap:
                    151/457 gold records are span-less, so "predict nothing"
                    looks precise but scores micro-F1 = 0).
B1 lexicon-copy   : memorizes train span texts (lowercased) -> label; matches
                    longest known texts in the utterance.
B2 rules          : hand-written surface rules (cue phrase list + value
                    patterns + history-match for REFERENCE).

All predictions go through the same evaluator: scripts/evaluate_spans.py.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402
import evaluate_spans  # noqa: E402


# ----------------------------------------------------------------- helpers
def find_all(hay: str, needle: str) -> list[int]:
    out, i = [], 0
    while True:
        j = hay.lower().find(needle.lower(), i)
        if j < 0:
            return out
        out.append(j)
        i = j + len(needle)


def pack(hay: str, spans: list[tuple[int, int, str]], vocab: set[str]) -> list[dict]:
    """Keep non-overlapping spans (longest first), labels in vocab."""
    spans = [s for s in spans if s[2] in vocab]
    spans.sort(key=lambda s: (-(s[1] - s[0]), s[0]))
    taken: list[tuple[int, int]] = []
    keep = []
    for s, e, lab in spans:
        if any(e > t0 and s < t1 for t0, t1 in taken):
            continue
        taken.append((s, e))
        keep.append((s, e, lab))
    keep.sort()
    return [{"start": s, "end": e, "text": hay[s:e], "label": lab} for s, e, lab in keep]


# ----------------------------------------------------------------- B0
def b0(row: dict) -> dict:
    return {"id": row["id"], "value_spans": [], "cue_spans": []}


# ----------------------------------------------------------------- B1
def make_b1(train_rows: list[dict]):
    lex: dict[str, collections.Counter] = {"value_spans": collections.Counter(),
                                           "cue_spans": collections.Counter()}
    span_text: dict[str, set] = {"value_spans": set(), "cue_spans": set()}
    for r in train_rows:
        for layer in ("value_spans", "cue_spans"):
            for s in r[layer]:
                span_text[layer].add(s["text"].lower())
                lex[layer][(s["text"].lower(), s["label"])] += 1

    def predict(row: dict) -> dict:
        utt = row["current_user_utterance"]
        out = {"id": row["id"]}
        for layer, vocab in (("value_spans", VALUE_LABELS), ("cue_spans", CUE_LABELS)):
            spans = []
            for txt in span_text[layer]:
                if len(txt) < 2:
                    continue
                for pos in find_all(utt, txt):
                    label = max((l for (t, l) in lex[layer] if t == txt),
                                key=lambda l: lex[layer][(txt, l)])
                    spans.append((pos, pos + len(txt), label))
            out[layer] = pack(utt, spans, vocab)
        return out

    return predict


# ----------------------------------------------------------------- B2
# Phrase lists are BASELINE MODEL rules (surface forms in the input), not
# annotation guidance; the guideline is unaffected by this file.
CUE_PHRASES = [
    (r"\bactually\b", "UPDATE_CUE"),
    (r"\bi meant\b|\bi mean\b", "UPDATE_CUE"),
    (r"\binstead\b", "UPDATE_CUE"),
    (r"\bchange (that|it|this) to\b", "UPDATE_CUE"),
    (r"\bmake (that|it)\b", "UPDATE_CUE"),
    (r"\bon second thought\b", "UPDATE_CUE"),
    (r"\bno,? (i|just)\b", "UPDATE_CUE"),
    (r"\bwait\b", "UPDATE_CUE"),
    (r"\bcancel\b|\bforget (it|that)\b|\bnever ?mind\b", "CANCEL_CUE"),
    (r"\bleave (it|that|them) (as|how) it is\b|\bkeep (it|that|them)\b|\bno change\b", "KEEP_CUE"),
    (r"\bgo back to\b|\bback to the (original|previous|first)\b", "RESTORE_CUE"),
]
MONTHS = ("january|february|march|april|may|june|july|august|september|october|november|december|"
          "jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec")
DAYS = "monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow|tonight"
VALUE_PATTERNS = [
    (r"\b\d{1,2}:\d{2}(?:\s*[ap]\.?m\.?)?\b", "NEW_VALUE"),
    (r"\b\d{1,2}\s*[ap]\.?m\.?\b", "NEW_VALUE"),
    (rf"\b(?:{MONTHS})\b[^,.;]{{0,24}}", "NEW_VALUE"),
    (rf"\b(?:{DAYS})\b[^,.;]{{0,24}}", "NEW_VALUE"),
    (r"\b\d+(?:\.\d+)?\b(?:\s*(?:people|persons|rooms|stops|stars|of us|or more))?", "NEW_VALUE"),
    (r"\b(?:at|for|around|about|until|from)\s+\d+(?:\.\d+)?\b", "NEW_VALUE"),
    (r"\b[A-Z][a-z]+(?:[\s-][A-Z][a-z]+)+\b", "NEW_VALUE"),  # multiword Capitalized (places)
    (r"\bthe same\b[^,.;]*", "REFERENCE"),
]
REF_PHRASES = [r"\bthat one\b", r"\bthe same\b", r"\bthat date\b", r"\bthere\b(?!,)"]


def b2(row: dict, lex: set[str]) -> dict:
    utt = row["current_user_utterance"]
    hist = " ".join(str(h.get("utterance", "")) for h in row.get("history") or [])

    cue = []
    for pat, lab in CUE_PHRASES:
        for m in re.finditer(pat, utt, re.IGNORECASE):
            cue.append((m.start(), m.end(), lab))
    # history-match: utterance fragment that reproduces an earlier user turn span
    for m in re.finditer(r"\b(?:it|that|them|there)\b", utt, re.IGNORECASE):
        pass  # bare pronouns are excluded by C3; deliberately not labeled

    val = []
    for pat, lab in VALUE_PATTERNS:
        for m in re.finditer(pat, utt):
            val.append((m.start(), m.end(), lab))
    for pat in REF_PHRASES:
        for m in re.finditer(pat, utt, re.IGNORECASE):
            val.append((m.start(), m.end(), "REFERENCE"))
    # exact reproduction of a train value span text (copy from earlier context)
    for txt in lex:
        for pos in find_all(utt, txt):
            val.append((pos, pos + len(txt), "NEW_VALUE"))

    return {"id": row["id"],
            "value_spans": pack(utt, val, VALUE_LABELS),
            "cue_spans": pack(utt, cue, CUE_LABELS)}


# ----------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()

    rows = read_jsonl(args.gold)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    split_of = {i: p for p, ids in manifest["splits"].items() for i in ids}
    train = [r for r in rows if split_of[r["id"]] == "train"]
    dev = [r for r in rows if split_of[r["id"]] == "dev"]
    dev_gold = sorted(dev, key=lambda r: r["id"])

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "dev_gold.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in dev_gold), encoding="utf-8")

    train_texts = {s["text"].lower() for r in train for layer in ("value_spans",) for s in r[layer]}
    b1 = make_b1(train)
    systems = {
        "b0_empty": b0,
        "b1_lexicon_copy": b1,
        "b2_rules": lambda r: b2(r, train_texts),
    }
    summary = {}
    for name, fn in systems.items():
        preds = [fn(r) for r in sorted(dev, key=lambda r: r["id"])]
        pred_path = args.outdir / f"pred_{name}_dev.jsonl"
        pred_path.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in preds),
                             encoding="utf-8")
        rep = evaluate_spans.evaluate(dev_gold, preds)
        out_path = args.outdir / f"metrics_{name}_dev.json"
        out_path.write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary[name] = {
            "value_micro_f1": rep["layers"]["value_spans"]["micro"]["f1"],
            "cue_micro_f1": rep["layers"]["cue_spans"]["micro"]["f1"],
            "value_gold_supported": rep["layers"]["value_spans"]["gold_supported_labels"],
            "cue_gold_supported": rep["layers"]["cue_spans"]["gold_supported_labels"],
        }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    (args.outdir / "baseline_summary_dev.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
