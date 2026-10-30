#!/usr/bin/env python3
"""D6 comparison rows (reports/D5V2_PROTOCOL.md section 6): fit B1, B2 and the CRF on ALL train-side gold with their
fixed D5 configurations and write predictions for an input JSONL. No tuning; labels of the input are never read.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import sklearn_crfsuite

sys.path.insert(0, str(Path(__file__).resolve().parent))
from d5_prepare_data import bio_tags  # noqa: E402
from d5_run_baselines import b2, make_b1  # noqa: E402
from d5_train_crf import decode, word_features  # noqa: E402
from span_tokenizer import tokenize  # noqa: E402
from validate_annotations import CUE_LABELS, VALUE_LABELS, read_jsonl  # noqa: E402


def crf_predict(train: list[dict], rows: list[dict]) -> dict[str, dict]:
    """Linear-chain CRF per layer, c1 = c2 = 0.1, 200 iterations, history = no (as in D5)."""
    def tokens(r):
        return [t._asdict() for t in tokenize(r["current_user_utterance"])]

    out = {r["id"]: {"id": r["id"], "value_spans": [], "cue_spans": []} for r in rows}
    for layer, labels in (("value_spans", VALUE_LABELS), ("cue_spans", CUE_LABELS)):
        X, y = [], []
        for r in train:
            toks = tokens(r)
            tags, problems = bio_tags(tokenize(r["current_user_utterance"]), r[layer], labels)
            if problems:
                raise SystemExit(f"{r['id']}: BIO problems {problems}")
            X.append([word_features(toks, i, "", False) for i in range(len(toks))])
            y.append(tags)
        model = sklearn_crfsuite.CRF(algorithm="lbfgs", c1=0.1, c2=0.1, max_iterations=200,
                                     all_possible_transitions=True)
        model.fit(X, y)
        for r in rows:
            toks, utt = tokens(r), r["current_user_utterance"]
            seq = model.predict([[word_features(toks, i, "", False) for i in range(len(toks))]])[0]
            for s in decode(toks, seq):
                s["text"] = utt[s["start"]:s["end"]]
                out[r["id"]][layer].append(s)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-gold", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True, help="rows with id, current_user_utterance, history")
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()

    train = read_jsonl(args.train_gold)
    rows = [{"id": r["id"], "current_user_utterance": r["current_user_utterance"], "history": r.get("history") or []}
            for r in read_jsonl(args.input)]  # only the model inputs are kept
    paths = {n: args.outdir / f"pred_{n}.jsonl" for n in ("b1_lexicon_copy", "b2_rules", "crf_hno")}
    for p in paths.values():
        if p.exists():
            raise SystemExit(f"ABORT: refusing to overwrite: {p}")
    args.outdir.mkdir(parents=True, exist_ok=True)

    b1 = make_b1(train)
    train_texts = {s["text"].lower() for r in train for s in r["value_spans"]}
    crf = crf_predict(train, rows)
    systems = {"b1_lexicon_copy": [b1(r) for r in rows],
               "b2_rules": [b2(r, train_texts) for r in rows],
               "crf_hno": [crf[r["id"]] for r in rows]}
    for name, preds in systems.items():
        paths[name].write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in preds), encoding="utf-8")
    print(json.dumps({"status": "PREDICTED", "train_records": len(train), "examples": len(rows),
                      "outputs": {k: str(v) for k, v in paths.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
