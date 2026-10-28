# Build Verification — OVERRIDE Handoff v0.5

**As of:** 2026-10-27. Built in project workspace for coding-agent handoff.

- Previous v0.4 project files preserved/updated in place.
- **Automated unit/synthetic integration tests:** 22 PASS (locally executed with `python -m unittest discover -s tests -v`).
- **Python compilation:** PASS (`python -m compileall -q scripts tests`).
- **Synthetic annotation schema example:** accepted in non-gold validation; correctly rejected when requiring human-adjudicated gold.
- **Full official SGD audit:** NOT EXECUTED; no real source files have been included.
- **Independent human gold annotations:** NOT CREATED; **real NLP model training:** NOT EXECUTED; **measured span F1:** NOT AVAILABLE.
- **Public GitHub/PPTX:** NOT CREATED/PUBLISHED.
- **Code license:** template only; team approval required before release.
- **No website or mobile app** is part of the assessed implementation plan.

**Next action:** agent reads `START_HERE_FOR_AGENT.md`, then `AGENT_MASTER_PROMPT.md`, executes D0 only and returns real source audit evidence. This package does not authorize bypassing human annotation gates.

## v0.6 validated in local environment
- Static compile of scripts/tests passed.
- `python -m unittest discover -s tests -q`: **35 synthetic fixture tests PASSED**.
- `python scripts/preflight_handoff.py --report reports/V06_HANDOFF_PREFLIGHT.json`: `HANDOFF_PRECHECK_PASS`; no actual SGD corpus, human gold or model code present.
- `scripts/evaluate_frozen_test.py` added for full gold hash and held-out ID integrity.
- Test count is an engineering signal, NOT human corpus quality, ML performance, instructor grade, or a complete release.
