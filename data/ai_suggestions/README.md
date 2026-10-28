# AI suggestions only

The two JSONL files are two different labeling policies produced by a *single* model family; they are not independent humans and not trusted gold. The review triage highlights AI disagreement examples for later human review; it does not validate AI consensus. Keep their `AI_DRAFT`, `AI_SIMULATION`, and provenance fields intact. Both files cover the same 100 records.

**Source attribution:** the quoted dialogue excerpts are from Google Schema-Guided Dialogue (SGD, DSTC8), https://github.com/google-research-datasets/dstc8-schema-guided-dialogue, licensed **CC BY-SA 4.0**, pinned commit `e852981ae34990f4358979625854259302feaa78`. The excerpted text is redistributed as a CC BY-SA 4.0 derivative; the AI suggestion layer is project output. Modifications (AI draft spans, provenance fields) are indicated in each record. See root `DATA_LICENSE_AND_ATTRIBUTION.md`.
