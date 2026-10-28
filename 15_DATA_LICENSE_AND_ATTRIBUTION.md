# 15 — Dataset License, Attribution and Publication Checklist

**Source:** Google SGD: https://github.com/google-research-datasets/dstc8-schema-guided-dialogue. The repository labels itself **CC BY-SA 4.0**; its licensing text must be included/linked along with attribution, version and modification notices. <https://creativecommons.org/licenses/by-sa/4.0/>.

## Distinguish legal objects
- **Original SGD dialogue text/data:** upstream CC BY-SA 4.0 license and attribution; archive commit pin/hashes.
- **Derived OVERRIDE human annotations containing original text:** may trigger share-alike/attribution; legal redistribution review required before pushing.
- **Independent project code:** separate, clearly identified open-source license selected by contributors (e.g. MIT only when team explicitly agrees); do **not** claim the source data became MIT-licensed.
- **Reports:** avoid leaking personal data, credentials or identifiable reviewer remarks.

## Before public repository
1. Check upstream repo license at pinned commit and licenses of any further sources (not just top-level dataset card).
2. Preserve original authorship, source and license links; describe modifications and date; include CC BY-SA 4.0 license text/URL as appropriate.
3. Determine whether raw and cleaned datasets can be redistributed, using source conditions; if not, include tested retrieval/transform scripts and ask instructor about alternative delivery.
4. Include *actual* repo code LICENSE, which applies to code only, and `DATA_LICENSE_AND_ATTRIBUTION.md` for dataset.
5. Avoid uploading unredacted reviewer notes, API keys, annotation hints or training test leakage files.
6. Record permission/review outcome in a checked-in release report before making the repo public.

No legal assessment is final here; do not claim redistribution rights without review.
