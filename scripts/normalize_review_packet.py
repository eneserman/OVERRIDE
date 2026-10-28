#!/usr/bin/env python3
"""Convert filled HUMAN-reviewed pilot packets to canonical per-reviewer records.

Never produces gold. Requires reviewer to fill both layers explicitly. The input
record has example_id and annotation.value_spans/cue_spans from the D1 sampler.
Output status remains ANNOTATED (not ADJUDICATED).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from validate_annotations import read_jsonl, validate_rows


def normalize(rows: list[dict], reviewer_id: str) -> list[dict]:
    if not reviewer_id:
        raise ValueError('real reviewer identifier required')
    normalized=[]
    for r in rows:
        a=r.get('annotation',{})
        if not isinstance(a,dict) or a.get('status') != 'ANNOTATED':
            raise ValueError(f"{r.get('example_id')}: reviewer annotation.status must be ANNOTATED, not unreviewed")
        if not isinstance(a.get('value_spans'),list) or not isinstance(a.get('cue_spans'),list):
            raise ValueError(f"{r.get('example_id')}: human reviewer must fill both value_spans and cue_spans lists; [] means reviewed negative")
        record={
            'id':r.get('example_id'), 'source':r.get('source'),
            'dialogue_family_id':r.get('dialogue_family_id') or (r.get('source') or {}).get('dialogue_id'),
            'history':r.get('history'), 'current_user_utterance':r.get('current_user_utterance'),
            'value_spans':a['value_spans'], 'cue_spans':a['cue_spans'],
            'transitions':a.get('transitions') or [], 'links':a.get('links') or [],
            'difficulty':a.get('difficulty'),
            'annotation':{'status':'ANNOTATED','guideline_version':a.get('guideline_version'),'reviewer_id':reviewer_id,
                          'uncertainty_notes':a.get('uncertainty_notes')}
        }
        normalized.append(record)
    report=validate_rows(normalized,require_gold=False)
    if report['status']!='PASS':
        raise ValueError('Converted reviewer packets invalid: '+str(report['errors'][:8]))
    return normalized


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--reviewer-id',required=True)
    args=p.parse_args()
    result=normalize(read_jsonl(args.input),args.reviewer_id)
    if args.out.exists():
        raise SystemExit('Refusing to overwrite reviewer normalized record: '+str(args.out))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('w',encoding='utf-8') as f:
        for r in result:f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
    print(f'{len(result)} HUMAN reviewed, NOT ADJUDICATED records validated at {args.out}')

if __name__=='__main__':main()
