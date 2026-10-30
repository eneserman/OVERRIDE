#!/usr/bin/env python3
"""D6 inference with a FROZEN D5 checkpoint. No training, no fine-tuning.

Preprocessing (TwoHead/build_example/collate/decode_word_tags) is imported
verbatim from scripts/d5_train_transformer.py so test-time alignment is
byte-identical to the dev-time pipeline that produced the frozen metrics.

Usage:
  python scripts/d6_infer_frozen.py --checkpoint reports/train_runs/d5_tf/checkpoint_tf_hno.pt \
      --input data/gold/test_reference_v1.jsonl --out reports/train_runs/d6/pred_test_hno.jsonl

Determinism: model.eval() + argmax; no dropout, no sampling, no shuffling.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_annotations import read_jsonl  # noqa: E402
from span_tokenizer import tokenize  # noqa: E402
from d5_train_transformer import TwoHead, build_example, collate, decode_word_tags  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True,
                    help="test reference rows (current_user_utterance + history required)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    if args.out.exists():
        raise SystemExit(f"ABORT: refusing to overwrite: {args.out}")

    ckpt = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    history = ckpt["history"] == "with"
    max_len, hist_words = ckpt["max_length"], ckpt["hist_words"]
    v_tagset, c_tagset = ckpt["v_tagset"], ckpt["c_tagset"]

    rows = read_jsonl(args.input)
    tok = AutoTokenizer.from_pretrained(ckpt["model_name"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    examples = []
    misses = 0
    for row in rows:
        r = dict(row)
        # same {start, end, text} dicts that d5_prepare_data.py wrote for training
        r["_words"] = [t._asdict() for t in tokenize(row["current_user_utterance"])]
        r["_value_tags"] = ["O"] * len(r["_words"])  # inference: labels unused
        r["_cue_tags"] = ["O"] * len(r["_words"])
        enc, _, _, pos, miss = build_example(r, tok, history, max_len, hist_words)
        misses += miss
        dummy = [0] * len(enc["input_ids"])  # inference: labels unused by loss/argmax
        examples.append((enc, dummy, dummy, pos, row))
    if misses:
        raise SystemExit(f"alignment misses on test input: {misses} (must be 0)")

    model = TwoHead(ckpt["model_name"], len(v_tagset), len(c_tagset))
    model.load_state_dict(ckpt["state_dict"])
    model.to(device).eval()

    preds = {}
    with torch.no_grad():
        for k in range(0, len(examples), args.batch):
            chunk = examples[k:k + args.batch]
            ids, attn, tt, _, _ = collate(chunk, tok.pad_token_id or 0)
            ids, attn, tt = ids.to(device), attn.to(device), tt.to(device)
            v_logits, c_logits = model(ids, attn, tt)
            v_pred = v_logits.argmax(-1).cpu().tolist()
            c_pred = c_logits.argmax(-1).cpu().tolist()
            for bi, (_, _, _, pos, row) in enumerate(chunk):
                utt = row["current_user_utterance"]
                out = {"id": row["id"], "value_spans": [], "cue_spans": []}
                vt = [v_tagset[v_pred[bi][pos[w]]] if pos[w] is not None else "O"
                      for w in range(len(pos))]
                ct = [c_tagset[c_pred[bi][pos[w]]] if pos[w] is not None else "O"
                      for w in range(len(pos))]
                for span in decode_word_tags(row["_words"], vt):
                    span["text"] = utt[span["start"]:span["end"]]
                    out["value_spans"].append(span)
                for span in decode_word_tags(row["_words"], ct):
                    span["text"] = utt[span["start"]:span["end"]]
                    out["cue_spans"].append(span)
                preds[row["id"]] = out

    if len(preds) != len(rows) or len({r["id"] for r in rows}) != len(rows):
        raise SystemExit("prediction ID coverage failure")

    ordered = [preds[r["id"]] for r in rows]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in ordered),
                        encoding="utf-8")
    out_sha = hashlib.sha256(args.out.read_bytes()).hexdigest()
    print(json.dumps({
        "status": "D6_INFERENCE_DONE",
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
        "history": ckpt["history"],
        "best_epoch_at_train": ckpt["best_epoch"],
        "examples": len(ordered),
        "predictions_sha256": out_sha,
        "out": str(args.out),
        "device": str(device),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
