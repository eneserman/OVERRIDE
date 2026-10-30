#!/usr/bin/env python3
"""Interactive demo: label one user turn (optionally with earlier turns) with a frozen D5-v2 ensemble.

  python scripts/demo.py --text "Actually, make it 7 pm at the same place." \
      --checkpoints "reports/train_runs/d5v2_final/no/*.pt"
  python scripts/demo.py --text "Actually, make it 7 pm at the same place." \
      --history "USER: Book a table for Friday at 6." --history "SYSTEM: Booked: Friday, 6 pm, Dolce." \
      --checkpoints "reports/train_runs/d5v2_final/tail60/*.pt"
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
import tempfile
from pathlib import Path

COLORS = {"UPDATE_CUE": "41", "CANCEL_CUE": "41", "KEEP_CUE": "45", "RESTORE_CUE": "45",
          "NEW_VALUE": "43", "OLD_VALUE": "47", "KEPT_VALUE": "46", "REFERENCE": "46"}


def render(utt: str, spans: list[dict]) -> str:
    out, pos = [], 0
    for s in sorted(spans, key=lambda s: s["start"]):
        out.append(utt[pos:s["start"]])
        out.append(f"\033[30;{COLORS.get(s['label'], '47')}m{utt[s['start']:s['end']]}\033[0m")
        pos = s["end"]
    out.append(utt[pos:])
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="the current user turn")
    ap.add_argument("--checkpoints", nargs="+", required=True, help="final_seed*.pt files (globs allowed)")
    ap.add_argument("--history", action="append", default=[], help='earlier turn, e.g. "SYSTEM: Booked for 6 pm."')
    args = ap.parse_args()
    ckpts = sorted({p for pattern in args.checkpoints for p in glob.glob(pattern)})
    if not ckpts:
        raise SystemExit("no checkpoint matched")

    history = []
    for i, h in enumerate(args.history):
        speaker, _, text = h.partition(":")
        history.append({"speaker": speaker.strip().upper(), "turn_index": i, "utterance": text.strip()})
    row = {"id": "demo", "current_user_utterance": args.text, "history": history}

    with tempfile.TemporaryDirectory() as td:
        inp, out = Path(td) / "in.jsonl", Path(td) / "out.jsonl"
        inp.write_text(json.dumps(row) + "\n", encoding="utf-8")
        run = subprocess.run([sys.executable, str(Path(__file__).with_name("d5v2_final.py")), "predict",
                              "--checkpoints", *ckpts, "--input", str(inp), "--out", str(out)],
                             capture_output=True, text=True)
        if run.returncode:
            raise SystemExit(run.stderr)
        pred = json.loads(out.read_text(encoding="utf-8"))

    spans = pred["value_spans"] + pred["cue_spans"]
    print(render(args.text, spans))
    for s in sorted(spans, key=lambda s: s["start"]):
        print(f"  {s['label']:<12} {s['text']!r}  [{s['start']}, {s['end']})")
    if not spans:
        print("  (no revision spans)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
