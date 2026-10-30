#!/usr/bin/env python3
"""Export the released raw (unlabeled) turns and check them against the original SGD files.

Writes one row per annotated turn with only the model inputs and provenance (id, SGD source, family, history,
current user utterance) and no labels. With --sgd-root, every utterance and history turn is compared with the pinned
upstream SGD dialogue at the recorded turn index; any difference aborts.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402

KEEP = ("id", "source", "dialogue_family_id", "history", "current_user_utterance")


def load_sgd(root: Path) -> dict[tuple[str, str], dict]:
    out = {}
    for split in ("train", "dev", "test"):
        for f in sorted(glob.glob(os.path.join(root, split, "dialogues_*.json"))):
            for d in json.load(open(f, encoding="utf-8")):
                out[(split, d["dialogue_id"])] = d
    return out


def check_against_sgd(row: dict, sgd: dict) -> list[str]:
    src = row["source"]
    d = sgd.get((src["split"], src["dialogue_id"]))
    if d is None:
        return [f"{row['id']}: dialogue {src['split']}/{src['dialogue_id']} not in SGD"]
    turns = d["turns"]
    problems = []
    if turns[src["turn_index"]]["utterance"] != row["current_user_utterance"]:
        problems.append(f"{row['id']}: utterance differs from SGD turn {src['turn_index']}")
    for h in row.get("history") or []:
        if "turn_index" in h and turns[h["turn_index"]]["utterance"] != h["utterance"]:
            problems.append(f"{row['id']}: history turn {h['turn_index']} differs from SGD")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sgd-root", type=Path, default=None, help="pinned SGD clone; verifies every exported text")
    args = ap.parse_args()

    rows = [{k: r[k] for k in KEEP} for path in args.gold for r in read_jsonl(path)]
    rows.sort(key=lambda r: r["id"])
    if len({r["id"] for r in rows}) != len(rows):
        raise SystemExit("duplicate ids across gold files")
    checked = 0
    if args.sgd_root:
        sgd = load_sgd(args.sgd_root)
        problems = [p for r in rows for p in check_against_sgd(r, sgd)]
        if problems:
            raise SystemExit("SGD cross-check failed:\n" + "\n".join(problems[:10]))
        checked = len(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"rows": len(rows), "verified_against_sgd": checked, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
