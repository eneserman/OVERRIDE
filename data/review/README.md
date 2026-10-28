# AI review triage (not human review)

`AI_TRIAGE_QUEUE.csv` and `AI_TRIAGE_REPORT.json` rank the 100 blind pilot examples by AI-vs-AI disagreement to help human reviewers start with hard cases. Every row is tagged `AI_SIMULATION_ONLY` / `human_status=NOT_REVIEWED`. **AI agreement is not gold**; all examples still need human annotation.

**Source attribution:** quoted dialogue excerpts are from Google Schema-Guided Dialogue (SGD, DSTC8), https://github.com/google-research-datasets/dstc8-schema-guided-dialogue, licensed **CC BY-SA 4.0**, pinned commit `e852981ae34990f4358979625854259302feaa78`. The excerpted text is redistributed as a CC BY-SA 4.0 derivative; the triage layer is project output. See root `DATA_LICENSE_AND_ATTRIBUTION.md`.
