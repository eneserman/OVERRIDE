#!/usr/bin/env python3
"""Blind cross re-annotation audit of the 357 single-annotated gold v1 records.

Pre-registered in reports/D3_GOLD_V1_AUDIT_PROTOCOL.md BEFORE any audit label
exists. Two subcommands, both fail-closed and refusing to overwrite:

  sample  deterministic hash-ranked sample from each solo set
          (sha256('<seed>::<id>') ascending, first N per set). Burak's solo
          records go to Enes and vice versa; packets are copied from the blind
          457 packets (no labels, no hints, no gold) and stamped v0.2.3.
  score   compares the canonical re-annotations with gold v1 on the sampled
          IDs: exact layer-set agreement per record + per-label exact-span
          P/R/F1 with gold v1 as reference. Mechanical only; disagreements are
          listed for the two reviewers, never resolved here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402

AUDIT_GUIDELINE = "v0.2.3"
LAYERS = ("value_spans", "cue_spans")


def rank_key(seed: int, rid: str) -> str:
    return hashlib.sha256(f"{seed}::{rid}".encode("utf-8")).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pick(ids: list[str], seed: int, n: int) -> list[str]:
    if n > len(ids):
        raise SystemExit(f"sample size {n} exceeds pool {len(ids)}")
    return sorted(sorted(ids, key=lambda i: rank_key(seed, i))[:n])


def blind_rows(packet: Path, wanted: list[str]) -> list[dict]:
    by_id = {r["example_id"]: r for r in read_jsonl(packet)}
    missing = [i for i in wanted if i not in by_id]
    if missing:
        raise SystemExit(f"{packet}: sampled ids missing from blind packet: {missing[:5]}")
    out = []
    for rid in wanted:
        row = json.loads(json.dumps(by_id[rid]))
        ann = row.get("annotation") or {}
        if ann.get("status") != "UNLABELED" or ann.get("value_spans") or ann.get("cue_spans"):
            raise SystemExit(f"{rid}: blind packet row is not UNLABELED/empty")
        ann["guideline_version"] = AUDIT_GUIDELINE
        out.append(row)
    return out


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"ABORT: refusing to overwrite: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def cmd_sample(args: argparse.Namespace) -> int:
    index = json.loads(args.assignment.read_text(encoding="utf-8"))
    solo_a, solo_b = list(index["solo_A_ids"]), list(index["solo_B_ids"])
    if (len(solo_a), len(solo_b)) != (178, 179) or set(solo_a) & set(solo_b):
        raise SystemExit(f"unexpected solo sets: A={len(solo_a)} B={len(solo_b)}")
    gold_ids = {r["id"] for r in read_jsonl(args.gold)}
    if not set(solo_a) | set(solo_b) <= gold_ids:
        raise SystemExit("solo ids not all present in gold v1")
    excluded = sorted(set(args.exclude_ids.split(","))) if args.exclude_ids else []
    unknown = [i for i in excluded if i not in set(solo_a) | set(solo_b)]
    if unknown:
        raise SystemExit(f"excluded ids are not solo records: {unknown}")
    solo_a = [i for i in solo_a if i not in excluded]
    solo_b = [i for i in solo_b if i not in excluded]

    a_sample = pick(solo_a, args.seed, args.per_set)  # Burak's records -> Enes
    b_sample = pick(solo_b, args.seed, args.per_set)  # Enes's records -> Burak
    packets = {
        "ENES_reannotates_BURAK_solo_BLIND.jsonl": blind_rows(args.blind_a, a_sample),
        "BURAK_reannotates_ENES_solo_BLIND.jsonl": blind_rows(args.blind_b, b_sample),
    }
    for name, rows in packets.items():
        write_new(args.outdir / name, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))

    audit_index = {
        "status": "GOLD_V1_AUDIT_SAMPLE_NOT_GOLD",
        "protocol": "reports/D3_GOLD_V1_AUDIT_PROTOCOL.md",
        "rule": "per solo set: sort ids by sha256('<seed>::<id>') ascending, take first per_set",
        "seed": args.seed,
        "per_set": args.per_set,
        "excluded_before_sampling": excluded,
        "gold_v1_file_sha256": file_sha(args.gold),
        "assignment_index_sha256": file_sha(args.assignment),
        "samples": {
            "solo_A_BURAK_reannotated_by_ENES": a_sample,
            "solo_B_ENES_reannotated_by_BURAK": b_sample,
        },
        "packets_sha256": {name: file_sha(args.outdir / name) for name in packets},
        "note": "Coordinator-only index. Reviewers see only their packet; never gold v1, never this file.",
    }
    write_new(args.outdir / "PRIVATE_audit_index.json",
              json.dumps(audit_index, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": "AUDIT_SAMPLE_BUILT", "per_set": args.per_set,
                      "packets_sha256": audit_index["packets_sha256"]}, indent=2))
    return 0


def span_set(row: dict, layer: str) -> set[tuple]:
    return {(s["start"], s["end"], s["label"]) for s in row.get(layer) or []}


def prf(tp: int, fp: int, fn: int) -> dict:
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    f = 2 * p * r / (p + r) if p and r else (0.0 if (tp + fp) and (tp + fn) else None)
    return {"precision": p, "recall": r, "f1": f, "tp": tp, "fp": fp, "fn": fn,
            "gold_support": tp + fn,
            "evaluable": (tp + fn) > 0}


def score_rows(gold: dict[str, dict], reann: dict[str, dict], ids: list[str]) -> dict:
    counts = {layer: Counter() for layer in LAYERS}
    agree, disagreements = 0, []
    for rid in ids:
        g, a = gold[rid], reann[rid]
        same = True
        for layer in LAYERS:
            gs, as_ = span_set(g, layer), span_set(a, layer)
            same &= gs == as_
            for _, _, lab in gs & as_:
                counts[layer][(lab, "tp")] += 1
            for _, _, lab in as_ - gs:
                counts[layer][(lab, "fp")] += 1
            for _, _, lab in gs - as_:
                counts[layer][(lab, "fn")] += 1
        if same:
            agree += 1
        else:
            disagreements.append(rid)
    layers = {}
    for layer in LAYERS:
        labels = sorted({lab for lab, _ in counts[layer]})
        per = {lab: prf(counts[layer][(lab, "tp")], counts[layer][(lab, "fp")],
                        counts[layer][(lab, "fn")]) for lab in labels}
        tot = [sum(counts[layer][(lab, k)] for lab in labels) for k in ("tp", "fp", "fn")]
        layers[layer] = {"micro": prf(*tot), "per_label": per}
    return {"records": len(ids), "exact_layer_set_agreement": agree / len(ids) if ids else None,
            "agreeing_records": agree, "disagreeing_ids": disagreements, "layers": layers}


def cmd_score(args: argparse.Namespace) -> int:
    index = json.loads(args.index.read_text(encoding="utf-8"))
    if file_sha(args.gold) != index["gold_v1_file_sha256"]:
        raise SystemExit("gold v1 changed since the audit sample was drawn")
    gold = {r["id"]: r for r in read_jsonl(args.gold)}
    parts = {
        "solo_A_BURAK_reannotated_by_ENES": (args.enes_canonical, "reviewer_B_ENES"),
        "solo_B_ENES_reannotated_by_BURAK": (args.burak_canonical, "reviewer_A_BURAK"),
    }
    report = {"status": "GOLD_V1_AUDIT_MEASURED", "gold_v1_file_sha256": index["gold_v1_file_sha256"],
              "parts": {}}
    pooled_gold, pooled_re, pooled_ids = {}, {}, []
    for part, (path, reviewer) in parts.items():
        ids = index["samples"][part]
        rows = {r["id"]: r for r in read_jsonl(path)}
        if set(rows) != set(ids):
            raise SystemExit(f"{path}: ids differ from the pre-drawn sample")
        bad = [rid for rid, r in rows.items()
               if (r.get("annotation") or {}).get("reviewer_id") != reviewer]
        if bad:
            raise SystemExit(f"{path}: expected reviewer {reviewer} on every row, e.g. {bad[:3]}")
        report["parts"][part] = score_rows(gold, rows, ids)
        report["parts"][part]["input_sha256"] = file_sha(path)
        pooled_gold.update({i: gold[i] for i in ids})
        pooled_re.update(rows)
        pooled_ids += ids
    report["pooled"] = score_rows(pooled_gold, pooled_re, sorted(pooled_ids))
    report["caveat"] = ("Each re-annotator saw the original labels earlier during the non-blind DOGRULAMA "
                        "verification; this audit is blind to labels at annotation time but not "
                        "exposure-naive. Disagreements are resolved only by joint reviewer decision.")
    write_new(args.out, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": report["status"],
                      "pooled_exact_layer_set_agreement": report["pooled"]["exact_layer_set_agreement"],
                      "disagreeing_records": len(report["pooled"]["disagreeing_ids"])}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--assignment", type=Path, required=True)
    s.add_argument("--blind-a", type=Path, required=True, help="reviewer A blind 457 packet (holds solo_A rows)")
    s.add_argument("--blind-b", type=Path, required=True, help="reviewer B blind 457 packet (holds solo_B rows)")
    s.add_argument("--gold", type=Path, required=True)
    s.add_argument("--seed", type=int, default=20261030)
    s.add_argument("--per-set", type=int, default=24)
    s.add_argument("--exclude-ids", help="comma-separated solo ids removed from the pool before sampling "
                                         "(pre-registered: findings already shown to a reviewer)")
    s.add_argument("--outdir", type=Path, required=True)
    c = sub.add_parser("score")
    c.add_argument("--index", type=Path, required=True)
    c.add_argument("--gold", type=Path, required=True)
    c.add_argument("--enes-canonical", type=Path, required=True)
    c.add_argument("--burak-canonical", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    return cmd_sample(args) if args.cmd == "sample" else cmd_score(args)


if __name__ == "__main__":
    raise SystemExit(main())
