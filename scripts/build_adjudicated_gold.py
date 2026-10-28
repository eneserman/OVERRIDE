#!/usr/bin/env python3
"""Build adjudicated gold from two independent HUMAN reviews plus HUMAN adjudication decisions.

This tool NEVER invents labels. Every final span must come from the adjudicator's
decision file, which is authored by a real human after reviewing both independent
annotations and the disagreement report. Without a decisions file nothing is produced.

Inputs:
  --a / --b        canonical per-reviewer files (output of normalize_review_packet.py)
  --decisions      JSONL, one human decision per example:
                   {"example_id": ..., "value_spans": [...], "cue_spans": [...],
                    "transitions": [...], "links": [...], "difficulty": ...,
                    "uncertainty_notes": ..., "issue_type": "boundary|class|target|polarity|ambiguity",
                    "decision_reason": "..."}
  --adjudicator    real adjudicator identifier
  --log-id         nonempty adjudication log identifier (evidence kept outside repo)
  --allowed-splits train (default) or dev,test for the sealed prospective test gold
  --out            gold JSONL (must not exist)

The output satisfies validate_annotations --require-gold: status ADJUDICATED,
two distinct reviewer ids, adjudication_log_id, SGD provenance. Un-decided
examples are reported and omitted unless --require-all is set (then any
missing decision aborts).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_annotations import read_jsonl, validate_rows, validate_record, VALUE_LABELS, CUE_LABELS


def load_side(path: Path, name: str) -> dict:
    rows = read_jsonl(path)
    res = validate_rows(rows, False)
    if res['status'] != 'PASS':
        raise ValueError(f'{name} file invalid: {res["errors"][:6]}')
    if any(r.get('annotation', {}).get('status') != 'ANNOTATED' for r in rows):
        raise ValueError(f'{name} must contain only ANNOTATED (human-reviewed) records')
    return {r['id']: r for r in rows}


def check_spans(utterance: str, spans, layer_key: str, allowed) -> list[str]:
    errs = []
    if not isinstance(spans, list):
        return [f'{layer_key} must be a list ([] means reviewed negative)']
    seen = []
    for s in spans:
        if not isinstance(s, dict):
            errs.append(f'{layer_key}: span entries must be objects')
            continue
        lab = s.get('label')
        if lab not in allowed:
            errs.append(f'{layer_key}: unknown label {lab!r}')
        st, en = s.get('start'), s.get('end')
        if type(st) is not int or type(en) is not int or not (0 <= st < en <= len(utterance)):
            errs.append(f'{layer_key}: invalid offsets {st!r},{en!r}')
            continue
        if utterance[st:en] != s.get('text'):
            errs.append(f'{layer_key}: text does not equal utterance[{st}:{en}]')
        seen.append((st, en))
    seen.sort()
    for prev, cur in zip(seen, seen[1:]):
        if cur[0] < prev[1]:
            errs.append(f'{layer_key}: overlap between spans')
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description='Merge two human reviews + human adjudication into gold (no invented labels)')
    ap.add_argument('--a', required=True, type=Path)
    ap.add_argument('--b', required=True, type=Path)
    ap.add_argument('--decisions', required=True, type=Path)
    ap.add_argument('--adjudicator', required=True)
    ap.add_argument('--log-id', required=True)
    ap.add_argument('--allowed-splits', default='train')
    ap.add_argument('--require-all', action='store_true', help='abort unless every example has a decision')
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()

    if not args.adjudicator.strip() or not args.log_id.strip():
        print('adjudicator and --log-id must be real nonempty identifiers')
        return 1
    if args.out.exists():
        print(f'refusing to overwrite existing {args.out}')
        return 1

    da = load_side(args.a, 'reviewer A')
    db = load_side(args.b, 'reviewer B')
    if set(da) != set(db):
        print('reviewer files cover different example ids; run annotation_agreement first')
        return 1
    ids_a = {da[k].get('annotation', {}).get('reviewer_id') for k in da}
    ids_b = {db[k].get('annotation', {}).get('reviewer_id') for k in db}
    if ids_a & ids_b:
        print('both files claim the same reviewer_id; independent review not established')
        return 1

    decisions = {}
    for i, line in enumerate(open(args.decisions, encoding='utf-8'), 1):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception as exc:
            print(f'decisions line {i}: invalid JSON {exc}')
            return 1
        rid = d.get('example_id')
        if not isinstance(rid, str) or not rid:
            print(f'decisions line {i}: missing example_id')
            return 1
        if rid in decisions:
            print(f'decisions line {i}: duplicate decision for {rid}')
            return 1
        if rid not in da:
            print(f'decisions line {i}: {rid} not in reviewer files')
            return 1
        decisions[rid] = d

    undecided = sorted(set(da) - set(decisions))
    if undecided and args.require_all:
        print(f'{len(undecided)} examples lack decisions (first: {undecided[:5]}); --require-all set, aborting')
        return 1

    allowed = tuple(s.strip() for s in args.allowed_splits.split(',') if s.strip())
    gold_rows = []
    problems = []
    for rid in sorted(decisions):
        d = decisions[rid]
        ra, rb = da[rid], db[rid]
        for field in ('source', 'history', 'current_user_utterance', 'dialogue_family_id'):
            if ra.get(field) != rb.get(field):
                problems.append(f'{rid}: reviewer files diverge on {field}; not adjudicable')
        utt = ra['current_user_utterance']
        problems += [f'{rid}: {e}' for e in check_spans(utt, d.get('value_spans'), 'value_spans', VALUE_LABELS)]
        problems += [f'{rid}: {e}' for e in check_spans(utt, d.get('cue_spans'), 'cue_spans', CUE_LABELS)]
        row = {
            'id': rid,
            'source': ra['source'],
            'dialogue_family_id': ra['dialogue_family_id'],
            'history': ra['history'],
            'current_user_utterance': utt,
            'value_spans': d.get('value_spans'),
            'cue_spans': d.get('cue_spans'),
            'transitions': d.get('transitions') or [],
            'links': d.get('links') or [],
            'difficulty': d.get('difficulty'),
            'annotation': {
                'status': 'ADJUDICATED',
                'guideline_version': ra['annotation'].get('guideline_version'),
                'reviewers': sorted({ra['annotation'].get('reviewer_id'), rb['annotation'].get('reviewer_id')}),
                'adjudicator': args.adjudicator.strip(),
                'adjudication_log_id': args.log_id.strip(),
                'issue_type': d.get('issue_type'),
                'decision_reason': d.get('decision_reason'),
                'uncertainty_notes': d.get('uncertainty_notes'),
            },
        }
        gold_rows.append(row)

    if problems:
        print('adjudication problems; nothing written:')
        for p in problems[:20]:
            print('  ', p)
        return 1

    report = validate_rows(gold_rows, True, allowed)
    if report['status'] != 'PASS':
        print('gold contract rejected the adjudicated rows; nothing written:')
        for e in report['errors'][:20]:
            print('  ', e)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as fh:
        for row in gold_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(json.dumps({
        'status': 'ADJUDICATED_GOLD_WRITTEN_FROM_HUMAN_DECISIONS',
        'records': len(gold_rows),
        'undecided_omitted': len(undecided),
        'reviewers': sorted(ids_a | ids_b),
        'adjudicator': args.adjudicator.strip(),
        'adjudication_log_id': args.log_id.strip(),
        'allowed_splits': list(allowed),
        'out': str(args.out),
        'note': 'Gold exists only because real humans annotated and adjudicated. Re-run validate_annotations --require-gold to audit independently.',
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
