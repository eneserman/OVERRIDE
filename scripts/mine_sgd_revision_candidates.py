"""Mine REAL SGD candidates for independent human review. Candidate != gold.

No external dependencies; reads official SGD dialogue files in the local repository.
All sampling buckets are PRIVATE and are not disclosed in blind reviewer packets.
"""
import argparse
import collections
import hashlib
import json
import random
import re
from pathlib import Path

BUCKETS = {
    "RESTORE": r"\b(?:go back|back to|restore|revert|first (?:option|choice|one)|original|earlier choice)\b",
    "KEEP": r"\b(?:keep|same|don't change|do not change|leave .* as is|everything else|retain|preserve)\b",
    "CANCEL": r"\b(?:cancel|not now|never mind|nevermind|forget (?:it|that)|don't book|do not book|no longer want)\b",
    "UPDATE": r"\b(?:instead|actually|change|switch|rather|make it|not .* but|i meant|on second thought|correction)\b",
    "REFERENCE": r"\b(?:that one|the first|the second|the previous|the earlier|what i said|the one i)\b",
}
PATTERNS = {k: re.compile(v, re.I) for k,v in BUCKETS.items()}


def read_dialogues(root, split="train"):
    folder = Path(root) / split
    files = sorted(folder.glob("dialogues_*.json"))
    if not files:
        raise FileNotFoundError(f"No official SGD dialogues_*.json found under {folder}")
    for path in files:
        raw=path.read_bytes()
        blob=json.loads(raw)
        if not isinstance(blob,list):
            raise ValueError(f"Expected JSON list in {path}")
        for d in blob:
            yield d, path.name, hashlib.sha256(raw).hexdigest()


def detect_bucket(text, history):
    hits=[k for k,p in PATTERNS.items() if p.search(text)]
    if len(hits)>=2: return "MIXED",hits
    if hits: return hits[0],hits
    if len(history)>=2: return "HARD_NEGATIVE",[]
    return "NO_CONTEXT",[]


def scan_dialogues(root, split="train", history_limit=12):
    allrows=[]
    observed=collections.Counter()
    per_domain=collections.Counter()
    for d,fn,digest in read_dialogues(root,split):
        history=[]
        did=d.get("dialogue_id","")
        if not did:raise ValueError(f"Missing dialogue_id in {fn}")
        for idx,t in enumerate(d.get("turns",[])):
            speaker=t.get("speaker")
            current=t.get("utterance","")
            if not isinstance(current,str):raise ValueError(f"Non-text turn {did}/{idx}")
            if speaker=="USER":
                bucket,hits=detect_bucket(current,history)
                service=(d.get("services") or ["UNKNOWN"])[0]
                rid="SGD-"+hashlib.sha256(f"{split}:{did}:{idx}".encode()).hexdigest()[:18]
                record={
                   "example_id":rid,
                   "source":{"dataset":"SGD","split":split,"dialogue_id":did,"turn_index":idx,"service":service,"source_file":fn,"source_file_sha256":digest},
                   "history":history[-history_limit:].copy(),
                   "current_user_utterance":current,
                   "annotation":{"status":"UNLABELED","guideline_version":"pilot_v0.1","value_spans":None,"cue_spans":None,"transitions":None,"uncertainty_notes":None,"difficulty":None},
                }
                # private metadata MUST NEVER be included in reviewer packets
                allrows.append((bucket,tuple(hits),service,record))
                observed[bucket]+=1;per_domain[service]+=1
            history.append({"turn_index":idx,"speaker":speaker,"utterance":current})
    return allrows,observed,per_domain


def sample(rows, per_bucket=50, seed=42):
    rng=random.Random(seed)
    buckets=collections.defaultdict(list)
    for bucket,hits,service,rec in rows:
        buckets[bucket].append((bucket,hits,service,rec))
    chosen=[];seen_dialogues=set();picked=collections.Counter()
    for bucket in ("MIXED","RESTORE","KEEP","CANCEL","UPDATE","REFERENCE","HARD_NEGATIVE","NO_CONTEXT"):
        options=buckets[bucket][:]
        rng.shuffle(options)
        # greedily favor a diversity of services (not a guarantee)
        service_count=collections.Counter()
        options.sort(key=lambda x:service_count[x[2]])
        for row in options:
            if picked[bucket]>=per_bucket:break
            did=row[3]["source"]["dialogue_id"]
            if did in seen_dialogues:continue
            chosen.append(row)
            picked[bucket]+=1
            seen_dialogues.add(did)
            service_count[row[2]]+=1
    rng.shuffle(chosen)
    return chosen,picked


def write(out,chosen,observed,per_domain,picked,split,seed):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    unlabelled=[x[3] for x in chosen]
    # Reviewers receive only unlabeled utterances/context; no candidate heuristics.
    encoded="".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in unlabelled)
    for file in ("reviewer_A_BLIND.jsonl","reviewer_B_BLIND.jsonl"):
        dest=out/file
        if dest.exists():raise FileExistsError(f"Refusing to overwrite existing {dest}")
        dest.write_text(encoded,encoding="utf-8")
    private=[{"example_id":x[3]["example_id"],"mining_bucket":x[0],"regex_hits":list(x[1]),"service":x[2]} for x in chosen]
    (out/"PRIVATE_mining_manifest.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in private),encoding="utf-8")
    report={"origin":"actual official SGD files provided locally", "split":split,"selected":len(chosen),"scanned_candidate_turns":sum(observed.values()),"observed_buckets":dict(observed),"selected_buckets":dict(picked),"selected_services":dict(collections.Counter(x[2] for x in chosen)),"source_services_scanned":len(per_domain),"seed":seed,"blind_reviewer_sha256":hashlib.sha256(encoded.encode()).hexdigest(),"gold_count":0,"warning":"Candidate mining is heuristic only; all examples require independent human label review and adjudication; no claim of gold or accuracy."}
    (out/"mining_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sgd-root",required=True)
    ap.add_argument("--split",choices=["train","dev","test"],default="train")
    ap.add_argument("--out",required=True)
    ap.add_argument("--per-bucket",type=int,default=50)
    ap.add_argument("--seed",type=int,default=42)
    args=ap.parse_args()
    if args.per_bucket<=0:ap.error("--per-bucket must be positive")
    rows,obs,domains=scan_dialogues(args.sgd_root,args.split)
    chosen,picked=sample(rows,args.per_bucket,args.seed)
    print(json.dumps(write(args.out,chosen,obs,domains,picked,args.split,args.seed),indent=2))

if __name__=="__main__":main()
