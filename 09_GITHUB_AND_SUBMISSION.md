# 09 — GitHub, Attribution and Submission

## Deliverables from instructor materials
P2 submission text explicitly asks for **GitHub URL first, PPTX presentation second**. P2 announcements require token-classification work, dataset/task claimed in P2 sheet and technical depth. An older **P1** instruction gives public repo, clean code, preprocessing, training scripts, raw/clean data, README, LICENSE and contributor files, along with a timing/rubric scale: treat this as **quality precedent, not confirmed P2 percentages**. The user additionally reports strict same-project collision penalty. Record the latest P2 list before locking dataset/task.

## Required repository tree (proposed, not all modules implemented)
```
OVERRIDE-PROJECT/
  README.md  LICENSE  DATA_LICENSE_AND_ATTRIBUTION.md  requirements-core.txt
  00_DESIGN_AUDIT.md ... 16_ARTIFACT_STATUS.md
  scripts/{audit_sgd,prepare_annotation_pilot,validate_annotations,freeze_gold_splits,evaluate_spans}.py
  tests/*.py
  configs/experiment.example.json
  examples/UNREVIEWED_annotation_example.jsonl
  contributions/STUDENT_NAME_STUDENT_ID_GITHUB_USERNAME.md (real files, one per member)
  data/upstream/   # downloaded source by script; normally excluded until redistribution decision
  data/annotations/ # blind queues and private hints excluded from public repo
  reports/ # only reviewed, non-sensitive published reports
  AGENT_MASTER_PROMPT.md and phase prompts
```
Never publish a teammate's personal ID or GitHub user without their permission; instructor requires student identification in contribution filenames, so prepare those only with actual member-supplied details.

## Repository hygiene
Add only needed packages. No node_modules, local venv, weights, private sampling manifests, unlicensed duplicates, private annotations, credentials, transient checkpoints. Pin data source version and environment. Before commit, run `git status --short`, tests, and inspect `git diff --check`. Code owner reviews artifacts before making repo public.

## Raw/clean data versus license
SGD source repo uses CC BY-SA 4.0. If sharing adapted text or labels, retain attribution/changes and apply share-alike obligations as appropriate; code should carry a distinct license. Verify what files may be redistributed and whether instructor expects raw data in repo; if data-sharing restrictions remain, document secure retrieval script and get instructor approval rather than misrepresenting submission.

## Actual team contributions
Each teammate authors `contributions/FIRST_LAST_STUDENTID_GITHUBUSER.md` describing exact tasks, commits/PR IDs, tests and evidence. Git diffs are checked by instructor; never invent contributions. `contributions/CONTRIBUTION_TEMPLATE.md` is a blank aid, not a substitute.

## PPTX preflight
- Start submission text with GitHub URL, then attach PPTX.
- Report measured class support, split IDs/hashes, real model metrics with reproducible commands.
- Briefly distinguish source SGD labels from new human-reviewed labels.
- Present methodological trade-offs and limitations, not overclaim long-term memory.
- Use the older P1 under-2-min pacing rule for rehearsal only if P2 timing not separately specified.

## v0.6 publication safeguard

Before final publication, verify code `LICENSE` is actually present and approved by contributors; a template in `legal_templates/` is not a license. Check raw/clean SGD derivative license compliance, public repo visibility, contribution filenames **with genuine Git diff evidence**, real training/eval run instructions and actual PPTX. Do not mark the handoff ZIP as the finished submission.
