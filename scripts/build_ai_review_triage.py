"""AI disagreement triage. Never claim human IAA; all examples need human review."""
import argparse
import collections
import csv
import json
from pathlib import Path

def load(p):
    return [json.loads(z) for z in Path(p).read_text(encoding='utf-8').splitlines() if z.strip()]

def sset(r,head):
    return {(int(x['start']),int(x['end']),x['label']) for x in r['annotation'][head]}

def run(a,b,out):
    A=load(a);B=load(b)
    assert len(A)==len(B) and len({x['example_id'] for x in A})==len(A)
    m={x['example_id']:x for x in B}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=[]; differing=0
    for r in A:
        other=m[r['example_id']]
        assert (r['current_user_utterance'],r['history'])==(other['current_user_utterance'],other['history'])
        vdiff=sset(r,'value_spans')!=sset(other,'value_spans')
        cdiff=sset(r,'cue_spans')!=sset(other,'cue_spans')
        transitions_differ=r['annotation']['transitions']!=other['annotation']['transitions']
        different=vdiff or cdiff or transitions_differ
        differing+=bool(different)
        records.append({
          'example_id':r['example_id'],'priority': 'REVIEW_FIRST' if different else 'REVIEW',
          'cue_disagreement':int(cdiff),'value_disagreement':int(vdiff),'transition_disagreement':int(transitions_differ),
          'current_user_utterance':r['current_user_utterance'],
          'human_status':'NOT_REVIEWED',
          'provenance':'AI_SIMULATION_ONLY'
        })
    with (out/'AI_TRIAGE_QUEUE.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(sorted(records,key=lambda r:r['priority']=='REVIEW'))
    report={'records':len(records),'AI_ANY_DISAGREEMENT_EXAMPLES':differing,'AI_SAME_SUGGESTIONS_EXAMPLES':len(records)-differing,'human_IAA':None,'human_gold_records':0,'note':'Even AI agreements are NOT presumed gold. Review all cases; disagreements first.'}
    (out/'AI_TRIAGE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--a',required=True);p.add_argument('--b',required=True);p.add_argument('--out',required=True);x=p.parse_args()
    print(json.dumps(run(x.a,x.b,x.out),indent=2))
