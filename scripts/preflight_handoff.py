#!/usr/bin/env python3
"""Reproducible documentation+code handoff preflight (NOT a science quality cert)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=[
    'README.md','AGENT_MASTER_PROMPT.md','START_HERE_FOR_AGENT.md',
    '01_REQUIREMENTS.md','02_NLP_TASK_DESIGN.md','03_DATASET_PIPELINE.md',
    '04_HUMAN_ANNOTATION_PILOT.md','05_SYSTEM_ARCHITECTURE.md',
    '06_MODEL_EXPERIMENTS.md','07_EVALUATION_METRICS.md','08_TESTING_AND_QA.md',
    '09_GITHUB_AND_SUBMISSION.md','13_ANNOTATION_GUIDELINES.md',
    '14_DATA_CONTRACTS.md','15_DATA_LICENSE_AND_ATTRIBUTION.md',
    'scripts/audit_sgd.py','scripts/prepare_annotation_pilot.py',
    'scripts/normalize_review_packet.py','scripts/annotation_agreement.py',
    'scripts/validate_annotations.py','scripts/freeze_gold_splits.py',
    'scripts/evaluate_spans.py','scripts/evaluate_frozen_test.py',
    'AGENT_D0_DATA_AUDIT_PROMPT.md', 'AGENT_D7_RELEASE_PROMPT.md'
]


def run_preflight() -> dict:
    absent=[f for f in REQUIRED if not (ROOT/f).is_file()]
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-q'],
                          cwd=ROOT,capture_output=True,text=True)
    compile_check=subprocess.run([sys.executable,'-m','compileall','-q',str(ROOT/'scripts'),str(ROOT/'tests')],
                                 cwd=ROOT,capture_output=True,text=True)
    test_messages=(result.stdout+'\n'+result.stderr).strip()
    return {
      'status':'HANDOFF_PRECHECK_PASS' if not absent and result.returncode==0 and compile_check.returncode==0 else 'HANDOFF_PRECHECK_FAIL',
      'missing_required_files':absent,
      'unit_test_exit_code':result.returncode,
      'unit_test_output':test_messages[-1800:],
      'syntax_exit_code':compile_check.returncode,
      'real_sgd_data_present':bool(list((ROOT/'data'/'upstream'/'sgd'/'train').glob('dialogues_*.json'))),
      'human_adjudicated_gold_present':bool(list((ROOT/'data'/'gold').glob('*.jsonl'))),
      'model_implementation_present':any((ROOT/'src'/'override').rglob('*.py')),
      'academic_ready':'NOT_VERIFIED_NEEDS_REAL_DATA_HUMANS_TRAINED_MODELS_COLLISION_CHECK',
      'warning':'Successful unit tests are synthetic safety checks; not an official SGD audit or trained model result.'
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',type=Path)
    args=ap.parse_args()
    result=run_preflight()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if result['status']!='HANDOFF_PRECHECK_PASS':
        raise SystemExit(1)

if __name__=='__main__':main()
