---
title: OVERRIDE demo
emoji: ✍️
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
short_description: Detecting revisions in dialogue, token classification
---

# OVERRIDE: live model

The frozen OVERRIDE ensembles (DeBERTa-v3-base, two BIO token heads, 3 seeds; with and without dialogue history)
behind the demo page. The online page **https://override-demo.vercel.app** sends sentences that are not in its stored
set to this Space.

- Code, data and results: https://github.com/eneserman/OVERRIDE
- Team Developers: Adnan Burak Özbay, Enes Erman, Mohammed Firas, İlayda Şenel

Checkpoints (model repo `enes123erman/override-checkpoints`, fetched at build time) are the frozen seeds stored in
half precision to halve the download; they are loaded back to float32. Runs on the free CPU tier, so the
first request after the Space has been asleep takes about a minute.

## Rebuilding this Space

The Space repository holds this folder plus `app/server.py`, `app/static/`, the seven `scripts/` the server imports`n(`d5_train_transformer`, `d5v2_cv`, `d5v2_final`, `span_tokenizer`, `d5_prepare_data`, `validate_annotations`,`n`evaluate_spans`), the two released gold files, `data/synthetic/synthetic_v2.jsonl` and `reports/d6_test/metrics_*.json`.
