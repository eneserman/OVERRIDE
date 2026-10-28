#!/usr/bin/env python3
"""Compare two independently filled HUMAN reviewer files (not a gold scorer)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from validate_annotations import read_jsonl,validate_rows


def span_label_metrics(da: dict, db: dict) -> dict:
    """Per-layer, per-label exact-span agreement between the two reviewers."""
    out = {}
    rows = list(da.values()) + list(db.values())
    for layer in ('value_spans', 'cue_spans'):
        labels = sorted({x['label'] for r in rows for x in r[layer]})
        per_label = {}
        for lab in labels:
            matched = only_a = only_b = 0
            for rid in da:
                sa = {(x['start'], x['end']) for x in da[rid][layer] if x['label'] == lab}
                sb = {(x['start'], x['end']) for x in db[rid][layer] if x['label'] == lab}
                matched += len(sa & sb)
                only_a += len(sa - sb)
                only_b += len(sb - sa)
            denom = 2 * matched + only_a + only_b
            per_label[lab] = {
                'matched_exact_spans': matched,
                'only_in_A': only_a,
                'only_in_B': only_b,
                'agreement_f1_symmetric': round(2 * matched / denom, 6) if denom else None,
            }
        out[layer] = per_label
    return out


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
            'span_level_agreement_by_label':span_label_metrics(da,db),
            'difficulty_agreement':round(sum(1 for rid in da if da[rid].get('difficulty')==db[rid].get('difficulty'))/len(da),6) if da else None,
            'uncertainty_flagged':{
                'reviewer_A':sorted(rid for rid in da if (da[rid].get('annotation',{}).get('uncertainty_notes') or '').strip()),
                'reviewer_B':sorted(rid for rid in db if (db[rid].get('annotation',{}).get('uncertainty_notes') or '').strip())},
            'disagreements':disagreements,
            'interpretation':'Exact layer-set equality per example plus exact-span agreement per label; not Cohen kappa, not gold correctness, not model F1.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--a',required=True,type=Path);p.add_argument('--b',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--exclude-ids',type=Path,help='JSON with {"ids":[...]} (e.g. calibration_index.json). Primary agreement is computed WITHOUT these practice items; both variants are reported.')
    args=p.parse_args()
    rows_a=read_jsonl(args.a);rows_b=read_jsonl(args.b)
    excl=set()
    if args.exclude_ids:
        data=json.loads(args.exclude_ids.read_text(encoding='utf-8'))
        excl={str(x) for x in data.get('ids',[])} if isinstance(data,dict) else {str(x) for x in data}
    if excl:
        primary=compare([r for r in rows_a if r['id'] not in excl],[r for r in rows_b if r['id'] not in excl])
        full=compare(rows_a,rows_b)
        report={'status':'HUMAN_AGREEMENT_ONLY_NOT_GOLD',
                'agreement_excluding_practice_items':primary,
                'agreement_including_practice_items':full,
                'excluded_ids':sorted(excl),
                'interpretation':'PRIMARY score = agreement_excluding_practice_items (calibration items discussed together are not independent). Both variants disclosed; not Cohen kappa, not gold correctness, not model F1.'}
    else:
        report=compare(rows_a,rows_b)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    slim={k:v for k,v in report.items() if k not in ('disagreements','agreement_including_practice_items')}
    if 'agreement_excluding_practice_items' in slim:
        slim['agreement_excluding_practice_items']={k:v for k,v in slim['agreement_excluding_practice_items'].items() if k!='disagreements'}
    print(json.dumps(slim,indent=2))

if __name__=='__main__':main()
