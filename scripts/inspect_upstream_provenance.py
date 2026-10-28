#!/usr/bin/env python3
"""Pins actual raw SGD provenance and checks split files (read only).

Not a substitute for OVERRIDE annotation. Requires locally cloned source.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

def inspect(root):
    root=root.resolve()
    if not root.is_dir():raise ValueError(f'No SGD checkout at {root}')
    try:commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    except Exception as exc:raise ValueError('SGD root must be a git repository with pinned commit') from exc
    manifest={'kind':'REAL_UPSTREAM_SGD_PROVENANCE','git_commit':commit,'splits':{},
              'purpose':'source reproducibility, not OVERRIDE gold'}
    for split in ('train','dev','test'):
        directory=root/split
        files=sorted(directory.glob('dialogues_*.json'))
        if not files:raise ValueError(f'Missing official source files: {directory}')
        info=[];dialogue_ids=set();count=0;turncount=0
        for path in files:
            data=json.loads(path.read_text(encoding='utf-8'))
            if not isinstance(data,list):raise ValueError(f'Expected list {path}')
            for r in data:
                if 'dialogue_id' not in r or not isinstance(r.get('turns'),list):raise ValueError(f'Unexpected schema in {path}')
                did=r['dialogue_id']
                if did in dialogue_ids:raise ValueError(f'ID duplicated within {split}: {did}')
                dialogue_ids.add(did);count+=1;turncount+=len(r['turns'])
            info.append({'relative_file':str(path.relative_to(root)),
                         'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                         'dialogue_count':len(data)})
        manifest['splits'][split]={'dialogues':count,'turns':turncount,'files':info}
    return manifest

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sgd-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise SystemExit('Refusing to overwrite provenance record')
    result=inspect(a.sgd_root)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'REAL_SOURCE_VERIFIED','git_commit':result['git_commit'],
        'dialogue_counts':{k:v['dialogues'] for k,v in result['splits'].items()}}))
if __name__=='__main__':main()
