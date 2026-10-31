#!/usr/bin/env python3
"""Why strict span F1 and not token accuracy: score an all-O tagger and a real prediction file both ways.

Token accuracy counts every word, and most words carry no label, so a tagger that labels nothing still looks accurate.
Strict span F1 gives that tagger 0.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from d5_prepare_data import bio_tags  # noqa: E402
from evaluate_spans import evaluate  # noqa: E402
from span_tokenizer import tokenize  # noqa: E402
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402

LAYERS = (("value_spans", VALUE_LABELS), ("cue_spans", CUE_LABELS))


def token_accuracy(gold: list[dict], pred: dict[str, dict]) -> dict:
    out, all_hit, all_n = {}, 0, 0
    for layer, labels in LAYERS:
        hit = n = 0
        for r in gold:
            toks = tokenize(r["current_user_utterance"])
            g, _ = bio_tags(toks, r[layer], labels)
            p, _ = bio_tags(toks, pred[r["id"]][layer], labels)
            hit += sum(a == b for a, b in zip(g, p))
            n += len(g)
        out[layer] = round(hit / n, 4)
        all_hit, all_n = all_hit + hit, all_n + n
    out["both_layers"] = round(all_hit / all_n, 4)
    return out


def span_s(gold: list[dict], preds: list[dict], accept_consensus: bool) -> dict:
    layers = evaluate(gold, preds, accept_consensus=accept_consensus,
                      allowed_splits=("train", "dev", "test"))["layers"]
    v, c = layers["value_spans"]["micro"]["f1"] or 0.0, layers["cue_spans"]["micro"]["f1"] or 0.0
    return {"value_f1": v, "cue_f1": c, "S": round((v + c) / 2, 4)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", type=Path, required=True)
    ap.add_argument("--pred", type=Path, nargs="*", default=[], help="prediction files to score both ways")
    ap.add_argument("--accept-consensus-reference", action="store_true")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    gold = read_jsonl(args.gold)
    labeled = sum(t != "O" for r in gold for layer, labels in LAYERS
                  for t in bio_tags(tokenize(r["current_user_utterance"]), r[layer], labels)[0])
    words = sum(len(tokenize(r["current_user_utterance"])) for r in gold)
    systems = {"all_O": [{"id": r["id"], "value_spans": [], "cue_spans": []} for r in gold]}
    for p in args.pred:
        systems[p.stem] = read_jsonl(p)
    result = {"gold": str(args.gold), "records": len(gold), "words": words,
              "labeled_word_share_per_layer": round(labeled / (2 * words), 4), "systems": {}}
    for name, preds in systems.items():
        by_id = {r["id"]: r for r in preds}
        result["systems"][name] = {"token_accuracy": token_accuracy(gold, by_id),
                                   "span_f1": span_s(gold, preds, args.accept_consensus_reference)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
