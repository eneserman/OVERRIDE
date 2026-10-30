# Data license and attribution

**Code** in this repository is MIT-licensed (`LICENSE`). **Data** is not covered by the code license; it is released
under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**, the license of its source.

## Source

- **Dataset:** Google Schema-Guided Dialogue (SGD), DSTC8 — https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
- **License:** CC BY-SA 4.0
- **Pinned commit:** `e852981ae34990f4358979625854259302feaa78`
- **Citation:** Rastogi, A., Zang, X., Sunkara, S., Gupta, R., Khaitan, P. (2020). *Towards Scalable Multi-domain
  Conversational Agents: The Schema-Guided Dialogue Dataset.* AAAI 2020. arXiv:1909.05855.

## What is redistributed

| Location | Content | Terms |
|---|---|---|
| `data/raw/sgd_turns_unlabeled.jsonl` | 1,220 verbatim SGD user turns with their earlier turns | CC BY-SA 4.0 (excerpts of SGD) |
| `data/gold/*.jsonl` | the same turns plus our span annotations | CC BY-SA 4.0 (adapted material) |
| `reports/d6_test/predictions/*.jsonl` | model predictions quoting SGD text | CC BY-SA 4.0 |
| `reports/`, `docs/` | counts, metrics, hashes, short quoted examples | CC BY-SA 4.0 where SGD text is quoted |

The full SGD corpus is not redistributed; `data/raw/README.md` explains how to fetch the pinned version.

## Modifications

The OVERRIDE team (2026) selected user turns from SGD and added new labels that SGD does not provide: VALUE spans
(NEW_VALUE, OLD_VALUE, KEPT_VALUE, REFERENCE) and CUE spans (UPDATE_CUE, CANCEL_CUE, KEEP_CUE, RESTORE_CUE), with
annotation provenance. Utterance text and history are unchanged (checked by `scripts/export_raw_turns.py`).
Reusers must give attribution to SGD and to this project, indicate their own changes, and share adaptations under
CC BY-SA 4.0.
