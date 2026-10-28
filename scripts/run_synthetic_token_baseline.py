#!/usr/bin/env python3
"""Actually trains a classical token-level BIO baseline, solely on synthetic data.

IMPORTANT: Results here are SYNTHETIC_DIAGNOSTIC, never real-world gold scores.
No pretrained Transformer, no claim of contextual linguistic reasoning.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

TOKEN = re.compile(r"\w+(?:['’]\w+)?|[^\w\s]", re.UNICODE)
LAYERS = ('value_spans', 'cue_spans')

def load_jsonl(path):
    rows=[]
    with path.open(encoding='utf-8') as f:
        for no,line in enumerate(f,1):
            if line.strip():
                try: rows.append(json.loads(line))
                except Exception as e: raise ValueError(f'{path}:{no}: {e}') from e
    if not rows: raise ValueError(f'Empty data {path}')
    if any(x.get('annotation',{}).get('status')!='SYNTHETIC_PROGRAMMATIC' for x in rows):
        raise ValueError('Synthetic baseline refuses non-synthetic labels to avoid misreporting research scores')
    return rows

def tokenize(txt):
    return [(m.group(0),m.start(),m.end()) for m in TOKEN.finditer(txt)]

def gold_tags(row,tokens,layer):
    tags=['O']*len(tokens)
    for span in row[layer]:
        s,e=span['start'],span['end']
        if row['current_user_utterance'][s:e]!=span['text']:
            raise ValueError(f'Bad span text in {row["id"]} {span}')
        ix=[i for i,(_,a,b) in enumerate(tokens) if a>=s and b<=e]
        if not ix or tokens[ix[0]][1]!=s or tokens[ix[-1]][2]!=e:
            raise ValueError(f'Boundary not token aligned in {row["id"]}: {span}')
        for j,i in enumerate(ix):
            if tags[i]!='O': raise ValueError('Overlap within layer')
            tags[i]=('B-' if j==0 else 'I-')+span['label']
    return tags

def features(tokens,i,row,context):
    w=tokens[i][0]
    f={'bias':1, 'lower':w.lower(),'prefix2':w.lower()[:2],
       'suffix2':w.lower()[-2:],'is_title':w.istitle(),
       'is_digit':w.isdigit(),'has_digit':any(c.isdigit() for c in w),
       'is_punct':not any(c.isalnum() for c in w),
       'position':min(i//4,10),
       'prev': tokens[i-1][0].lower() if i else '<BOS>',
       'next':tokens[i+1][0].lower() if i+1<len(tokens) else '<EOS>',
       'prev2':tokens[i-2][0].lower() if i>1 else '<BOS2>',
       'next2':tokens[i+2][0].lower() if i+2<len(tokens) else '<EOS2>'}
    if context:
        hist=' '.join(x.get('utterance','') for x in row.get('history',[]))
        lower=hist.lower()
        hist_tokens=set(w.lower() for w,_,_ in tokenize(hist))
        f['history_token_present']=w.lower() in hist_tokens
        f['history_excerpt_mentioned']=(w.isalnum() and len(w)>2 and w.lower() in lower)
        f['history_turn_count_bin']=min(len(row.get('history',[])),7)
    return f

def featurize(rows,layer,context):
    X=[];Y=[];boundaries=[]
    for r in rows:
        tokens=tokenize(r['current_user_utterance'])
        if not tokens: raise ValueError('Empty token sequence')
        tags=gold_tags(r,tokens,layer)
        boundaries.append((r,tokens,len(X),len(X)+len(tokens)))
        for i in range(len(tokens)):
            X.append(features(tokens,i,r,context));Y.append(tags[i])
    return X,Y,boundaries

def decode(tags,tokens):
    out=[];active=None
    for tag,(_,s,e) in zip(tags,tokens):
        if tag=='O':
            if active: out.append(active);active=None
            continue
        m=re.fullmatch(r'([BI])-(.+)',tag)
        if not m: raise ValueError(f'Unknown BIO label {tag}')
        prefix,label=m.groups()
        if prefix=='B' or active is None or active['label']!=label:
            if active: out.append(active)
            active={'start':s,'end':e,'label':label}
        else: active['end']=e
    if active:out.append(active)
    return out

def metrics(gold,pred):
    correct=Counter(); total_gold=Counter();total_pred=Counter()
    for g,p in zip(gold,pred):
        gs={(s['start'],s['end'],s['label']) for s in g}
        ps={(s['start'],s['end'],s['label']) for s in p}
        total_gold.update(label for _,_,label in gs)
        total_pred.update(label for _,_,label in ps)
        correct.update(label for _,_,label in gs&ps)
    scores={}
    for k in sorted(total_gold.keys()|total_pred.keys()):
        tp=correct[k];ng=total_gold[k];np=total_pred[k]
        pr=tp/np if np else 0.; re=tp/ng if ng else 0.
        f=2*pr*re/(pr+re) if pr+re else 0.
        scores[k]={'gold':ng,'predicted':np,'correct':tp,'precision':round(pr,4),'recall':round(re,4),'f1':round(f,4)}
    tp=sum(correct.values()); pg=sum(total_gold.values());pp=sum(total_pred.values())
    return {'strict_micro_precision':round(tp/pp,4) if pp else 0,
            'strict_micro_recall':round(tp/pg,4) if pg else 0,
            'strict_micro_f1':round(2*tp/(pp+pg),4) if pp+pg else 0,
            'gold_spans':pg,'predicted_spans':pp,'exact_matches':tp,'per_label':scores}

def train_eval(train,evaluation,layer,context,seed):
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.svm import LinearSVC
    x,y,_=featurize(train,layer,context)
    ex,_,bounds=featurize(evaluation,layer,context)
    vector=DictVectorizer(sparse=True)
    X=vector.fit_transform(x); EX=vector.transform(ex)
    clf=LinearSVC(random_state=seed,max_iter=3000)
    clf.fit(X,y); tags=clf.predict(EX)
    gt=[];pr=[]
    for row,tokens,a,b in bounds:
        gt.append(row[layer]);pr.append(decode(tags[a:b],tokens))
    return metrics(gt,pr),{'train_tokens':len(y),'test_tokens':len(tags),
                            'features':len(vector.get_feature_names_out()),
                            'classifier':'sklearn.svm.LinearSVC (token-independent lexical baseline)'}

def execute(root,seed):
    d=root/'data/synthetic_bootstrap'
    train=load_jsonl(d/'synthetic_train.jsonl')
    dev=load_jsonl(d/'synthetic_dev.jsonl')
    challenge=load_jsonl(d/'synthetic_challenge.jsonl')
    from sklearn import __version__ as sklver
    output={'experiment_id':'V08_SYNTHETIC_LEXICAL_BIO',
            'result_type':'SYNTHETIC_DIAGNOSTIC_ONLY',
            'academic_real_gold_test':'NOT_RUN',
            'date_utc':datetime.now(timezone.utc).isoformat(),
            'seed':seed,'library':'scikit-learn '+sklver,
            'data_counts':{'train':len(train),'dev':len(dev),'challenge':len(challenge)},
            'input_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in d.glob('synthetic_*.jsonl')},
            'results':{}}
    for history in (False,True):
        name='current_turn_only' if not history else 'with_history_lexical_features'
        output['results'][name]={}
        for part,evalrows in [('dev',dev),('challenge',challenge)]:
            output['results'][name][part]={}
            for layer in LAYERS:
                m,details=train_eval(train,evalrows,layer,history,seed)
                output['results'][name][part][layer]={'metrics':m,'technical':details}
    return output

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--seed',type=int,default=20261028)
    args=ap.parse_args()
    output=execute(args.root,args.seed)
    args.out.parent.mkdir(exist_ok=True,parents=True)
    args.out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':'MEASURED_SYNTHETIC_ONLY','out':str(args.out),
        'challenge_f1':{name:{layer:results['challenge'][layer]['metrics']['strict_micro_f1']
            for layer in LAYERS} for name,results in output['results'].items()}},indent=2))
if __name__=='__main__':main()
