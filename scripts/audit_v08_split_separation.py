#!/usr/bin/env python3
"""Inspect within/between synthetic split lexical overlap, no academic claims."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re

def load(path):return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
def tokens(txt):return set(re.findall(r'\w+',txt.casefold()))
def norm(txt):return re.sub(r'\s+',' ',txt.casefold()).strip()
def scan(root):
    path=root/'data/synthetic_bootstrap'
    files={name:path/f'synthetic_{name}.jsonl' for name in ('train','dev','challenge')}
    rows={name:load(p) for name,p in files.items()}
    result={'type':'SYNTHETIC_SPLIT_DIAGNOSTIC','source_status':'SYNTHETIC_PROGRAMMATIC_NOT_HUMAN_GOLD',
            'records':{x:len(v) for x,v in rows.items()},'sha256':{x:hashlib.sha256(p.read_bytes()).hexdigest() for x,p in files.items()},
            'within_split_duplicate_utterances':{},'pairwise':{},'support':{}}
    for name,rs in rows.items():
        c=collections.Counter(norm(r['current_user_utterance']) for r in rs)
        result['within_split_duplicate_utterances'][name]=sum(v-1 for v in c.values() if v>1)
        counts=collections.Counter(s['label'] for r in rs for k in ('value_spans','cue_spans') for s in r[k])
        result['support'][name]=dict(sorted(counts.items()))
    for left,right in [('train','dev'),('train','challenge'),('dev','challenge')]:
        a=rows[left];b=rows[right]
        aset={norm(r['current_user_utterance']) for r in a}
        bset={norm(r['current_user_utterance']) for r in b}
        cross=[]
        for x in b:
            xb=tokens(x['current_user_utterance'])
            for y in a:
                ya=tokens(y['current_user_utterance']);sim=len(xb&ya)/len(xb|ya) if xb|ya else 0
                if sim>=0.90:
                    cross.append({'left':y['id'],'right':x['id'],'token_jaccard':round(sim,3)})
        result['pairwise'][f'{left}_vs_{right}']={
            'exact_current_turn_collisions':len(aset&bset),
            'high_lexical_overlap_pairs_jaccard_ge_0_9':len(cross),
            'overlap_examples':cross[:12]}
    result['interpretation']='Same deterministic generator and shared vocab/recipes even without exact duplicates; heldout template challenge is NOT independent real test.'
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    v=scan(a.root);a.out.parent.mkdir(exist_ok=True,parents=True)
    a.out.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':v['type'],'pairwise':v['pairwise']},ensure_ascii=False,indent=2)[:1800])
if __name__=='__main__':main()
