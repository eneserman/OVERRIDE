#!/usr/bin/env python3
"""Strict validator for *human* OVERRIDE annotation JSONL; does not create gold.

All offsets are Python character offsets [start, end) against unmodified
current_user_utterance. The script never modifies source records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VALUE_LABELS = frozenset({'NEW_VALUE', 'OLD_VALUE', 'KEPT_VALUE', 'REFERENCE'})
CUE_LABELS = frozenset({'UPDATE_CUE', 'CANCEL_CUE', 'KEEP_CUE', 'RESTORE_CUE'})
GOLD_STATUS = 'ADJUDICATED'


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    rows = []
    with path.open('r', encoding='utf-8') as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f'{path}:{line_no}: invalid JSON: {error}') from error
            if not isinstance(item, dict):
                raise ValueError(f'{path}:{line_no}: each record must be a JSON object')
            rows.append(item)
    return rows


def validate_record(row: dict[str, Any], require_gold: bool = False) -> list[str]:
    errs: list[str] = []
    rid = row.get('id')
    if not isinstance(rid, str) or not rid.strip():
        errs.append('id is required and must be a non-empty string')
    utterance = row.get('current_user_utterance')
    if not isinstance(utterance, str):
        errs.append('current_user_utterance must be a string')
        utterance = ''
    source = row.get('source')
    if not isinstance(source, dict):
        errs.append('source must be an object')
        source = {}
    turn_index = source.get('turn_index')
    if type(turn_index) is not int or turn_index < 0:
        errs.append('source.turn_index must be a nonnegative integer')
    if not isinstance(source.get('dialogue_id'), str) or not source.get('dialogue_id'):
        errs.append('source.dialogue_id must be a nonempty string')
    if not isinstance(source.get('service'), str) or not source.get('service'):
        errs.append('source.service must be a nonempty string')
    history = row.get('history')
    if not isinstance(history, list):
        errs.append('history must be a list')
    else:
        seen_indices = set()
        last_index = -1
        for i, msg in enumerate(history):
            if not isinstance(msg, dict) or msg.get('speaker') not in ('USER','SYSTEM') or not isinstance(msg.get('utterance'), str):
                errs.append(f'history[{i}]: expected speaker USER/SYSTEM and string utterance')
                continue
            hist_index = msg.get('turn_index')
            if hist_index is not None:
                if type(hist_index) is not int or hist_index < 0 or (type(turn_index) is int and hist_index >= turn_index):
                    errs.append(f'history[{i}]: future/invalid turn_index')
                elif hist_index in seen_indices or hist_index <= last_index:
                    errs.append(f'history[{i}]: duplicate/out-of-order turn_index')
                else:
                    seen_indices.add(hist_index)
                    last_index = hist_index
        if any(isinstance(msg,dict) and 'turn_index' in msg for msg in history) and any(isinstance(msg,dict) and 'turn_index' not in msg for msg in history):
            errs.append('history turn_index must be provided for all turns or none')
    for key, vocabulary in (('value_spans', VALUE_LABELS), ('cue_spans', CUE_LABELS)):
        spans = row.get(key)
        if spans is None and not require_gold:
            continue  # blind, not-yet-annotated packets may have null spans
        if not isinstance(spans, list):
            errs.append(f'{key} must be a list' + (' for gold' if require_gold else ' or null for blind packets'))
            continue
        intervals = []
        for i, s in enumerate(spans):
            if not isinstance(s, dict):
                errs.append(f'{key}[{i}]: span must be an object')
                continue
            start, end, label = s.get('start'), s.get('end'), s.get('label')
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(utterance):
                errs.append(f'{key}[{i}]: invalid half-open offsets')
                continue
            if label not in vocabulary:
                errs.append(f'{key}[{i}]: label {label!r} not in {sorted(vocabulary)}')
            if s.get('text') != utterance[start:end]:
                errs.append(f'{key}[{i}]: text differs from original utterance slice')
            intervals.append((start,end,i))
        intervals.sort()
        for preceding, following in zip(intervals, intervals[1:]):
            if preceding[1] > following[0]:
                errs.append(f'{key}: within-layer overlap between spans {preceding[2]} and {following[2]}')
    if require_gold:
        a = row.get('annotation')
        if not isinstance(a, dict) or a.get('status') != GOLD_STATUS:
            errs.append('gold status must be annotation.status=ADJUDICATED')
        else:
            if not isinstance(a.get('guideline_version'), str) or not a['guideline_version'].strip():
                errs.append('gold missing annotation.guideline_version')
            reviewers = a.get('reviewers')
            if not isinstance(reviewers, list) or len(reviewers) < 2 or any(not isinstance(x,str) or not x.strip() for x in reviewers) or len(set(reviewers)) != len(reviewers):
                errs.append('gold requires at least two distinct reviewer identifiers')
            if not isinstance(a.get('adjudication_log_id'), str) or not a['adjudication_log_id'].strip():
                errs.append('gold requires an adjudication_log_id (actual evidence required separately)')
        if source.get('dataset') != 'SGD' or source.get('split') != 'train':
            errs.append('this custom gold contract only accepts reviewed official SGD train source')
        family = row.get('dialogue_family_id')
        if not isinstance(family, str) or not family.strip():
            errs.append('gold requires nonempty dialogue_family_id')
        elif family != source.get('dialogue_id'):
            errs.append('dialogue_family_id must equal SGD source.dialogue_id unless audited family grouping is explicitly implemented')
    return errs


def validate_rows(rows: list[dict[str, Any]], require_gold: bool = False) -> dict[str, Any]:
    all_errors = []
    seen = set()
    for i, row in enumerate(rows):
        rid = row.get('id')
        rid_key = rid if isinstance(rid, str) else repr(rid)
        if rid_key in seen:
            all_errors.append(f'row {i}: duplicate example id {rid!r}')
        seen.add(rid_key)
        all_errors.extend(f'row {i} id={rid!r}: {err}' for err in validate_record(row, require_gold))
    return {'records':len(rows),'status':'PASS' if not all_errors and rows else 'FAIL', 'errors':all_errors}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--require-gold', action='store_true')
    ap.add_argument('--report', type=Path, help='optional JSON result path')
    args = ap.parse_args()
    report = validate_rows(read_jsonl(args.input), args.require_gold)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'], 'records':report['records'], 'errors':report['errors'][:12]},indent=2,ensure_ascii=False))
    if report['status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
