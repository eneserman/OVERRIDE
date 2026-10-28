#!/usr/bin/env python3
"""Fail-closed evaluation against a frozen, content-hashed adjudicated test split.

The model must supply predictions for exactly the test IDs. Developer scripts may
still use evaluate_spans.py on dev, but only this entry point can be used for
claims about a frozen final test in the OVERRIDE report.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from validate_annotations import read_jsonl, validate_rows
from evaluate_spans import evaluate


def canonical_gold_sha256(rows: list[dict]) -> str:
    canonical = json.dumps(sorted(rows, key=lambda r:r['id']),ensure_ascii=False,
                           sort_keys=True,separators=(',',':'))
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def check_manifest(gold: list[dict], manifest: dict) -> list[dict]:
    verdict=validate_rows(gold,require_gold=True)
    if verdict['status']!='PASS':
        raise ValueError('Full gold invalid: '+str(verdict['errors'][:5]))
    if canonical_gold_sha256(gold) != manifest.get('gold_content_sha256'):
        raise ValueError('Frozen gold SHA-256 differs: gold labels/text changed after freezing')
    recorded_digest = manifest.get('manifest_digest')
    unhashed = {k:v for k,v in manifest.items() if k!='manifest_digest'}
    expected_digest = hashlib.sha256(json.dumps(unhashed,sort_keys=True).encode()).hexdigest()
    if recorded_digest != expected_digest:
        raise ValueError('Split manifest digest does not verify')
    splits = manifest.get('splits')
    if not isinstance(splits,dict) or set(splits) != {'train','dev','test'}:
        raise ValueError('Manifest requires exactly train/dev/test splits')
    ids=[i for group in splits.values() for i in group]
    by_id={row['id']:row for row in gold}
    if len(ids)!=len(set(ids)) or set(ids)!=set(by_id):
        raise ValueError('Split IDs do not partition full gold exactly once')
    if not splits['test'] or not splits['train'] or not splits['dev']:
        raise ValueError('Empty frozen split')
    assignment = manifest.get('family_assignment',{})
    if any(assignment.get(row['dialogue_family_id']) != split
           for split, group in splits.items() for rid in group
           for row in [by_id[rid]]):
        raise ValueError('Family leakage/inconsistent split membership')
    return [by_id[rid] for rid in splits['test']]


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--full-gold',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--test-predictions',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    gold=read_jsonl(args.full_gold)
    manifest=json.loads(args.manifest.read_text(encoding='utf-8'))
    heldout=check_manifest(gold,manifest)
    predictions=read_jsonl(args.test_predictions)
    report=evaluate(heldout,predictions)
    report['evaluation_split']='frozen_custom_test'
    report['gold_content_sha256']=manifest['gold_content_sha256']
    report['manifest_digest']=manifest['manifest_digest']
    report['source_split']='original_SGD_train_subset'
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists():
        raise SystemExit(f'Refusing to overwrite frozen evaluation report: {args.out}')
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'FROZEN_TEST_EVALUATED', 'examples':len(heldout),
        'value_f1':report['layers']['value_spans']['micro']['f1'],
        'cue_f1':report['layers']['cue_spans']['micro']['f1']},indent=2))

if __name__=='__main__':main()
