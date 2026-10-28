"""Deterministic synthetic OVERRIDE bootstrap. NEVER report as human gold.

Uses explicit compositional labels and verifies exact character offsets.
Run: python scripts/build_synthetic_bootstrap.py --out data/synthetic_bootstrap
"""
import argparse
import collections
import hashlib
import json
import random
from pathlib import Path

DESTINATIONS = ["Paris", "Berlin", "Rome", "Lisbon", "Prague", "Oslo", "Vienna", "Madrid", "Dublin", "Boston", "Toronto", "Seattle", "Denver", "Miami", "Chicago", "Tokyo", "Kyoto", "Seoul", "Athens", "Cairo", "Helsinki", "Zurich", "Nice", "Lyon"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
RIDES = ["regular", "pooled", "premium", "shared"]
CATEGORIES = ["replace_explicit", "replace_implicit", "keep_named", "keep_unspecified", "cancel_intent", "restore_reference", "restore_named", "multi_update_keep", "negated_cancel_update", "add_preference", "paraphrase_same", "topic_shift", "unresolved_reference", "reject_offer"]
V_LABELS = {"NEW_VALUE", "OLD_VALUE", "KEPT_VALUE", "REFERENCE"}
C_LABELS = {"UPDATE_CUE", "CANCEL_CUE", "KEEP_CUE", "RESTORE_CUE"}


def p(text, label=None, polarity=None):
    return (text, label, polarity)


def utterance(parts):
    s = ""
    values, cues = [], []
    for text, label, polarity in parts:
        start = len(s)
        s += text
        if label:
            record = {"start": start, "end": len(s), "text": text, "label": label}
            if label in C_LABELS:
                record["polarity"] = polarity or "ASSERTED"
                cues.append(record)
            else:
                values.append(record)
    return s, values, cues


def make(kind, split, idx, rng):
    old, new = rng.sample(DESTINATIONS, 2)
    day = rng.choice(DAYS)
    count0, count1 = rng.sample([1, 2, 3, 4, 5, 6], 2)
    ride0, ride1 = rng.sample(RIDES, 2)
    h = []
    trans = []
    links = []
    difficulty = {"replace_explicit":"L1", "replace_implicit":"L1", "keep_named":"L2", "keep_unspecified":"L2", "cancel_intent":"L3", "restore_reference":"L4", "restore_named":"L4", "multi_update_keep":"L5", "negated_cancel_update":"L5"}.get(kind, "NEGATIVE_OR_AMBIGUOUS")

    def item(op, field, before, after, target=0):
        trans.append({"operation": op, "field": field, "before": before, "after": after, "target_turn_index": target})

    if kind == "replace_explicit":
        h = [f"I want to travel to {old}."]
        forms = {
          "train": [p("Please "),p("replace","UPDATE_CUE"),p(" "),p(old,"OLD_VALUE"),p(" with "),p(new,"NEW_VALUE"),p(".")],
          "dev": [p("Could you "),p("swap","UPDATE_CUE"),p(" "),p(old,"OLD_VALUE"),p(" for "),p(new,"NEW_VALUE"),p("?")],
          "challenge": [p(old,"OLD_VALUE"),p(" isn't right anymore; "),p("use","UPDATE_CUE"),p(" "),p(new,"NEW_VALUE"),p(" instead.")]}
        item("UPDATE", "destination",old,new)
    elif kind == "replace_implicit":
        h = [f"Book my trip to {old}."]
        forms = {
          "train":[p("Actually","UPDATE_CUE"),p(", the destination should be "),p(new,"NEW_VALUE"),p(".")],
          "dev":[p("Make","UPDATE_CUE"),p(" the destination "),p(new,"NEW_VALUE"),p(" now.")],
          "challenge":[p("I've changed my mind","UPDATE_CUE"),p(" — let's go to "),p(new,"NEW_VALUE"),p(".")]}
        item("UPDATE","destination",old,new)
    elif kind == "keep_named":
        h = [f"Travel to {old} on {day}."]
        forms = {
          "train":[p("Change","UPDATE_CUE"),p(" the city to "),p(new,"NEW_VALUE"),p(", but "),p("keep","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")],
          "dev":[p("Switch","UPDATE_CUE"),p(" to "),p(new,"NEW_VALUE"),p(" and "),p("retain","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")],
          "challenge":[p("Destination: "),p(new,"NEW_VALUE"),p(". "),p("Don't change","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p("; "),p("update","UPDATE_CUE"),p(" only the city.")]}
        item("UPDATE","destination",old,new);item("KEEP","date",day,day)
    elif kind == "keep_unspecified":
        h = [f"Go to {old} on {day}."]
        forms = {
          "train":[p("Change","UPDATE_CUE"),p(" the destination to "),p(new,"NEW_VALUE"),p(", but "),p("leave","KEEP_CUE"),p(" the date as it is.")],
          "dev":[p("Switch","UPDATE_CUE"),p(" my city to "),p(new,"NEW_VALUE"),p("; "),p("preserve","KEEP_CUE"),p(" the previous date.")],
          "challenge":[p("Only the city should "),p("change","UPDATE_CUE"),p(" to "),p(new,"NEW_VALUE"),p(". Everything else "),p("stays","KEEP_CUE"),p(".")]}
        item("UPDATE","destination",old,new);item("KEEP","date",day,day)
    elif kind == "cancel_intent":
        h = [f"Please book my trip to {old} for {day}."]
        forms = {
          "train":[p("Cancel","CANCEL_CUE"),p(" that booking request.")],
          "dev":[p("Please "),p("drop","CANCEL_CUE"),p(" the reservation I asked for.")],
          "challenge":[p("I no longer want","CANCEL_CUE"),p(" that trip reserved.")]}
        item("CANCEL_INTENT","booking_intent","ACTIVE","CANCELLED")
    elif kind == "restore_reference":
        h = [f"My destination is {old}.", "Okay.", f"Actually, let's go to {new} instead.", "Understood."]
        forms = {
          "train":[p("Go back to","RESTORE_CUE"),p(" "),p("my first destination","REFERENCE"),p(".")],
          "dev":[p("Restore","RESTORE_CUE"),p(" "),p("the original city","REFERENCE"),p(" I mentioned.")],
          "challenge":[p("Take us back to","RESTORE_CUE"),p(" "),p("the place from my opening message","REFERENCE"),p(".")]}
        item("RESTORE","destination",new,old)
        links = [{"role":"restored_reference","target_turn_index":0,"resolved_value":old}]
    elif kind == "restore_named":
        h = [f"I initially chose {old}.", "Noted.", f"Change that to {new}.", "Okay."]
        forms = {
          "train":[p("Go back to","RESTORE_CUE"),p(" "),p(old,"NEW_VALUE"),p(" for the destination.")],
          "dev":[p("Bring back","RESTORE_CUE"),p(" "),p(old,"NEW_VALUE"),p(" as my choice.")],
          "challenge":[p("I want the original destination again: "),p(old,"NEW_VALUE"),p(". "),p("Reinstate","RESTORE_CUE"),p(" it.")]}
        item("RESTORE","destination",new,old)
        links = [{"role":"restored_value","target_turn_index":0,"resolved_value":old}]
    elif kind == "multi_update_keep":
        h = [f"Book a {ride0} ride for {count0} people to {old} on {day}."]
        forms = {
          "train":[p("Change","UPDATE_CUE"),p(" the ride to "),p(ride1,"NEW_VALUE"),p(" for "),p(str(count1),"NEW_VALUE"),p(" people, and "),p("keep","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")],
          "dev":[p("Make","UPDATE_CUE"),p(" it a "),p(ride1,"NEW_VALUE"),p(" ride for "),p(str(count1),"NEW_VALUE"),p(" passengers; "),p("retain","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")],
          "challenge":[p("The ride should now be "),p(ride1,"NEW_VALUE"),p(" and the party size "),p(str(count1),"NEW_VALUE"),p("; "),p("don't touch","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(". "),p("Revise","UPDATE_CUE"),p(" those two details.")]}
        item("UPDATE","ride_type",ride0,ride1);item("UPDATE","passengers",str(count0),str(count1));item("KEEP","date",day,day)
    elif kind == "negated_cancel_update":
        h = [f"Book a ride to {old} on {day}."]
        forms = {
          "train":[p("Don't cancel","CANCEL_CUE","NEGATED"),p(" my booking; just "),p("change","UPDATE_CUE"),p(" the destination to "),p(new,"NEW_VALUE"),p(".")],
          "dev":[p("Do not cancel","CANCEL_CUE","NEGATED"),p(" the request. "),p("Switch","UPDATE_CUE"),p(" the city to "),p(new,"NEW_VALUE"),p(".")],
          "challenge":[p("Cancellation isn't what I want. "),p("Update","UPDATE_CUE"),p(" the destination to "),p(new,"NEW_VALUE"),p("; "),p("don't cancel","CANCEL_CUE","NEGATED"),p(" anything.")]}
        item("UPDATE","destination",old,new)
    elif kind == "add_preference":
        h = [f"Find a place to eat in {old} on {day}."]
        forms = {
          "train":[p("Also show me restaurants with "),p("outdoor seating","NEW_VALUE"),p(".")],
          "dev":[p("I'd also like "),p("vegetarian options","NEW_VALUE"),p(".")],
          "challenge":[p("One more requirement: "),p("quiet atmosphere","NEW_VALUE"),p(".")]}
        extra = {"train":"outdoor seating", "dev":"vegetarian options", "challenge":"quiet atmosphere"}[split]
        item("ADD","new_preference",None,extra)
    elif kind == "paraphrase_same":
        h = [f"I want the appointment in {old} on {day} at 6 pm."]
        forms = {
          "train":[p("Six in the evening works for me.")],
          "dev":[p("Yes, that 18:00 slot is fine.")],
          "challenge":[p("That evening slot at six still works.")]}
        # Semantically equivalent paraphrase: do not relabel a revision.
    elif kind == "topic_shift":
        h = [f"I'm comparing hotels in {old} for {day}."]
        forms = {
          "train":[p("Now I'd like to see weather information.")],
          "dev":[p("Can we look up the forecast next?")],
          "challenge":[p("Let's talk about weekend temperatures.")]}
    elif kind == "unresolved_reference":
        h = [f"The first option is {old}.", "Okay.", f"The second option is {new}.", "Both are available."]
        forms = {
          "train":[p("Use "),p("that one","REFERENCE"),p(" after all.")],
          "dev":[p("I'd prefer "),p("the one we discussed","REFERENCE"),p(".")],
          "challenge":[p("Select "),p("the one we mentioned","REFERENCE"),p("; I can't remember which.")]}
        # Do not claim an unambiguously resolvable reference.
        item("UNRESOLVED","destination",None,None)
    elif kind == "reject_offer":
        h = [f"Would you like me to reserve the {day} appointment in {old}?"]
        forms = {
          "train":[p("No thanks, just show me the available times.")],
          "dev":[p("Not yet. I'd like to compare the options first.")],
          "challenge":[p("I haven't decided; please list the alternatives.")]}
    else:
        raise ValueError(kind)

    # Lexical alternatives within the training partition, kept disjoint from dev/challenge.
    # These are still synthetic templates, not independent natural-language data.
    TRAIN_ALTERNATIVES = {
      "replace_explicit": [
        [p("Kindly "),p("change","UPDATE_CUE"),p(" "),p(old,"OLD_VALUE"),p(" into "),p(new,"NEW_VALUE"),p(".")],
        [p("For the destination, "),p("switch","UPDATE_CUE"),p(" from "),p(old,"OLD_VALUE"),p(" to "),p(new,"NEW_VALUE"),p(".")]],
      "replace_implicit": [
        [p("Sorry, "),p("I meant","UPDATE_CUE"),p(" "),p(new,"NEW_VALUE"),p(" as the destination.")],
        [p("On second thought","UPDATE_CUE"),p(", let's make it "),p(new,"NEW_VALUE"),p(".")]],
      "keep_named": [
        [p("Please "),p("update","UPDATE_CUE"),p(" the destination to "),p(new,"NEW_VALUE"),p("; "),p("don't alter","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")],
        [p("I prefer "),p(new,"NEW_VALUE"),p(" now. "),p("Change","UPDATE_CUE"),p(" the city but "),p("keep","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")]],
      "keep_unspecified": [
        [p("Make","UPDATE_CUE"),p(" the city "),p(new,"NEW_VALUE"),p("; the date must "),p("stay","KEEP_CUE"),p(" the same.")],
        [p("Only "),p("adjust","UPDATE_CUE"),p(" the destination to "),p(new,"NEW_VALUE"),p(" and "),p("keep","KEEP_CUE"),p(" everything else.")]],
      "cancel_intent": [
        [p("I need to "),p("cancel","CANCEL_CUE"),p(" that booking.")],
        [p("Please "),p("withdraw","CANCEL_CUE"),p(" my reservation request.")]],
      "restore_reference": [
        [p("Please "),p("revert","RESTORE_CUE"),p(" to "),p("my original choice","REFERENCE"),p(".")],
        [p("Can we "),p("return to","RESTORE_CUE"),p(" "),p("the city from my first message","REFERENCE"),p("?")]],
      "restore_named": [
        [p("Please "),p("reinstate","RESTORE_CUE"),p(" "),p(old,"NEW_VALUE"),p(" as the destination.")],
        [p("Let's "),p("restore","RESTORE_CUE"),p(" "),p(old,"NEW_VALUE"),p(" from before.")]],
      "multi_update_keep": [
        [p("Please "),p("update","UPDATE_CUE"),p(" the type to "),p(ride1,"NEW_VALUE"),p(" and group size to "),p(str(count1),"NEW_VALUE"),p(". "),p("Keep","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")],
        [p("I want "),p(ride1,"NEW_VALUE"),p(" for "),p(str(count1),"NEW_VALUE"),p(" passengers; "),p("change","UPDATE_CUE"),p(" those details, but "),p("retain","KEEP_CUE"),p(" "),p(day,"KEPT_VALUE"),p(".")]],
      "negated_cancel_update": [
        [p("Please "),p("don't cancel","CANCEL_CUE","NEGATED"),p(" it. "),p("Update","UPDATE_CUE"),p(" the city to "),p(new,"NEW_VALUE"),p(".")],
        [p("I am "),p("not cancelling","CANCEL_CUE","NEGATED"),p(" this booking; "),p("change","UPDATE_CUE"),p(" its destination to "),p(new,"NEW_VALUE"),p(".")]],
      "add_preference": [
        [p("Could you include places offering "),p("outdoor seating","NEW_VALUE"),p(" as well?")],
        [p("One additional filter is "),p("outdoor seating","NEW_VALUE"),p(".")]],
      "paraphrase_same": [
        [p("Okay, I can do six o'clock in the evening.")],
        [p("That six pm appointment is good.")]],
      "topic_shift": [
        [p("Can you tell me the temperature forecast now?")],
        [p("Could you also show the forecast?")]],
      "unresolved_reference": [
        [p("Go with "),p("that option","REFERENCE"),p(".")],
        [p("I want "),p("the one I mentioned","REFERENCE"),p(", if you recall.")]],
      "reject_offer": [
        [p("I haven't agreed to reserve anything yet.")],
        [p("Could you list the available times before I decide?")]],
    }
    if split == "train":
        forms["train"] = rng.choice([forms["train"]] + TRAIN_ALTERNATIVES[kind])

    current, value_spans, cue_spans = utterance(forms[split])
    if split == "challenge" and kind in ("paraphrase_same", "topic_shift", "reject_offer"):
        pass
    history = [{"turn_index": j, "speaker": "USER" if j%2==0 else "SYSTEM", "utterance": v} for j, v in enumerate(h)]
    record = {
      "id": f"SYN-{split.upper()}-{kind}-{idx:03d}",
      "dialogue_family_id": f"syn-{split}-{kind}-{idx:03d}",
      "source": {"dataset":"SYNTHETIC_COMPOSITION", "split":f"synthetic_{split}", "dialogue_id":f"syn-{split}-{kind}-{idx:03d}","turn_index":len(history),"service":"synthetic_booking","generator":"scripts/build_synthetic_bootstrap.py","recipe_id":kind,"template_family":f"{kind}/{split}"},
      "history":history, "current_user_utterance":current,
      "value_spans":value_spans,"cue_spans":cue_spans,"transitions":trans,"links":links,"difficulty":difficulty,
      "annotation":{"status":"SYNTHETIC_PROGRAMMATIC","method":"deterministic_composition","reviewers":[],"guideline_version":"synthetic_contract_v0.7","is_gold":False},
      "disclosure":"Machine-generated synthetic example, not SGD and not human gold. Academic test prohibited."
    }
    return record


def validate_record(r):
    s = r["current_user_utterance"]
    assert r["source"]["dataset"]=="SYNTHETIC_COMPOSITION"
    assert r["annotation"]["is_gold"] is False
    assert all(t["turn_index"] < r["source"]["turn_index"] for t in r["history"])
    for key, allowed in (("value_spans",V_LABELS),("cue_spans",C_LABELS)):
        positions=[]
        for sp in r[key]:
            assert sp["label"] in allowed
            assert 0 <= sp["start"] < sp["end"] <= len(s)
            assert s[sp["start"]:sp["end"]]==sp["text"]
            positions.append((sp["start"],sp["end"]))
            if key=="cue_spans":assert sp["polarity"] in {"ASSERTED","NEGATED","UNCERTAIN"}
        positions.sort()
        assert all(a[1]<=b[0] for a,b in zip(positions,positions[1:]))
    for link in r["links"]:
        assert 0 <= link["target_turn_index"] < r["source"]["turn_index"]
        if link.get("resolved_value"):
            assert link["resolved_value"] in r["history"][link["target_turn_index"]]["utterance"]
    for tr in r["transitions"]:
        assert tr["operation"] in {"ADD","UPDATE","KEEP","DELETE","RESTORE","CANCEL_INTENT","UNRESOLVED"}
    return True


def generate(seed=20261028, counts=None):
    counts = counts or {"train":36,"dev":9,"challenge":9}
    rng=random.Random(seed)
    result={}
    seen=set()
    for split in ("train","dev","challenge"):
        records=[]
        for category in CATEGORIES:
            produced=0; attempts=0
            while produced<counts[split]:
                attempts+=1
                if attempts>5000: raise RuntimeError(f"Cannot generate enough unique examples: {category}/{split}")
                record=make(category,split,produced,rng)
                sig=(record["current_user_utterance"], tuple(x["utterance"] for x in record["history"]))
                if sig in seen:continue
                seen.add(sig)
                validate_record(record)
                records.append(record);produced+=1
        rng.shuffle(records)
        result[split]=records
    return result


def write_data(out, seed):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result=generate(seed)
    counts={}; support={}; nchar={}
    all_templates={}
    for split,records in result.items():
        path=out / f"synthetic_{split}.jsonl"
        path.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in records),encoding="utf-8")
        c=collections.Counter(s["label"] for r in records for k in ("value_spans","cue_spans") for s in r[k])
        counts[split]=len(records);support[split]=dict(sorted(c.items()))
        nchar[split]=sum(len(r["current_user_utterance"]) for r in records)
        all_templates[split]=sorted({r["source"]["template_family"] for r in records})
    assert all(not (set(all_templates[a])&set(all_templates[b])) for a in result for b in result if a!=b)
    manifest={"dataset_name":"OVERRIDE_SYNTHETIC_BOOTSTRAP", "version":"v0.7","seed":seed, "counts":counts,"span_support":support,"characters":nchar,"held_out_templates":True,"academic_gold":False,"reviewer_agreement_available":False,"intended_use":"TRAIN/DEV bootstrap and engineering regressions; synthetic_challenge for sanity checks only; NOT independent academic test or human gold", "upstream_data_used":"none in generator", "files_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.jsonl'))}}
    (out/"generation_manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    return manifest


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='data/synthetic_bootstrap')
    ap.add_argument('--seed',type=int,default=20261028)
    a=ap.parse_args()
    print(json.dumps(write_data(a.out,a.seed),indent=2))

if __name__=='__main__':main()
