#!/usr/bin/env python3
"""Exact-offset labeled-span evaluator, no inflated token/O accuracy.

Prediction rows: {id, value_spans:[{start,end,label}], cue_spans:[...]}.
Gold rows: adjudicated canonical records (see docs/DATA_FORMAT.md).
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from validate_annotations import CUE_LABELS,VALUE_LABELS,read_jsonl,validate_rows


def fscore(tp:int,fp:int,fn:int):
    if tp+fp+fn==0:
        return {'precision':None,'recall':None,'f1':None,'tp':0,'fp':0,'fn':0}
    p=tp/(tp+fp) if tp+fp else 0.
    r=tp/(tp+fn) if tp+fn else 0.
    f=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    return {'precision':round(p,6),'recall':round(r,6),'f1':round(f,6) if f is not None else None,'tp':tp,'fp':fp,'fn':fn}


def evaluate(gold_rows:list[dict], pred_rows:list[dict],
             accept_consensus:bool=False,
             allowed_splits:tuple[str,...]=('train',)):
    check=validate_rows(gold_rows,require_gold=True,allowed_splits=allowed_splits,
                        accept_consensus=accept_consensus)
    if check['status']!='PASS':
        raise ValueError('Invalid gold: '+str(check['errors'][:5]))
    if len({r.get('id') for r in pred_rows})!=len(pred_rows):
        raise ValueError('Duplicate prediction IDs')
    gold={r['id']:r for r in gold_rows}
    pred={r['id']:r for r in pred_rows}
    if set(gold)!=set(pred):
        raise ValueError(f'Prediction IDs differ from gold: missing={len(set(gold)-set(pred))} extra={len(set(pred)-set(gold))}')
    out={}
    for layer, allowed in (('value_spans',VALUE_LABELS),('cue_spans',CUE_LABELS)):
        tp=Counter(); fp=Counter(); fn=Counter()
        for rid in sorted(gold):
            g={(int(s['start']),int(s['end']),s['label']) for s in gold[rid][layer]}
            p=set()
            if not isinstance(pred[rid].get(layer),list):
                raise ValueError(f'{rid}: missing prediction layer {layer}')
            for s in pred[rid][layer]:
                label=s.get('label')
                start,end=s.get('start'),s.get('end')
                if label not in allowed or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(gold[rid]['current_user_utterance']):
                    raise ValueError(f'{rid}: bad prediction span: {s}')
                tup=(start,end,label)
                if tup in p:
                    raise ValueError(f'{rid}: duplicate prediction span')
                p.add(tup)
            intervals=sorted((start,end) for start,end,_ in p)
            if any(left[1] > right[0] for left,right in zip(intervals, intervals[1:])):
                raise ValueError(f'{rid}: overlapping predictions within {layer}')
            for span in g & p:tp[span[2]]+=1
            for span in p-g:fp[span[2]]+=1
            for span in g-p:fn[span[2]]+=1
        classes={lab:fscore(tp[lab],fp[lab],fn[lab]) for lab in sorted(allowed)}
        evaluable=[v['f1'] for v in classes.values() if v['tp']+v['fn']>0]
        out[layer]={
           'micro':fscore(sum(tp.values()),sum(fp.values()),sum(fn.values())),
           'macro_f1_on_gold_supported_classes':round(sum(evaluable)/len(evaluable),6) if evaluable else None,
           'classes':classes,
           'gold_supported_labels':[lab for lab,v in classes.items() if v['tp']+v['fn']>0],
        }
    return {'status':'MEASURED_FROM_SUPPLIED_GOLD_AND_PREDICTIONS','examples':len(gold_rows),'layers':out}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--gold',required=True,type=Path)
    ap.add_argument('--pred',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    report=evaluate(read_jsonl(args.gold),read_jsonl(args.pred))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'examples':report['examples'], 'value_micro_f1':report['layers']['value_spans']['micro']['f1'], 'cue_micro_f1':report['layers']['cue_spans']['micro']['f1']},indent=2))

if __name__=='__main__':main()
