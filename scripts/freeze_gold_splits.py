#!/usr/bin/env python3
"""Freeze immutable, dialogue-family-grouped custom gold splits.

Splits require human adjudication; script does not label or learn.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
from pathlib import Path
from validate_annotations import read_jsonl, validate_rows


def freeze(rows: list[dict], seed: int = 42) -> dict:
    validation = validate_rows(rows, require_gold=True)
    if validation['status'] != 'PASS':
        raise ValueError('Refusing to split invalid/unadjudicated data: '+str(validation['errors'][:5]))
    groups = collections.defaultdict(list)
    for row in rows:
        family = row.get('dialogue_family_id') or row['source']['dialogue_id']
        groups[str(family)].append(row['id'])
    if len(groups) < 3:
        raise ValueError('Need at least three independent dialogue families for train/dev/test')
    # Content-bound fingerprint prevents later silent edits to gold labels/text
    # from masquerading as an unchanged frozen split manifest.
    canonical = json.dumps(sorted(rows, key=lambda r: r['id']), ensure_ascii=False,
                           sort_keys=True, separators=(',', ':'))
    gold_content_sha256 = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    # Hash-based stable grouping. Assignment is determined solely by family and seed.
    manifest = {'algorithm':'sha256_family_bucket_v1','seed':seed,'gold_content_sha256':gold_content_sha256,
                'splits':{'train':[],'dev':[],'test':[]},'family_assignment':{}}
    for family in sorted(groups):
        hash_hex = hashlib.sha256(f'{seed}::{family}'.encode()).hexdigest()
        bucket = int(hash_hex[:15], 16) / float(16 ** 15)
        split = 'train' if bucket < .8 else ('dev' if bucket < .9 else 'test')
        manifest['family_assignment'][family] = split
        manifest['splits'][split].extend(sorted(groups[family]))
    if any(not ids for ids in manifest['splits'].values()):
        raise ValueError('Hash split produced an empty partition: increase families or alter documented seed before freezing')
    for key in manifest['splits']:
        manifest['splits'][key].sort()
    manifest['family_counts'] = dict(collections.Counter(manifest['family_assignment'].values()))
    manifest['example_counts'] = {k:len(v) for k,v in manifest['splits'].items()}
    by_id={r['id']:r for r in rows}
    manifest['gold_span_support_by_split']={}
    for split, ids in manifest['splits'].items():
        counts={layer: collections.Counter() for layer in ('value_spans','cue_spans')}
        for eid in ids:
            for layer in counts:
                counts[layer].update(s['label'] for s in by_id[eid][layer])
        manifest['gold_span_support_by_split'][split]={layer:dict(sorted(counter.items()))
                                                          for layer,counter in counts.items()}
    # Empty test supports must be reported and may require a prospective,
    # pre-registration split redesign before ANY model comparison.
    manifest['test_unsupported_labels']={layer: sorted({s['label'] for row in rows
                                     for s in row[layer]}-set(manifest['gold_span_support_by_split']['test'][layer]))
                                    for layer in ('value_spans','cue_spans')}
    manifest['manifest_digest'] = hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--gold',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seed',type=int,default=42)
    args=ap.parse_args()
    result=freeze(read_jsonl(args.gold),args.seed)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists():
        raise SystemExit(f'ABORT: refusing to overwrite frozen manifest: {args.out}')
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'FROZEN','file':str(args.out),'hash':result['manifest_digest'],'counts':result['example_counts']},indent=2))

if __name__=='__main__':
    main()
