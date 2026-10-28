#!/usr/bin/env python3
"""Tamper-evident prospective RAW candidate lock; NOT a gold data freeze.

No existing AI-reviewed SGD pilot dialogue/text may enter this holdout.
Accepts new official SGD dev/test or external Frames human-written real dialogues.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))

def sha(obj):
    if isinstance(obj,bytes): return hashlib.sha256(obj).hexdigest()
    return hashlib.sha256(canonical(obj).encode('utf-8')).hexdigest()

def norm(text): return re.sub(r'\s+',' ',text.casefold()).strip()

def lines(path):
    with path.open(encoding='utf-8') as f:
        for no,line in enumerate(f,1):
            if not line.strip():continue
            try: yield json.loads(line)
            except Exception as exc: raise ValueError(f'{path}:{no}: invalid JSON {exc}') from exc

def rowid(r): return r.get('id',r.get('example_id'))

def sourceid(r):
    s=r.get('source') or {}
    dataset=s.get('dataset') or s.get('origin_corpus')
    split=s.get('split') or s.get('origin_split')
    dialogue=s.get('dialogue_id') or r.get('dialogue_family_id')
    turn=s.get('turn_index')
    return dataset,split,dialogue,turn

def footprint(r):
    dataset,split,dialogue,turn=sourceid(r)
    h=r.get('history',[])
    return {'id':rowid(r),'source':{'dataset':dataset,'split':split,'dialogue_id':dialogue,'turn_index':turn},
            'current_user_utterance':r.get('current_user_utterance'),
            'history':h}

def seen_registry(paths):
    ids=set(); families=set();utterances=set()
    for p in paths:
        for r in lines(p):
            ids.add(str(rowid(r)))
            ds,_,di,_=sourceid(r)
            if ds and di: families.add((str(ds).casefold(),str(di)))
            u=r.get('current_user_utterance') or ''
            if u:utterances.add(norm(u))
    return ids,families,utterances

def create_lock(pool,seen_paths,commit,license_status,seed=20261028,source_release_id=None):
    rows=list(lines(pool))
    if not rows: raise ValueError('Empty pool')
    source_datasets={sourceid(r)[0] for r in rows}
    if source_datasets=={'SGD'}:
        if not isinstance(commit,str) or not re.fullmatch(r'[0-9a-f]{7,40}',commit):
            raise ValueError('SGD needs real git commit SHA, 7..40 hex characters')
    elif source_datasets=={'FRAMES'}:
        if not isinstance(source_release_id,str) or not source_release_id.strip():
            raise ValueError('Frames requires an official portal release identifier, not a fake git SHA')
        commit=None
    else:
        raise ValueError('Separate source corpora into independently frozen pools')
    seen_ids,seen_families,seen_texts=seen_registry(seen_paths)
    ids=set();fam=set();texts=set();manifest_rows=[]
    for r in rows:
        dataset,split,dialogue,turn=sourceid(r)
        rid=rowid(r);u=r.get('current_user_utterance')
        if not isinstance(rid,str) or not rid or not isinstance(u,str) or not u.strip():
            raise ValueError('Missing id or utterance')
        if not isinstance(dialogue,str) or not dialogue or not isinstance(turn,int) or turn<0:
            raise ValueError(f'{rid} missing source provenance')
        if dataset=='SGD' and split not in ('dev','test'):
            raise ValueError(f'{rid} SGD blind pool must come from unseen official dev/test, got {split}')
        if dataset not in ('SGD','FRAMES'):
            raise ValueError(f'{rid} unsupported dataset for real blinded holdout: {dataset}')
        if dataset=='FRAMES' and split not in ('prospective','test'):
            raise ValueError(f'{rid} Frames split must be a prospective disjoint holdout')
        if r.get('annotation',{}).get('status') not in (None,'UNLABELED'):
            raise ValueError(f'{rid} appears to contain label/reviewer status')
        if any(k in r for k in ('value_spans','cue_spans','transitions','links','prediction')):
            raise ValueError(f'{rid} includes labels/predictions')
        if any(r.get('annotation',{}).get(k) is not None for k in ('cue_spans','value_spans','transitions','difficulty')):
            raise ValueError(f'{rid} has annotation leakage')
        family=(dataset.casefold(),dialogue)
        if rid in ids or rid in seen_ids or family in seen_families or norm(u) in seen_texts:
            raise ValueError(f'Contamination or repeated id/dialogue/text: {rid}')
        if norm(u) in texts: raise ValueError(f'Duplicate candidate utterance: {rid}')
        for h in r.get('history',[]):
            if not isinstance(h.get('turn_index'),int) or h['turn_index']>=turn:
                raise ValueError(f'{rid} future/unknown history turn index')
        ids.add(rid);fam.add(family);texts.add(norm(u))
        manifest_rows.append({'id':rid,'corpus':dataset,'official_source_split':split,'dialogue_family_id':dialogue,
            'turn_index':turn,'raw_record_sha256':sha(footprint(r)),
            'current_text_sha256':hashlib.sha256(u.encode()).hexdigest()})
    manifest_rows.sort(key=lambda x:x['id'])
    manifest={'status':'RAW_POOL_LOCKED_NOT_HUMAN_GOLD',
       'protocol_version':'v0.8','algorithm':'prospective_raw_pool_sha256_v1','seed':seed,
       'source_commit_sha':commit,'source_release_id':source_release_id,'license_status':license_status,
       'source_file_sha256':hashlib.sha256(pool.read_bytes()).hexdigest(),
       'source_file_bytes':pool.stat().st_size,
       'seen_files_sha256':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in seen_paths},
       'counts':{'candidate_examples':len(rows),'dialogue_families':len(fam)},
       'test_candidates':manifest_rows,
       'note':'Raw pool frozen; NO custom revision gold labels or measured model F1 exist yet.'}
    manifest['manifest_sha256']=sha(manifest)
    return manifest

def verify_lock(pool,seen_paths,manifest):
    constructed=create_lock(pool,seen_paths,manifest['source_commit_sha'],manifest['license_status'],manifest['seed'],manifest.get('source_release_id'))
    if constructed != manifest:raise ValueError('Lock verification FAIL: source/seen file or manifest changed')
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pool',type=Path,required=True)
    ap.add_argument('--seen',type=Path,action='append',default=[])
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--source-commit-sha')
    ap.add_argument('--source-release-id',help='Official release identifier for Frames portal-only files')
    ap.add_argument('--license-status',choices=('VERIFIED','REVIEW_REQUIRED'),required=True)
    ap.add_argument('--seed',type=int,default=20261028)
    ap.add_argument('--verify',action='store_true')
    a=ap.parse_args()
    if a.verify:
        if not a.out.is_file(): raise SystemExit('No existing manifest to verify')
        verify_lock(a.pool,a.seen,json.loads(a.out.read_text(encoding='utf-8')))
        print(json.dumps({'status':'RAW_POOL_LOCK_VALID','manifest':str(a.out)}));return
    if a.out.exists(): raise SystemExit('Refuse to overwrite existing frozen manifest: '+str(a.out))
    if not a.seen: raise SystemExit('Specify at least one --seen contamination source (prior SGD pilot)')
    output=create_lock(a.pool,a.seen,a.source_commit_sha,a.license_status,a.seed,a.source_release_id)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':output['status'],'count':output['counts'],'manifest_sha256':output['manifest_sha256']}))
if __name__=='__main__': main()
