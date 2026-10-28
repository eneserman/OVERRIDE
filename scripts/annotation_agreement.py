#!/usr/bin/env python3
"""Compare two independently filled HUMAN reviewer files (not a gold scorer)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from validate_annotations import read_jsonl,validate_rows


def compare(a:list[dict],b:list[dict]) -> dict:
    for name,rows in [('A',a),('B',b)]:
        if validate_rows(rows,False)['status']!='PASS':
            raise ValueError(f'Reviewer {name} contains invalid annotations')
        if any(r.get('annotation',{}).get('status')!='ANNOTATED' for r in rows):
            raise ValueError('reviewer input must be explicitly ANNOTATED')
    if len({r['id'] for r in a})!=len(a) or len({r['id'] for r in b})!=len(b):
        raise ValueError('Duplicate reviewer IDs')
    da={r['id']:r for r in a};db={r['id']:r for r in b}
    if set(da)!=set(db):raise ValueError('Independent reviewers did not annotate identical example IDs')
    disagreements=[];total_match=0;total=0
    for rid in sorted(da):
        for field in ('source','history','current_user_utterance','dialogue_family_id'):
            if da[rid].get(field) != db[rid].get(field):
                raise ValueError(f'Annotation packets not comparable for {rid}: {field} differs')
        if da[rid].get('annotation',{}).get('reviewer_id') == db[rid].get('annotation',{}).get('reviewer_id'):
            raise ValueError(f'Both packets claim the same reviewer_id for {rid}; independent review not established')
        for layer in ('value_spans','cue_spans'):
            sa={(x['start'],x['end'],x['label']) for x in da[rid][layer]}
            sb={(x['start'],x['end'],x['label']) for x in db[rid][layer]}
            if sa==sb:total_match+=1
            else:disagreements.append({'id':rid,'layer':layer,'reviewer_A':sorted(sa),'reviewer_B':sorted(sb)})
            total+=1
    return {'status':'HUMAN_AGREEMENT_ONLY_NOT_GOLD','examples':len(da),'layer_judgements':total,
            'exact_layer_set_agreement':round(total_match/total,6) if total else None,
            'disagreements':disagreements,
            'interpretation':'Exact layer-set equality per example; not Cohen kappa, not gold correctness, not model F1.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--a',required=True,type=Path);p.add_argument('--b',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    args=p.parse_args()
    report=compare(read_jsonl(args.a),read_jsonl(args.b))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='disagreements'},indent=2))

if __name__=='__main__':main()
