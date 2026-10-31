#!/usr/bin/env python3
"""Sample real SGD contexts for the synthetic-data experiment (reports/SYNTHETIC_DATA.md).

A context is the real history of an official-train SGD dialogue up to a SYSTEM turn that confirms or offers concrete
values (acts CONFIRM / OFFER), so a revision is natural as the next user turn. Dialogues used by the released gold or
the locked holdout are excluded, and sampling is spread over services (at most --per-service contexts each).
The real next user turn is not written: the synthetic turn is authored for the context, never copied from SGD.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402

ACTS = {"CONFIRM", "OFFER"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sgd-root", type=Path, required=True)
    ap.add_argument("--exclude", type=Path, nargs="+", required=True, help="gold JSONL files whose dialogues are excluded")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--per-service", type=int, default=20)
    ap.add_argument("--history-turns", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261031)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    used = {(r["source"]["split"], r["source"]["dialogue_id"]) for p in args.exclude for r in read_jsonl(p)}
    by_service = defaultdict(list)
    for f in sorted((args.sgd_root / "train").glob("dialogues_*.json")):
        for d in json.loads(f.read_text(encoding="utf-8")):
            if ("train", d["dialogue_id"]) in used:
                continue
            turns = d["turns"]
            for i in range(2, len(turns) - 1):
                t = turns[i]
                if t["speaker"] != "SYSTEM":
                    continue
                acts = {(a["act"], a.get("slot", "")) for fr in t["frames"] for a in fr["actions"]}
                if not any(act in ACTS for act, _ in acts):
                    continue
                values = sorted({v for fr in t["frames"] for a in fr["actions"] if a["act"] in ACTS for v in a["values"]})
                by_service[t["frames"][0]["service"]].append({
                    "dialogue_id": d["dialogue_id"], "source_file": f.name, "service": t["frames"][0]["service"],
                    "next_turn_index": i + 1, "system_values": values,
                    "history": [{"speaker": x["speaker"], "turn_index": j, "utterance": x["utterance"]}
                                for j, x in enumerate(turns[:i + 1])][-args.history_turns:]})
    rng = random.Random(args.seed)
    picked = []
    for service in sorted(by_service):
        cands = by_service[service]
        rng.shuffle(cands)
        seen, take = set(), []
        for c in cands:  # one context per dialogue
            if c["dialogue_id"] not in seen:
                take.append(c)
                seen.add(c["dialogue_id"])
            if len(take) == args.per_service:
                break
        picked.extend(take)
    rng.shuffle(picked)
    picked = picked[:args.n]
    for k, c in enumerate(picked):
        c["context_id"] = f"CTX-{k:04d}"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in picked), encoding="utf-8")
    print(json.dumps({"contexts": len(picked), "services": len({c["service"] for c in picked}),
                      "excluded_dialogues": len(used), "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
