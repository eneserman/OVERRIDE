#!/usr/bin/env python3
"""D3-EXT round 2 (amendment E3): blind cross re-annotation of the 320 single-annotated D3-EXT records.

Burak receives Enes's 160 solo records and Enes receives Burak's 160, copied from the original blind packets
(UNLABELED, no labels, no hints). Order is shuffled per reviewer by sha256('<seed>:<who>:<id>').
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SEED = 20261031
PACKET_KEYS = {"example_id", "source", "history", "current_user_utterance", "annotation"}


def cross_packet(blind_rows: list[dict], solo_ids: list[str], who: str, seed: int = SEED) -> list[dict]:
    by_id = {r["example_id"]: r for r in blind_rows}
    missing = [i for i in solo_ids if i not in by_id]
    if missing:
        raise SystemExit(f"solo ids missing from the blind packet: {missing[:3]}")
    out = []
    for rid in sorted(solo_ids, key=lambda i: hashlib.sha256(f"{seed}:{who}:{i}".encode()).hexdigest()):
        rec = json.loads(json.dumps(by_id[rid]))
        ann = rec["annotation"]
        if set(rec) != PACKET_KEYS or ann.get("status") != "UNLABELED" or ann.get("value_spans") or ann.get("cue_spans"):
            raise SystemExit(f"{rid}: source row is not a clean blind packet row")
        out.append(rec)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, required=True, help="data/annotations/d3_ext_v0.1")
    args = ap.parse_args()
    d = args.dir
    index = json.loads((d / "PRIVATE_ext_index.json").read_text(encoding="utf-8"))
    rd = lambda p: [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
    plan = {"reviewer_A_BURAK_EK2_BLIND.jsonl": cross_packet(rd(d / "reviewer_B_ENES_EK_BLIND.jsonl"), index["assignment"]["B"], "A"),
            "reviewer_B_ENES_EK2_BLIND.jsonl": cross_packet(rd(d / "reviewer_A_BURAK_EK_BLIND.jsonl"), index["assignment"]["A"], "B")}
    shas = {}
    for name, rows in plan.items():
        p = d / name
        if p.exists():
            raise SystemExit(f"ABORT: refusing to overwrite {p}")
        p.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
        shas[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    idx2 = {"status": "D3_EXT_ROUND2_PACKETS_NOT_GOLD", "protocol": "reports/D3_EXT_PROTOCOL.md §9 (E3)", "seed": SEED,
            "burak_reannotates_enes_solo": index["assignment"]["B"], "enes_reannotates_burak_solo": index["assignment"]["A"],
            "packets_sha256": shas}
    p = d / "PRIVATE_ext2_index.json"
    if p.exists():
        raise SystemExit(f"ABORT: refusing to overwrite {p}")
    p.write_text(json.dumps(idx2, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "D3_EXT_ROUND2_PACKETS_BUILT", "per_reviewer": {n: len(r) for n, r in plan.items()},
                      "packets_sha256": shas}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
