# Data License and Attribution

**Applies to data files in this repository.** Project code is MIT (`LICENSE`); the code license does **not** cover data.

## Upstream source

- **Dataset:** Google Schema-Guided Dialogue (SGD), DSTC8
- **Source:** https://github.com/google-research-datasets/dstc8-schema-guided-dialogue
- **License:** Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Pinned commit:** `e852981ae34990f4358979625854259302feaa78` (2023-08-07)
- **Citation:** Rastogi, A.; Zang, X.; Gupta, R.; Sunkara, S.; Khaitan, P. (2019). *Towards Scalable Multi-domain Conversational Agents: The Schema-Guided Dialogue Dataset*. arXiv:1909.05855

## What is redistributed here and under what terms

| Location | Content | License / status |
|---|---|---|
| `data/upstream/` (local only, gitignored) | Full raw SGD clone | Not redistributed; fetch from the official source above |
| `data/sgd_pilot/annotator_*_UNLABELED.jsonl` | 100 blind pilot examples quoting SGD train utterances + short history | **CC BY-SA 4.0 derivative** (verbatim excerpts); attributed here; modifications noted below |
| `data/ai_suggestions/*` | AI-generated span suggestions over the same 100 excerpts (`AI_SIMULATION`, not gold) | Contains verbatim SGD excerpts → **CC BY-SA 4.0 derivative** for the excerpted text; the suggestion layer is project output (MIT), disclosed as AI-draft |
| `data/review/*` | AI triage queue/report over the same 100 excerpts | Same as above: **CC BY-SA 4.0 derivative** excerpts |
| `data/synthetic_bootstrap/*` | Fully machine-generated examples (`SYNTHETIC_COMPOSITION`) | No upstream text; project output (MIT). Not SGD, not gold |
| `reports/` | Aggregate counts, hashes, metrics | Project output (MIT); no raw dialogue text beyond short quoted examples for inspection |

Any file containing SGD excerpts is shared under **CC BY-SA 4.0** as part of an adapted collection; the accompanying annotation/suggestion layers are project output. Reusers must retain attribution, indicate modifications, and apply CC BY-SA 4.0 to the excerpted material. No additional restrictions are imposed.

## Modifications indicated

- Span/label annotations, AI draft suggestions, triage fields and sampling metadata were added by the OVERRIDE project (2026). These are **new intended labels**, not provided by SGD.
- SGD slot states and offsets in the upstream files are unchanged; raw files remain in `data/upstream/` unmodified (SHA-256 manifests in `reports/`).

## Prohibition against misrepresentation

AI draft suggestions (`data/ai_suggestions/`) are **not** human annotations and **not** gold. Synthetic bootstrap files are **not** SGD. Never present either as human-adjudicated gold or as real benchmark results.
