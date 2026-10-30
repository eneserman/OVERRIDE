# Raw data

## Upstream source (not redistributed in full)

Google Schema-Guided Dialogue (SGD, DSTC8), CC BY-SA 4.0, pinned commit `e852981ae34990f4358979625854259302feaa78`.

```bash
git clone https://github.com/google-research-datasets/dstc8-schema-guided-dialogue.git data/upstream/sgd
git -C data/upstream/sgd checkout e852981ae34990f4358979625854259302feaa78
python scripts/inspect_upstream_provenance.py --sgd-root data/upstream/sgd --out reports/V08_UPSTREAM_PROVENANCE.json
python scripts/audit_sgd.py --sgd-root data/upstream/sgd --split train --out reports/sgd_train_audit
```

## `sgd_turns_unlabeled.jsonl` — the 1,220 selected turns, before labeling

One row per user turn that was annotated: `id`, `source` (SGD split, dialogue id, turn index, service, source file and its
SHA-256), `dialogue_family_id`, `history` (earlier USER/SYSTEM turns only, never future turns) and
`current_user_utterance`. **No labels.** 857 rows come from official SGD `train` (model development), 363 from official
`dev`/`test` (the locked prospective test).

Produced by `scripts/export_raw_turns.py`, which compares every utterance and every history turn with the pinned SGD
files and aborts on any difference (1,220 / 1,220 verified).

```bash
python scripts/export_raw_turns.py --gold data/gold/train_dev_gold_v1_3.jsonl data/gold/test_reference_v1.jsonl \
  --out data/raw/sgd_turns_unlabeled.jsonl --sgd-root data/upstream/sgd
```

How the turns were selected from SGD (mining buckets, blind packets, holdout lock) is described in
`docs/DATA_PIPELINE.md`.
