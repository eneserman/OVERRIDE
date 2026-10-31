#!/usr/bin/env python3
"""OVERRIDE live demo: a small web app around the frozen D5-v2 ensembles.

  python app/server.py --checkpoints-no "reports/train_runs/d5v2_final/no/*.pt" \
      --checkpoints-history "reports/train_runs/d5v2_final/tail60/*.pt"     # then open http://localhost:8000

POST /api/analyze {"utterance": str, "history": [{"speaker", "utterance"}], "use_history": bool} returns every step the
page shows: the words, the encoder's sub-word pieces, the averaged per-word tag probabilities of both layers, and the
decoded spans. Prediction is the same code path as `scripts/d5v2_final.py predict` (softmax averaged over seeds).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from pathlib import Path

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import AutoTokenizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from d5_train_transformer import TwoHead  # noqa: E402
from d5v2_cv import collate, spans_from  # noqa: E402
from d5v2_final import prepare  # noqa: E402

STATIC = Path(__file__).with_name("static")
REPORTS = Path(__file__).resolve().parents[1] / "reports" / "d6_test"
MAX_CHARS = 300


class Turn(BaseModel):
    speaker: str
    utterance: str


class Request(BaseModel):
    utterance: str
    history: list[Turn] = []
    use_history: bool = False


class Ensemble:
    """The seeds of one frozen configuration, loaded once."""

    def __init__(self, paths: list[str], device: torch.device):
        ckpts = [torch.load(p, map_location="cpu", weights_only=False) for p in paths]
        self.meta = ckpts[0]["meta"]
        if any(c["meta"]["history"] != self.meta["history"] for c in ckpts):
            raise SystemExit("checkpoints disagree on the history setting")
        self.tok = AutoTokenizer.from_pretrained(self.meta["model"])
        self.device, self.models = device, []
        for c in ckpts:
            m = TwoHead(self.meta["model"], len(self.meta["v_tags"]), len(self.meta["c_tags"])).float()
            m.load_state_dict(c["state_dict"])
            self.models.append(m.to(device).eval())

    @torch.no_grad()
    def analyze(self, utterance: str, history: list[dict]) -> dict:
        row = {"id": "demo", "current_user_utterance": utterance, "history": history}
        (r,), _ = prepare([row], self.tok, self.meta["history"], self.meta["max_len"], labeled=False)
        batch = collate([(r["_enc"], r["_pos"], [0] * len(r["_pos"]), [0] * len(r["_pos"]))],
                        self.tok.pad_token_id or 0, self.device)
        v_seed, c_seed = [], []
        for m in self.models:
            v_log, c_log = m(batch[0], batch[1], batch[2])
            v_seed.append(v_log.softmax(-1)[0].cpu())
            c_seed.append(c_log.softmax(-1)[0].cpu())
        v_avg, c_avg = sum(v_seed) / len(self.models), sum(c_seed) / len(self.models)
        v_tags, c_tags = self.meta["v_tags"], self.meta["c_tags"]
        enc, seq, off = r["_enc"], r["_enc"].sequence_ids(), r["_enc"]["offset_mapping"]
        utt_seq = 1 if (self.meta["history"] != "no" and 1 in seq) else 0
        utt_tok = [i for i, s in enumerate(seq) if s == utt_seq]
        pieces = [self.tok.convert_ids_to_tokens(enc["input_ids"][i]) for i in utt_tok]
        words = []
        for w, p in zip(r["_words"], r["_pos"]):
            vi, ci = (int(v_avg[p].argmax()), int(c_avg[p].argmax())) if p is not None else (0, 0)
            own = [self.tok.convert_ids_to_tokens(enc["input_ids"][i]) for i in utt_tok
                   if off[i][1] > off[i][0] and off[i][0] < w["end"] and off[i][1] > w["start"]]
            # the role shown for a word: its cue tag if it has one, else its value tag; per-seed probability of that tag
            seeds = (c_seed, ci) if ci else (v_seed, vi)
            words.append({"text": w["text"], "start": w["start"], "end": w["end"], "pieces": own,
                          "value_tag": v_tags[vi], "value_p": round(float(v_avg[p][vi]), 3) if p is not None else None,
                          "cue_tag": c_tags[ci], "cue_p": round(float(c_avg[p][ci]), 3) if p is not None else None,
                          "seed_p": [round(float(s[p][seeds[1]]), 3) for s in seeds[0]] if p is not None else None})
        spans = spans_from(r, r["_pos"], v_avg.argmax(-1).tolist(), c_avg.argmax(-1).tolist(), v_tags, c_tags)
        spans = spans["value_spans"] + spans["cue_spans"]
        for s in spans:  # mean probability of the predicted tag over the span's words
            key = "cue" if s["label"].endswith("_CUE") else "value"
            inside = [w for w in words if s["start"] <= w["start"] and w["end"] <= s["end"] and w[f"{key}_p"]]
            ps = [w[f"{key}_p"] for w in inside]
            s["words"], s["p"] = len(ps), round(sum(ps) / len(ps), 3) if ps else None
            s["pieces"] = [x for w in inside for x in w["pieces"]]
            s["seed_p"] = [round(sum(w["seed_p"][k] for w in inside) / len(inside), 3)
                           for k in range(len(self.models))] if inside else []
        return {"words": words, "pieces": pieces, "spans": spans,
                "model": self.meta["model"], "history_mode": self.meta["history"], "seeds": len(self.models)}


def test_scores() -> list[dict]:
    """Locked-test S per system, read from the released metric files (reports/d6_test/)."""
    names = [("laya_choice_en", "Laya zero-shot (JEV alternative)"), ("b2_rules", "Surface rules"),
             ("b1_lexicon_copy", "Lexicon copy"), ("bert_v1_1_hno", "BERT-base, first data"), ("crf_hno", "CRF"),
             ("deberta_v2_ens_hno", "DeBERTa-v3, selected"), ("deberta_v2_ens_htail60", "DeBERTa-v3 + history")]
    out = []
    for key, label in names:
        path = REPORTS / f"metrics_{key}.json"
        if path.exists():
            layers = json.loads(path.read_text(encoding="utf-8"))["layers"]
            v, c = layers["value_spans"]["micro"]["f1"] or 0.0, layers["cue_spans"]["micro"]["f1"] or 0.0
            out.append({"system": label, "value": round(v, 3), "cue": round(c, 3), "S": round((v + c) / 2, 3)})
    return out


def build_app(no_paths: list[str], hist_paths: list[str]) -> FastAPI:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ensembles = {False: Ensemble(no_paths, device)}
    if hist_paths:
        ensembles[True] = Ensemble(hist_paths, device)
    app = FastAPI(title="OVERRIDE demo")

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/info")
    def info():
        return {"device": "GPU" if device.type == "cuda" else "CPU", "history_available": True in ensembles,
                "model": ensembles[False].meta["model"], "seeds": len(ensembles[False].models),
                "train_records": ensembles[False].meta["records"], "test": test_scores()}

    @app.get("/static/{name}")
    def static(name: str):
        path = STATIC / name
        if path.parent != STATIC or not path.is_file():
            raise HTTPException(404)
        return FileResponse(path)

    @app.post("/api/analyze")
    def analyze(req: Request):
        utt = req.utterance.strip()
        if not utt or len(utt) > MAX_CHARS:
            raise HTTPException(400, f"Enter a user turn of 1 to {MAX_CHARS} characters")
        ens = ensembles.get(req.use_history and True in ensembles, ensembles[False])
        t0 = time.perf_counter()
        out = ens.analyze(utt, [{"speaker": t.speaker.upper(), "utterance": t.utterance} for t in req.history[-8:]])
        out["ms"] = round((time.perf_counter() - t0) * 1000)
        return out

    return app


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoints-no", default=os.environ.get("OVERRIDE_CKPT_NO", ""),
                    help="glob of the history = no seeds (the selected model)")
    ap.add_argument("--checkpoints-history", default=os.environ.get("OVERRIDE_CKPT_HISTORY", ""),
                    help="glob of the history = tail60 seeds (optional)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8000)))
    args = ap.parse_args()
    no_paths, hist_paths = sorted(glob.glob(args.checkpoints_no)), sorted(glob.glob(args.checkpoints_history))
    if not no_paths:
        raise SystemExit("no checkpoint matched --checkpoints-no")
    uvicorn.run(build_app(no_paths, hist_paths), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
