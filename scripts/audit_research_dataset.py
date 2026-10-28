"""Audits AI suggestion provenance, synthetic exactness, split families and missing gold.
Return 0 for structural integrity; use --require-academic-gold to require actual adjudicated gold.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from build_synthetic_bootstrap import validate_record, V_LABELS, C_LABELS


def read_jsonl(path):
    lines=Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def audit(root):
    root=Path(root)
    generated=root/'data'/'synthetic_bootstrap'
    manifest=json.loads((generated/'generation_manifest.json').read_text(encoding='utf-8'))
    summary={"structural_pass":True,"academic_gold_ready":False,"issues":[],"synthetic":{},"sgd_pilot":{},"AI_suggestions":{}}
    families={}
    all_text=set()
    for split in ('train','dev','challenge'):
        path=generated/f'synthetic_{split}.jsonl'
        rs=read_jsonl(path)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if digest!=manifest['files_sha256'][path.name]: raise ValueError(f"Hash mismatch: {path}")
        if len(rs)!=manifest['counts'][split]:raise ValueError(f"Count mismatch: {split}")
        fam=set(); cc=collections.Counter()
        for r in rs:
            validate_record(r)
            if r['source']['split']!=f'synthetic_{split}':raise ValueError('Split contamination')
            fam.add(r['source']['template_family'])
            sig=(r['current_user_utterance'],tuple(x['utterance'] for x in r['history']))
            if sig in all_text:raise ValueError('Duplicated synthetic pair')
            all_text.add(sig)
            cc.update(x['label'] for key in ('value_spans','cue_spans') for x in r[key])
        if dict(sorted(cc.items()))!=manifest['span_support'][split]:raise ValueError('Label support mismatch')
        families[split]=fam
        summary['synthetic'][split]={"records":len(rs),"span_support":dict(cc),"zero_classes":sorted((V_LABELS|C_LABELS)-set(cc))}
    for a in families:
        for b in families:
            if a!=b and families[a]&families[b]:raise ValueError(f"Template family overlap: {a}/{b}")
    src=root/'data'/'sgd_pilot'
    a=read_jsonl(src/'annotator_A_UNLABELED.jsonl')
    b=read_jsonl(src/'annotator_B_UNLABELED.jsonl')
    if a!=b:raise ValueError('Pilot reviewer packets differ')
    ids=[r['example_id'] for r in a]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate pilot ID')
    if any(r['annotation']['status']!='UNLABELED' for r in a):raise ValueError('Pilot source altered')
    summary['sgd_pilot']={"examples":len(a),"source":"user-supplied SGD-derived pilot; underlying upstream files not independently downloaded here","gold_examples":0}
    ai=root/'data'/'ai_suggestions'
    pa=read_jsonl(ai/'annotator_A_AI_DRAFT.jsonl')
    pb=read_jsonl(ai/'annotator_B_AI_DRAFT.jsonl')
    if len(pa)!=len(pb) or [x['example_id'] for x in pa]!=ids or [x['example_id'] for x in pb]!=ids:raise ValueError('AI pilot alignment invalid')
    for name,rs in (('A',pa),('B',pb)):
        cnt=collections.Counter()
        positives=0
        for r in rs:
            if r['annotation']['status']!='AI_DRAFT' or r['annotation']['annotator_type']!='AI_SIMULATION':raise ValueError('AI provenance improperly marked')
            s=r['current_user_utterance']
            if r['annotation']['value_spans'] or r['annotation']['cue_spans']:positives+=1
            for head in ('cue_spans','value_spans'):
                for span in r['annotation'][head]:
                    if s[span['start']:span['end']]!=span['text']: raise ValueError('Bad AI span offset')
                    cnt[span['label']]+=1
        summary['AI_suggestions'][name]={"records":len(rs),"any_spans":positives,"span_support":dict(cnt),"not_human":True,"not_gold":True}
    gold=list((root/'data'/'gold').glob('*.jsonl'))
    if gold: summary['issues'].append('Presence of gold-like filenames does NOT prove human validation; independently audit review/adjudication provenance.')
    else: summary['issues'].append('No independently human-adjudicated SGD gold dataset exists yet.')
    summary['issues'] += [
      'Synthetic challenge set is only a rule/template held-out regression suite; it is NOT the final unbiased academic evaluation.',
      'A/B AI suggestions are from one model family; they do NOT constitute inter-annotator agreement.',
      'All synthetic examples must be labeled synthetic in training statistics; do not claim them as SGD or native annotations.',
      'Real SGD source files were not independently downloaded during this build; verify full source SHA-256 locally.',
      'A complete production model training and real-data external validation is not included in this dataset pack.',
    ]
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--project-root',default='.')
    ap.add_argument('--out')
    ap.add_argument('--require-academic-gold',action='store_true')
    x=ap.parse_args()
    r=audit(Path(x.project_root))
    if x.out:Path(x.out).write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(r,indent=2,ensure_ascii=False))
    if x.require_academic_gold and not r['academic_gold_ready']:raise SystemExit(2)

if __name__=='__main__':main()
