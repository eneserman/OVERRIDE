#!/usr/bin/env python3
"""Local ONLY: Microsoft Frames user turns -> blinded review candidates.

This does not auto-label any OVERRIDE spans. Obtain corpus via official agreement.
Frame annotations can guide candidate ranking but do not imply gold revision labels.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re

CUES={
 'revision':re.compile(r'\b(instead|actually|change|rather|switch|different|no[,]?|not anymore|make it)\b',re.I),
 'restore':re.compile(r'\b(go back|earlier|original|first option|previous|before|initially)\b',re.I),
 'preserve':re.compile(r'\b(keep|same|still|leave .* as|everything else)\b',re.I),
 'ref':re.compile(r'\b(this one|that one|the other|second one|first one|same hotel|those dates)\b',re.I),
}
def read(path):
    obj=json.loads(path.read_text(encoding='utf-8'))
    if isinstance(obj,list):return obj
    if isinstance(obj,dict):
        for key in ('dialogues','data','conversations'):
            if isinstance(obj.get(key),list):return obj[key]
    raise ValueError('Frames JSON expected list of conversations or object with dialogues/data/conversations list')

def extract(path,limit=200,seed=20261028,history_max=30):
    dialogues=read(path)
    if not dialogues:raise ValueError('Empty Frames corpus')
    output=[]
    seen_dialogues=set()
    for d in dialogues:
        cid=str(d.get('id',''))
        if not cid or cid in seen_dialogues:raise ValueError('Missing or repeated Frames dialogue id')
        seen_dialogues.add(cid)
        prev=[]
        for idx,turn in enumerate(d.get('turns',[])):
            if not isinstance(turn,dict):raise ValueError('Malformed turn')
            author=str(turn.get('author','')).lower()
            txt=turn.get('text')
            if not isinstance(txt,str) or not txt.strip():continue
            speaker='USER' if author in ('user','customer') else 'SYSTEM'
            if speaker=='USER':
                score=sum(bool(pattern.search(txt)) for pattern in CUES.values())
                if score or (idx>1 and idx%5==0):
                    eid=hashlib.sha256(f'FRAMES::{cid}::{idx}'.encode()).hexdigest()[:20]
                    rec={'example_id':'frames_'+eid,
                         'source':{'dataset':'FRAMES','split':'prospective','dialogue_id':cid,'turn_index':idx},
                         'history':prev[-history_max:].copy(),
                         'current_user_utterance':txt,
                         'annotation':{'status':'UNLABELED','guideline_version':'v0.8_frames',
                            'value_spans':None,'cue_spans':None,'transitions':None,'difficulty':None}}
                    output.append((score,rec))
            prev.append({'speaker':speaker,'turn_index':idx,'utterance':txt})
    rng=random.Random(seed)
    rng.shuffle(output)
    selected=sorted(output,key=lambda x:-x[0])[:limit]
    return [r for _,r in selected], {'candidate_count':len(output),'selected_count':len(selected),
          'dialogue_count':len(dialogues),'selection':'ranked heuristic candidates + periodic negatives; not random gold or representative distribution',
          'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'official_license_agreement':'MUST_BE_CONFIRMED_BEFORE_REDISTRIBUTION'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--frames-json',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--metadata-out',type=Path,required=True)
    p.add_argument('--limit',type=int,default=200)
    p.add_argument('--seed',type=int,default=20261028)
    p.add_argument('--history-max',type=int,default=30)
    a=p.parse_args()
    if a.limit<1 or a.history_max<1:raise SystemExit('Positive limit/history-max required')
    for file in (a.out,a.metadata_out):
        if file.exists():raise SystemExit(f'Refusing to overwrite existing data: {file}')
    records,meta=extract(a.frames_json,a.limit,a.seed,a.history_max)
    for file in (a.out,a.metadata_out):file.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in records),encoding='utf-8')
    a.metadata_out.write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'UNLABELED_FRAMES_CANDIDATES_ONLY','count':len(records)}))
if __name__=='__main__':main()
