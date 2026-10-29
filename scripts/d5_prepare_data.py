#!/usr/bin/env python3
"""Prepare tokenized BIO training data for D5 from frozen gold + frozen split.

Outputs (under --outdir, default data/intermediate/d5/):
  train.jsonl / dev.jsonl  — one row per example:
    {id, split, tokens:[{start,end,text}], value_tags:[...], cue_tags:[...]}
  prepare_report.json      — counts, label inventory, boundary compatibility

Notes:
  - BIO tags are derived mechanically from gold char spans; no label is invented.
  - Gold spans that do not align to token boundaries are counted and reported
    (token models can only emit token-aligned offsets).
  - Predictions are decoded back to exact char offsets for evaluate_spans.py.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402
from span_tokenizer import partial_overlap, span_tokens, tokenize  # noqa: E402


def bio_tags(tokens, spans, allowed: set[str]) -> tuple[list[str], list[str]]:
    """Greedy left-to-right BIO. Returns (tags, problems)."""
    tags = ["O"] * len(tokens)
    problems: list[str] = []
    ordered = sorted(spans, key=lambda s: (s["start"], s["end"]))
    for span in ordered:
        idxs = span_tokens(tokens, span["start"], span["end"])
        if not idxs:
            problems.append(f"no token inside span {span}")
            continue
        if partial_overlap(tokens, span["start"], span["end"]):
            problems.append(f"token straddles span boundary: {span}")
        label = span["label"]
        if label not in allowed:
            problems.append(f"bad label {label}")
            continue
        for pos, ti in enumerate(idxs):
            if tags[ti] != "O":
                problems.append(f"overlap after tokenization at token {ti}: {span}")
            tags[ti] = ("B-" if pos == 0 else "I-") + label
    return tags, problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()

    rows = read_jsonl(args.gold)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    split_of = {}
    for part, ids in manifest["splits"].items():
        for rid in ids:
            split_of[rid] = part

    args.outdir.mkdir(parents=True, exist_ok=True)
    report = {
        "gold": str(args.gold),
        "gold_content_sha256_expected": manifest["gold_content_sha256"],
        "manifest_digest": manifest["manifest_digest"],
        "counts": collections.Counter(),
        "value_labels": sorted(VALUE_LABELS),
        "cue_labels": sorted(CUE_LABELS),
        "boundary_straddles": [],
        "problems": [],
        "tag_inventory": {"value": collections.Counter(), "cue": collections.Counter()},
        "per_split": {},
    }

    out_rows: dict[str, list] = {"train": [], "dev": []}
    for row in sorted(rows, key=lambda r: r["id"]):
        rid = row["id"]
        if rid not in split_of:
            report["problems"].append(f"{rid}: not in frozen manifest")
            continue
        tokens = tokenize(row["current_user_utterance"])
        vtags, vprobs = bio_tags(tokens, row["value_spans"], VALUE_LABELS)
        ctags, cprobs = bio_tags(tokens, row["cue_spans"], CUE_LABELS)
        for p in vprobs + cprobs:
            if "straddles" in p:
                report["boundary_straddles"].append(f"{rid}: {p}")
            else:
                report["problems"].append(f"{rid}: {p}")
        out_rows[split_of[rid]].append({
            "id": rid,
            "split": split_of[rid],
            "tokens": [t._asdict() for t in tokens],
            "value_tags": vtags,
            "cue_tags": ctags,
        })
        report["counts"][split_of[rid]] += 1
        report["tag_inventory"]["value"].update(vtags)
        report["tag_inventory"]["cue"].update(ctags)

    for part, rws in out_rows.items():
        path = args.outdir / f"{part}.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for r in rws:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        sup = collections.Counter()
        for r in rws:
            sup.update(t for t in r["value_tags"] + r["cue_tags"] if t != "O")
        report["per_split"][part] = {"records": len(rws), "bio_tag_support": dict(sorted(sup.items()))}

    report["counts"] = dict(report["counts"])
    report["tag_inventory"] = {k: dict(sorted(v.items())) for k, v in report["tag_inventory"].items()}
    report["status"] = "FAIL" if (report["problems"] or report["boundary_straddles"]) else "PASS"
    (args.outdir / "prepare_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "counts", "boundary_straddles", "problems", "per_split")},
                     indent=2, ensure_ascii=False)[:3000])
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
