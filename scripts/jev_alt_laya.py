#!/usr/bin/env python3
"""JEV-alternative row: Laya (open decision model, convaiinnovations/laya, Apache-2.0) used zero-shot.

Laya answers typed questions about a text; it has no token head. Each word of the current user turn is asked about
separately: the word is marked with << >> inside the state (the last earlier turns + the current turn) and Laya picks its
role. Consecutive words with the same role form one span; punctuation-only words are never part of a span.

Four variants are fixed in advance (reports/JEV_ALTERNATIVE.md): question type (one `choice` question, or three yes/no
`noul` questions with argmax above 0.5) x checkpoint (english, multilingual). `select` scores all four on the train-side
gold, which Laya never saw; `predict` runs the selected variant on any input. Labels of the input are never read.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from d5_train_crf import decode  # noqa: E402
from evaluate_spans import evaluate  # noqa: E402
from span_tokenizer import tokenize  # noqa: E402
from validate_annotations import read_jsonl  # noqa: E402

VARIANTS = {"choice_en": ("choice", "english"), "choice_ml": ("choice", "multilingual"),
            "noul_en": ("noul", "english"), "noul_ml": ("noul", "multilingual")}
HISTORY_TURNS = 4
ROLES = {"UPDATE_CUE": "the marked word signals that the user changes an earlier request (actually, instead, make it)",
         "NEW_VALUE": "the marked word is part of the new value the user now wants (a time, date, name, place, number)",
         "REFERENCE": "the marked word is part of a phrase that points back to something said earlier (the same place, "
                      "that one)",
         "O": "the marked word plays none of these roles"}
NOUL = {"UPDATE_CUE": "Is the word marked with << >> a word that signals the user is changing an earlier request, such as "
                      "actually, instead or make it?",
        "NEW_VALUE": "Is the word marked with << >> part of a new concrete value (time, date, name, place, number) that "
                     "the user now asks for?",
        "REFERENCE": "Is the word marked with << >> part of a phrase that refers back to something mentioned in an "
                     "earlier turn, such as the same place?"}
CHOICE_Q = {"role": {"type": "choice", "criteria": ROLES,
                     "instructions": "What role does the word marked with << >> play in the current user turn?"}}
NOUL_Q = {lab: {"type": "noul", "instructions": q} for lab, q in NOUL.items()}


def state_for(row: dict, words: list[dict], i: int) -> str:
    utt = row["current_user_utterance"]
    w = words[i]
    marked = utt[:w["start"]] + "<<" + utt[w["start"]:w["end"]] + ">>" + utt[w["end"]:]
    hist = [f"{h.get('speaker', 'USER')}: {h.get('utterance', '')}" for h in (row.get("history") or [])][-HISTORY_TURNS:]
    return "Earlier turns:\n" + ("\n".join(hist) if hist else "(none)") + "\nCurrent user turn: " + marked


def word_label(answer: dict, qtype: str) -> str:
    if qtype == "choice":
        return answer["role"]["choice"]
    probs = {lab: answer[lab]["noul"] for lab in NOUL}
    best = max(probs, key=probs.get)
    return best if probs[best] > 0.5 else "O"


def predict(router, rows: list[dict], variant: str, batch_size: int) -> list[dict]:
    qtype, model = VARIANTS[variant]
    questions = CHOICE_Q if qtype == "choice" else NOUL_Q
    words = {r["id"]: [t._asdict() for t in tokenize(r["current_user_utterance"])] for r in rows}
    requests, index = [], []
    for r in rows:
        for i, w in enumerate(words[r["id"]]):
            if any(ch.isalnum() for ch in w["text"]):
                requests.append({"state": state_for(r, words[r["id"]], i), "questions": questions, "model": model})
                index.append((r["id"], i))
    answers = router.predict_batch(requests, batch_size=batch_size, sort_by_length=True)
    labels = {r["id"]: ["O"] * len(words[r["id"]]) for r in rows}
    for (rid, i), res in zip(index, answers):
        labels[rid][i] = word_label(res["answers"], qtype)
    out = []
    for r in rows:
        tags, prev = [], "O"
        for lab in labels[r["id"]]:
            tags.append("O" if lab == "O" else ("I-" if lab == prev else "B-") + lab)
            prev = lab
        spans = decode(words[r["id"]], tags)
        for s in spans:
            s["text"] = r["current_user_utterance"][s["start"]:s["end"]]
        out.append({"id": r["id"],
                    "value_spans": [s for s in spans if s["label"] in ("NEW_VALUE", "REFERENCE")],
                    "cue_spans": [s for s in spans if s["label"] == "UPDATE_CUE"]})
    return out


def write_jsonl(path: Path, rows: list[dict]) -> None:
    if path.exists():
        raise SystemExit(f"ABORT: refusing to overwrite: {path}")
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select", help="score the four variants on train-side gold")
    s.add_argument("--gold", type=Path, required=True)
    s.add_argument("--outdir", type=Path, required=True)
    p = sub.add_parser("predict", help="run one variant on an input JSONL")
    p.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    for a in (s, p):
        a.add_argument("--batch-size", type=int, default=64)
    args = ap.parse_args()

    from laya import Router  # heavy import, only when running
    router = Router(device="cuda")

    if args.cmd == "predict":
        rows = [{"id": r["id"], "current_user_utterance": r["current_user_utterance"], "history": r.get("history") or []}
                for r in read_jsonl(args.input)]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        write_jsonl(args.out, predict(router, rows, args.variant, args.batch_size))
        print(json.dumps({"status": "PREDICTED", "variant": args.variant, "examples": len(rows), "out": str(args.out)}))
        return 0

    gold = read_jsonl(args.gold)
    rows = [{"id": r["id"], "current_user_utterance": r["current_user_utterance"], "history": r.get("history") or []}
            for r in gold]
    args.outdir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for variant in VARIANTS:
        t0 = time.time()
        preds = predict(router, rows, variant, args.batch_size)
        write_jsonl(args.outdir / f"pred_{variant}.jsonl", preds)
        layers = evaluate(gold, preds)["layers"]
        v, c = layers["value_spans"]["micro"]["f1"] or 0.0, layers["cue_spans"]["micro"]["f1"] or 0.0
        summary[variant] = {"value_f1": v, "cue_f1": c, "S": round((v + c) / 2, 6),
                            "per_label": {lab: m["f1"] for layer in layers.values()
                                          for lab, m in layer["classes"].items() if m["tp"] + m["fn"] > 0},
                            "seconds": round(time.time() - t0, 1)}
        print(variant, json.dumps(summary[variant]), flush=True)
    chosen = max(summary, key=lambda k: summary[k]["S"])
    result = {"gold": str(args.gold), "examples": len(gold), "variants": summary, "selected": chosen,
              "rule": "highest S on train-side gold; ties broken by the order choice_en, choice_ml, noul_en, noul_ml"}
    (args.outdir / "select.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected": chosen, "S": summary[chosen]["S"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
