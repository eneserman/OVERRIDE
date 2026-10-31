#!/usr/bin/env python3
"""Export the demo as a static site (the online version on Vercel).

  python app/export_static.py --url http://localhost:8000 --out web

The model (6 checkpoints x 735 MB) cannot run on a static host, so this asks a running demo server for the real
ensemble output on every input the site offers with one click: the 8 examples and every dataset record, each with
history off and on. Answers are stored in 256 shard files keyed by a hash of the request; the page looks a request up
there and, for any other sentence, says it needs the local server. Nothing is edited: every stored answer is the
server's response as returned.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

STATIC = Path(__file__).resolve().parent / "static"


def get(url: str):
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read())


class Poster:
    """One keep-alive connection for thousands of requests (a new socket per request exhausts Windows' port pool)."""

    def __init__(self, url: str):
        u = urllib.parse.urlsplit(url)
        self.host, self.port = u.hostname, u.port or 80
        self.conn = http.client.HTTPConnection(self.host, self.port, timeout=120)

    def __call__(self, path: str, body: dict):
        for attempt in range(3):
            try:
                self.conn.request("POST", path, json.dumps(body), {"Content-Type": "application/json"})
                r = self.conn.getresponse()
                data = r.read()
                if r.status != 200:
                    raise RuntimeError(f"{path}: HTTP {r.status} {data[:200]!r}")
                return json.loads(data)
            except (http.client.HTTPException, OSError):
                if attempt == 2:
                    raise
                self.conn.close()
                time.sleep(2)
                self.conn = http.client.HTTPConnection(self.host, self.port, timeout=120)


def cache_key(utterance: str, history: list[list[str]], use_history: bool) -> str:
    """Same string the page builds: history only matters when it is used, and the server reads the last 8 turns."""
    hist = [[s.upper(), u.strip()] for s, u in history if u.strip()][-8:] if use_history else []
    return json.dumps([1 if use_history else 0, utterance.strip(), hist], ensure_ascii=False, separators=(",", ":"))


def examples() -> list[tuple[list[list[str]], str]]:
    """The EXAMPLES list from the page: history pairs and the user turn."""
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    block = html[html.index("const EXAMPLES"):]
    block = block[:block.index("];") + 2]
    out = []
    for m in re.finditer(r'hist:\s*(\[\[.*?\]\])\s*,\s*utt:\s*("(?:[^"\\]|\\.)*")', block, re.S):
        out.append((json.loads(m.group(1)), json.loads(m.group(2))))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--out", default="web")
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    (out / "api" / "a").mkdir(parents=True)
    (out / "static").mkdir()

    info = get(f"{args.url}/api/info")
    info["device"] = "static"
    data = get(f"{args.url}/api/data")
    (out / "api" / "info.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    (out / "api" / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    inputs = examples()
    if len(inputs) != 8:
        raise SystemExit(f"expected 8 examples in index.html, found {len(inputs)}")
    inputs += [(r["history"], r["utt"]) for r in data["records"]]
    shards: dict[str, dict] = {}
    done = set()
    post = Poster(args.url)
    for n, (hist, utt) in enumerate(inputs):
        for use in (False, True):
            key = cache_key(utt, hist, use)
            if key in done:
                continue
            done.add(key)
            res = post("/api/analyze", {"utterance": utt, "use_history": use,
                                                   "history": [{"speaker": s, "utterance": u} for s, u in hist]})
            h = hashlib.sha256(key.encode()).hexdigest()
            shards.setdefault(h[:2], {})[h] = res
        if n % 200 == 0:
            print(f"{n} / {len(inputs)}", flush=True)
    for name, entries in shards.items():
        (out / "api" / "a" / f"{name}.json").write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    page = (STATIC / "index.html").read_text(encoding="utf-8")
    page = page.replace("<head>", "<head>\n<script>window.OVERRIDE_STATIC = true;</script>", 1)
    (out / "index.html").write_text(page, encoding="utf-8")
    for f in STATIC.iterdir():
        if f.name != "index.html":
            shutil.copy(f, out / "static" / f.name)
    print(f"{len(done)} answers in {len(shards)} shards -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
