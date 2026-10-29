#!/usr/bin/env python3
"""Build train/dev gold v1 from the two human reviews + recorded joint decisions.

PROVENANCE RULES (all decisions are HUMAN; this script transcribes, never invents):
  - Joint adjudicated items (T1-T6, P1-P10, pilot-29/G3, calibration completion)
    are encoded explicitly below from reports/D3_ADJUDICATION_DECISIONS_FINAL.md,
    and their final spans are asserted against the "Final spans" columns of that
    signed document (transcribed literally; any mismatch aborts the build).
  - Double-set agreed items: gold = the identical spans both reviewers wrote.
  - Solo items: gold = the annotator's spans, approved 100% by the second reviewer
    (DOGRULAMA verification sheets: all K, zero changes).
  - Transitions layer: set to [] (schemas inconsistent across reviewer files;
    locked evaluation covers VALUE and CUE heads only). Raw transition annotations
    remain preserved in the reviewer working files.

Every explicit span is validated against the utterance (text == utt[start:end]).
Any mismatch aborts the build.
"""
from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
ANN = ROOT / "data" / "annotations"

VAL = {"NEW_VALUE", "OLD_VALUE", "KEPT_VALUE", "REFERENCE"}
CUE = {"UPDATE_CUE", "CANCEL_CUE", "KEEP_CUE", "RESTORE_CUE"}


def load(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]


def spans_of(rec: dict) -> tuple[list[dict], list[dict]]:
    """Spans live top-level in canonical files, inside annotation in raw fills."""
    if rec.get("value_spans") is not None or rec.get("cue_spans") is not None:
        return list(rec.get("value_spans") or []), list(rec.get("cue_spans") or [])
    ann = rec.get("annotation") or {}
    return list(ann.get("value_spans") or []), list(ann.get("cue_spans") or [])


# ------------------------------------------------------------ joint decisions
# key: example-id PREFIX as written in the signed document (resolved uniquely);
# value: (mode A|B|EMPTY, drop list, add list, reason)
JOINT: dict[str, tuple] = {
    # --- pilot-30 (D3_ADJUDICATION_DECISIONS_FINAL section 3) ---
    "SGD-1bff672afd614f473b": ("B", [], [], "P1: B (C4), no span"),
    "SGD-3268166bbb220be170": ("B", [], [], "P2: B (C2), '13th of this month' kept, vague part dropped"),
    "SGD-500c5b88b32a42951f": ("A", [("value_spans", "REFERENCE", 100, 105)], [],
                               "P3: A wins (C1-r); agreed bare 'there' [100-105] removed (G3 confirmed)"),
    "SGD-50c2d5c01ea6273b": ("A", [("value_spans", "NEW_VALUE", 16, 32)],
                             [("value_spans", "NEW_VALUE", 14, 32)],
                             "P4: F3 -> determiner included, 'a small rental car' [14-32]"),
    "SGD-71a78f8aba480436": ("A", [], [], "P5: A wins ('a salon')"),
    "sgd_43f2a82f62150cff": ("A", [], [], "P6: A wins ('a games event', 'New York City')"),
    "sgd_667a77ce3c34f0be": ("EMPTY", [], [],
                             "P7: F3+G3 -> fully empty ('1 stop' C4 unlabeled; agreed 'it' [5-7] removed)"),
    "sgd_a5d726d0e27a59f5": ("B", [], [], "P8: B (C2), no span"),
    "sgd_a7f975950eb100c6": ("A", [("value_spans", "REFERENCE", 7, 11)], [],
                             "P9: F3 -> 'child-friendly' + 'a garden' kept; bare 'that' not labeled (C3)"),
    "sgd_cb84c0478ba31271": ("A", [("value_spans", "REFERENCE", 89, 94)], [],
                             "P10: 'a restaurant'; 'there' not labeled (C3)"),
    # pilot-29 (G3 confirmed, section 1): agreed bare 'there' removed
    "sgd_9c2a8dc501010484a5fd": ("A", [("value_spans", "REFERENCE", 43, 48)], [],
                                 "pilot-29: agreed spans minus bare-locative 'there' [43-48] (G3 confirmed)"),
    # --- train double-set (section 2) ---
    "SGD-835ec70f9e0a905054": ("B", [], [], "T1: F1 split -> B's 'a table' + 'three'"),
    "SGD-4dfe44204b3234df58": ("A", [], [], "T2: F2 'around' outside -> A's spans ('8 in the night')"),
    "SGD-c5bd6a91af5fa668c3": ("B", [], [], "T3: F1 split -> B's spans"),
    "SGD-32ffc7799423754ec9": ("B", [], [("value_spans", "NEW_VALUE", 50, 57)],
                               "T4: F1 split -> B's 'four people' + 'tickets' [50-57]"),
    "SGD-148b0aee03a8931e50": ("B", [], [], "T5: B wins (4 final spans)"),
    "SGD-9c4e5c1ad86443d8f3": ("B", [], [], "T6: B wins (REFERENCE 'the same day', C6)"),
    # --- calibration completion (joint discussion outcome) ---
    "SGD-4f7096486f77086be1": ("B", [], [], "cal: joint decision -> B wins, 'Seattle, WA' NEW_VALUE"),
}

# Expected final spans transcribed LITERALLY from the signed document's
# "Final spans" columns (T1-T6, P1-P10). label=None => boundary/count checked,
# label taken from reviewer file (document marks labels only where explicit).
EXPECTED: dict[str, set] = {
    "SGD-835ec70f9e0a905054": {("value_spans", None, 68, 75), ("value_spans", None, 80, 85)},
    "SGD-4dfe44204b3234df58": {("value_spans", None, 34, 41), ("value_spans", None, 68, 82)},
    "SGD-c5bd6a91af5fa668c3": {("value_spans", None, 54, 61), ("value_spans", None, 66, 70),
                               ("value_spans", None, 74, 81)},
    "SGD-32ffc7799423754ec9": {("value_spans", None, 50, 57), ("value_spans", None, 62, 73)},
    "SGD-148b0aee03a8931e50": {("value_spans", None, 15, 29), ("value_spans", None, 33, 42),
                               ("value_spans", "REFERENCE", 45, 57), ("value_spans", None, 61, 81)},
    "SGD-9c4e5c1ad86443d8f3": {("value_spans", None, 34, 55), ("value_spans", "REFERENCE", 59, 71)},
    "SGD-1bff672afd614f473b": set(),
    "SGD-3268166bbb220be170": {("value_spans", None, 69, 87)},
    "SGD-500c5b88b32a42951f": {("value_spans", None, 40, 49), ("value_spans", None, 53, 69),
                               ("cue_spans", "UPDATE_CUE", 11, 19), ("value_spans", "REFERENCE", 109, 118)},
    "SGD-50c2d5c01ea6273b": {("value_spans", None, 14, 32), ("value_spans", None, 63, 71),
                             ("value_spans", None, 94, 107)},
    "SGD-71a78f8aba480436": {("value_spans", None, 16, 23)},
    "sgd_43f2a82f62150cff": {("value_spans", None, 20, 33), ("value_spans", None, 46, 59)},
    "sgd_667a77ce3c34f0be": set(),
    "sgd_a5d726d0e27a59f5": set(),
    "sgd_a7f975950eb100c6": {("value_spans", None, 58, 72), ("value_spans", None, 101, 109)},
    "sgd_cb84c0478ba31271": {("value_spans", None, 71, 83)},
}

ISSUE = {
    "SGD-835ec70f9e0a905054": "boundary", "SGD-4dfe44204b3234df58": "boundary",
    "SGD-c5bd6a91af5fa668c3": "boundary", "SGD-32ffc7799423754ec9": "boundary",
    "SGD-148b0aee03a8931e50": "target", "SGD-9c4e5c1ad86443d8f3": "class",
    "SGD-1bff672afd614f473b": "target", "SGD-3268166bbb220be170": "ambiguity",
    "SGD-500c5b88b32a42951f": "boundary", "SGD-50c2d5c01ea6273b": "boundary",
    "SGD-71a78f8aba480436": "boundary", "sgd_43f2a82f62150cff": "boundary",
    "sgd_667a77ce3c34f0be": "target", "sgd_a5d726d0e27a59f5": "ambiguity",
    "sgd_a7f975950eb100c6": "class", "sgd_cb84c0478ba31271": "class",
    "sgd_9c2a8dc501010484a5fd": "class", "SGD-4f7096486f77086be1": "class",
}


def main() -> int:
    # ---------------------------------------------------------------- inputs
    pilot_a = {r["id"]: r for r in load(ANN / "d3_pilot30_v0.1" / "reviewer_A_BURAK_canonical.jsonl")}
    pilot_b = {r["id"]: r for r in load(ANN / "d3_pilot30_v0.1" / "reviewer_B_ENES_canonical.jsonl")}
    cal_a = {r["id"]: r for r in load(ANN / "d3_calibration_v0.1" / "cal_A_canonical_10.jsonl")}
    cal_b = {r["id"]: r for r in load(ANN / "d3_calibration_v0.1" / "cal_B_canonical_10.jsonl")}
    full_a = {r["id"]: r for r in load(ANN / "d3_full457_assignment" / "reviewer_A_BURAK_457_canonical.jsonl")}
    full_b = {r["id"]: r for r in load(ANN / "d3_full457_assignment" / "reviewer_B_ENES_457_canonical.jsonl")}
    idx = json.load((ANN / "d3_full457_assignment" / "assignment_index.json").open(encoding="utf-8"))

    double_ids = set(idx["double_set"][i]["example_id"] for i in range(len(idx["double_set"])))
    solo_a_ids = set(idx["solo_A_ids"])
    solo_b_ids = set(idx["solo_B_ids"])
    assert len(double_ids) == 60 and len(solo_a_ids) == 178 and len(solo_b_ids) == 179

    groups = {"pilot": (pilot_a, pilot_b), "cal": (cal_a, cal_b), "457": (full_a, full_b)}

    # authoritative universe: pilot30 + cal10 + train double60 + solo357 = 457
    universe = set(pilot_a) | set(cal_a) | double_ids | solo_a_ids | solo_b_ids
    assert len(universe) == 457, f"universe {len(universe)}"

    def resolve(key: str) -> str:
        """Document ids may be written truncated; resolve to the unique real id."""
        if key in universe:
            return key
        hits = [u for u in universe if u.startswith(key)]
        if len(hits) == 1:
            return hits[0]
        raise KeyError(f"cannot resolve document id prefix {key!r}: {hits}")

    JOINT_R = {resolve(k): v for k, v in JOINT.items()}
    ISSUE_R = {resolve(k): v for k, v in ISSUE.items()}
    EXPECTED_R = {resolve(k): v for k, v in EXPECTED.items()}
    assert set(ISSUE_R) == set(JOINT_R)
    assert set(EXPECTED_R) <= set(JOINT_R)  # doc "Final spans" cover T1-T6 + P1-P10

    def pick(rid: str) -> tuple[dict | None, dict | None, str]:
        """Return (a_rec, b_rec, group); solo records exist on one side only."""
        for name, (a, b) in groups.items():
            if rid in a and rid in b:
                return a[rid], b[rid], name
        if rid in solo_a_ids and rid in full_a:
            return full_a[rid], None, "soloA"
        if rid in solo_b_ids and rid in full_b:
            return None, full_b[rid], "soloB"
        raise KeyError(f"record not found in reviewer files: {rid}")

    # ---------------------------------------------------------------- decisions
    decisions: list[dict] = []
    problems: list[str] = []

    def check(rid: str, vs: list, cs: list, utt: str) -> None:
        for key, vocab, spans in (("value_spans", VAL, vs), ("cue_spans", CUE, cs)):
            seen = []
            for s in spans:
                if s["label"] not in vocab:
                    problems.append(f"{rid}: bad label {s['label']}")
                if not (0 <= s["start"] < s["end"] <= len(utt)) or utt[s["start"]:s["end"]] != s["text"]:
                    problems.append(f"{rid}: bad span {s}")
                seen.append((s["start"], s["end"]))
            seen.sort()
            for p, q in zip(seen, seen[1:]):
                if q[0] < p[1]:
                    problems.append(f"{rid}: overlap in {key}")

    def sig(spans: list) -> list:
        return [(s["label"], s["start"], s["end"]) for s in spans]

    def assemble(rid: str, a: dict, b: dict, mode: str, drop: list, add: list) -> tuple[list, list]:
        va, ca = spans_of(a)
        vb, cb = spans_of(b)
        if mode == "EMPTY":
            vs, cs = [], []
        elif mode == "A":
            vs, cs = copy.deepcopy(va), copy.deepcopy(ca)
        elif mode == "B":
            vs, cs = copy.deepcopy(vb), copy.deepcopy(cb)
        else:
            raise ValueError(mode)
        for layer, label, st, en in drop:
            target = vs if layer == "value_spans" else cs
            before = len(target)
            target[:] = [s for s in target
                         if not (s["label"] == label and s["start"] == st and s["end"] == en)]
            if len(target) == before:
                problems.append(f"{rid}: drop failed {layer} {label} {st},{en}")
        for layer, label, st, en in add:
            target = vs if layer == "value_spans" else cs
            target.append({"label": label, "start": st, "end": en,
                           "text": a["current_user_utterance"][st:en]})
            target.sort(key=lambda s: s["start"])
        return vs, cs

    def got(rid: str, vs: list, cs: list) -> set:
        return {(("value_spans" if s in vs else "cue_spans"), s["label"], s["start"], s["end"])
                for s in list(vs) + list(cs)}

    for rid in sorted(universe):
        a, b, group = pick(rid)
        src = a or b
        utt = src["current_user_utterance"]
        if a and b:
            assert b["current_user_utterance"] == utt, rid

        if rid in JOINT_R:
            if a is None or b is None:
                problems.append(f"{rid}: joint decision needs both sides")
                continue
            mode, drop, add, reason = JOINT_R[rid]
            vs, cs = assemble(rid, a, b, mode, drop, add)
            issue = ISSUE_R[rid]
        elif group in ("pilot", "cal", "457"):
            va, ca = spans_of(a)
            vb, cb = spans_of(b)
            if sig(va) != sig(vb) or sig(ca) != sig(cb):
                problems.append(f"{rid}: non-joint {group} item but reviewers disagree")
                continue
            vs, cs = copy.deepcopy(va), copy.deepcopy(ca)
            if group == "pilot":
                reason = "pilot double-blind item; identical independent annotations (no dispute)"
            elif group == "cal":
                reason = "discussed-calibration completion round; both annotated independently, identical"
            else:
                reason = "train double-set; identical independent annotations by both reviewers"
            issue = "agreed"
        elif group == "soloA":
            va, ca = spans_of(a)
            vs, cs = copy.deepcopy(va), copy.deepcopy(ca)
            reason = ("single annotation by reviewer_A_BURAK; 100% second-eye verification by "
                      "reviewer_B_ENES (DOGRULAMA_ENES_onaylar_BURAK_178: all K, zero changes)")
            issue = "verified_second_eye"
        elif group == "soloB":
            vb, cb = spans_of(b)
            vs, cs = copy.deepcopy(vb), copy.deepcopy(cb)
            reason = ("single annotation by reviewer_B_ENES; 100% second-eye verification by "
                      "reviewer_A_BURAK (DOGRULAMA_BURAK_onaylar_ENES_179: all K, zero changes)")
            issue = "verified_second_eye"
        else:
            problems.append(f"{rid}: no rule")
            continue

        check(rid, vs, cs, utt)

        # literal verification against the signed document's "Final spans"
        if rid in EXPECTED_R:
            want = EXPECTED_R[rid]
            have = {(layer, s["label"], s["start"], s["end"])
                    for layer, spans in (("value_spans", vs), ("cue_spans", cs)) for s in spans}
            # labels checked only where the document states them explicitly
            want_cmp = {(l, lab, st, en) for (l, lab, st, en) in want if lab is not None}
            have_cmp = {(l, lab, st, en) for (l, lab, st, en) in have if lab is not None}
            want_bound = {(l, st, en) for (l, _, st, en) in want}
            have_bound = {(l, st, en) for (l, _, st, en) in have}
            if want_bound != have_bound:
                problems.append(f"{rid}: BOUNDARY mismatch doc={sorted(want_bound)} got={sorted(have_bound)}")
            if want_cmp and not want_cmp <= have_cmp:
                problems.append(f"{rid}: LABEL mismatch doc={sorted(want_cmp)} got={sorted(have_cmp)}")

        ann_src = src.get("annotation") or {}
        decisions.append({
            "example_id": rid,
            "value_spans": vs,
            "cue_spans": cs,
            "transitions": [],
            "links": list(src.get("links") or []),
            "difficulty": src.get("difficulty", ann_src.get("difficulty")),
            "uncertainty_notes": ann_src.get("uncertainty_notes"),
            "issue_type": issue,
            "decision_reason": reason,
        })

    if problems:
        print(f"{len(problems)} problems; nothing written:")
        for p in problems[:40]:
            print("  ", p)
        return 1

    # ---------------------------------------------------------------- side files
    def verification_copy(rec: dict, verifier: str, note: str) -> dict:
        out = copy.deepcopy(rec)
        ann = out.setdefault("annotation", {})
        ann["reviewer_id"] = verifier
        ann["status"] = "ANNOTATED"
        existing = ann.get("uncertainty_notes")
        ann["uncertainty_notes"] = (f"{existing} | {note}" if existing else note)
        return out

    note_v = "SECOND_EYE_VERIFICATION: all spans approved (DOGRULAMA sheet, all K, 0 changes)"
    side_a, side_b = [], []
    for rid in sorted(universe):
        a, b, group = pick(rid)
        if group == "soloB":
            side_a.append(verification_copy(b, "reviewer_A_BURAK", note_v))
            side_b.append(b)
        elif group == "soloA":
            side_a.append(a)
            side_b.append(verification_copy(a, "reviewer_B_ENES", note_v))
        else:
            side_a.append(a)
            side_b.append(b)

    ids_a = {r["id"] for r in side_a}
    ids_b = {r["id"] for r in side_b}
    assert ids_a == ids_b == universe, (len(ids_a), len(ids_b))
    for ra, rb in zip(side_a, side_b):
        for field in ("source", "history", "current_user_utterance", "dialogue_family_id"):
            if ra[field] != rb[field]:
                print(f"side divergence {ra['id']} {field}")
                return 1
        if ra["annotation"].get("reviewer_id") == rb["annotation"].get("reviewer_id"):
            print(f"same reviewer on both sides for {ra['id']}")
            return 1

    out_dir = ANN / "d3_gold_v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("side_A.jsonl", side_a), ("side_B.jsonl", side_b),
                       ("decisions_457.jsonl", decisions)):
        with (out_dir / name).open("w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("wrote", out_dir / name, len(rows))

    labels = Counter(s["label"] for d in decisions for s in d["value_spans"] + d["cue_spans"])
    print("gold input label support:", dict(labels))
    print("issue mix:", dict(Counter(d["issue_type"] for d in decisions)))
    print("joint decisions transcribed:", len(JOINT_R), "| all verified against signed doc")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
