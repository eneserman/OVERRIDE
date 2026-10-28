#!/usr/bin/env python3
"""Prepare reproducible, UNLABELED human-review queues from official SGD train.

Never infers gold revision labels. Does not modify upstream data. Standard library only.
The private manifest (not annotator packets) contains candidate-mining hints.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import re

from audit_sgd import CUE_PATTERNS, sha256, state_deltas

NEGATED_CANCEL = re.compile(r"\b(?:do\s+not|don't|never|not)\s+cancel\b", re.I)
STRATA = (
    'NEGATED_CANCEL_CUE', 'POSSIBLE_RESTORE', 'POSSIBLE_KEEP',
    'POSSIBLE_CANCEL', 'STATE_CHANGED', 'POSSIBLE_REVISION',
    'STATE_ADD_OR_CLEAR', 'ALIAS_VARIANT', 'NO_CHANGE_CONTROL',
    'FIRST_OBSERVED_CONTROL',
)


def classify(flags: list[str], changes: list[dict], text: str, previously_seen: bool) -> str:
    kinds = {item['kind'] for item in changes}
    if NEGATED_CANCEL.search(text):
        return 'NEGATED_CANCEL_CUE'
    if 'possible_restore_cue' in flags:
        return 'POSSIBLE_RESTORE'
    if 'possible_keep_cue' in flags:
        return 'POSSIBLE_KEEP'
    if 'possible_cancel_cue' in flags:
        return 'POSSIBLE_CANCEL'
    if 'SLOT_CHANGED_CANDIDATE' in kinds:
        return 'STATE_CHANGED'
    if 'possible_revision_cue' in flags:
        return 'POSSIBLE_REVISION'
    if kinds & {'SLOT_ADDED_CANDIDATE', 'SLOT_CLEARED_CANDIDATE'}:
        return 'STATE_ADD_OR_CLEAR'
    if 'ALIAS_OR_STATE_VARIANT_CANDIDATE' in kinds:
        return 'ALIAS_VARIANT'
    return 'NO_CHANGE_CONTROL' if previously_seen else 'FIRST_OBSERVED_CONTROL'


def mine_raw(files: list[Path], context_turns: int) -> tuple[list[dict], dict]:
    """Scan official train records. Extract annotator-visible text and private hints."""
    records: list[dict] = []
    stats: Counter = Counter()
    file_hashes: dict[str, str] = {}
    seen_dids: set[str] = set()
    for file in sorted(files):
        file_hashes[file.name] = sha256(file)
        dialogues = json.loads(file.read_text(encoding='utf-8'))
        if not isinstance(dialogues, list):
            raise ValueError(f'{file}: expected JSON list')
        for d in dialogues:
            did = d.get('dialogue_id')
            if not isinstance(did, str) or not did:
                raise ValueError(f'{file}: dialogue missing string dialogue_id')
            if did in seen_dids:
                raise ValueError(f'Duplicate dialogue ID: {did}')
            seen_dids.add(did)
            stats['dialogues'] += 1
            turns = d.get('turns', [])
            previous_states: dict[str, dict] = {}
            for idx, turn in enumerate(turns):
                if turn.get('speaker') != 'USER':
                    continue
                text = turn.get('utterance')
                if not isinstance(text, str):
                    stats['nontext_user_turns'] += 1
                    continue
                flags = [name for name, p in CUE_PATTERNS.items() if p.search(text)]
                for frame in turn.get('frames', []):
                    service = frame.get('service')
                    state = frame.get('state')
                    if not isinstance(service, str) or not isinstance(state, dict):
                        stats['missing_service_or_state'] += 1
                        continue
                    slot_values = state.get('slot_values')
                    if not isinstance(slot_values, dict):
                        stats['missing_slot_values'] += 1
                        continue
                    had_prior = service in previous_states
                    changes = state_deltas(previous_states[service], slot_values) if had_prior else []
                    stratum = classify(flags, changes, text, had_prior)
                    # No future turns, no current/previous gold state, no candidate hints
                    # in the annotator-visible record.
                    history = [
                        {'turn_index': n, 'speaker': t['speaker'], 'utterance': t['utterance']}
                        for n, t in enumerate(turns[max(0, idx-context_turns):idx],
                                               start=max(0, idx-context_turns))
                        if isinstance(t.get('utterance'), str) and t.get('speaker') in ('USER', 'SYSTEM')
                    ]
                    eid = hashlib.sha256(f'SGD:train:{did}:{idx}:{service}'.encode()).hexdigest()[:20]
                    records.append({
                        'example_id': f'sgd_{eid}', 'source': {'dataset': 'SGD', 'split': 'train',
                        'dialogue_id': did, 'turn_index': idx, 'service': service},
                        'history': history, 'utterance': text,
                        '_private': {'stratum': stratum, 'lexical_flags': flags,
                                     'state_change_candidates': changes, 'prior_service_frame': had_prior},
                    })
                    stats[f'available_{stratum}'] += 1
                    previous_states[service] = slot_values
    return records, {'total_records': len(records), 'counts': dict(sorted(stats.items())),
                     'raw_file_sha256': file_hashes, 'distinct_dialogues': len(seen_dids)}


def select_pilot(records: list[dict], target: int, seed: int) -> tuple[list[dict], dict]:
    """Seeded round-robin stratification, max one selected example per dialogue."""
    if target <= 0:
        raise ValueError('sample-size must be > 0')
    rng = random.Random(seed)
    buckets: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        buckets[record['_private']['stratum']].append(record)
    for bucket in buckets.values():
        bucket.sort(key=lambda r: r['example_id'])
        rng.shuffle(bucket)
    selected: list[dict] = []
    used_dids: set[str] = set()
    indexes: dict[str, int] = defaultdict(int)
    while len(selected) < target:
        made_progress = False
        for key in STRATA:
            bucket = buckets[key]
            while indexes[key] < len(bucket):
                r = bucket[indexes[key]]
                indexes[key] += 1
                did = r['source']['dialogue_id']
                if did in used_dids:
                    continue
                selected.append(r)
                used_dids.add(did)
                made_progress = True
                break
            if len(selected) >= target:
                break
        if not made_progress:
            break
    breakdown = dict(sorted(Counter(r['_private']['stratum'] for r in selected).items()))
    return selected, {'requested_sample_size': target, 'actual_selected': len(selected),
                      'random_seed': seed, 'max_per_dialogue': 1,
                      'selection_method': 'seeded_round_robin_across_priority_strata',
                      'selection_is_not_population_representative': True,
                      'selected_strata': breakdown,
                      'shortfall': max(0, target-len(selected))}


def annotator_record(record: dict) -> dict:
    """No target labels or heuristics; blank fields are NOT negative labels."""
    return {
        'example_id': record['example_id'], 'source': record['source'],
        'history': record['history'], 'current_user_utterance': record['utterance'],
        'annotation': {'status': 'UNLABELED', 'guideline_version': 'pilot_v0.1',
                       'value_spans': None, 'cue_spans': None, 'transitions': None,
                       'difficulty': None, 'uncertainty_notes': None},
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    with path.open('w', encoding='utf-8') as out:
        for r in records:
            out.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')


def main() -> None:
    ap = argparse.ArgumentParser(description='Prepare a blinded, unlabeled SGD pilot annotation sample')
    ap.add_argument('--sgd-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--split', default='train', choices=['train'], help='Safety: only train split permitted')
    ap.add_argument('--sample-size', type=int, default=100)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--context-turns', type=int, default=8)
    args = ap.parse_args()
    if args.context_turns < 0:
        ap.error('context-turns must not be negative')
    paths = sorted((args.sgd_root/'train').glob('dialogues_*.json'))
    if not paths:
        ap.error('No train/dialogues_*.json files found')
    # Never overwrite human-edited annotation packets or private manifests.
    if args.out.exists() and any(args.out.iterdir()):
        ap.error('Output directory is not empty. Use a new versioned path to prevent overwriting human work.')
    records, inventory = mine_raw(paths, args.context_turns)
    selection, meta = select_pilot(records, args.sample_size, args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    blind = [annotator_record(r) for r in selection]
    write_jsonl(args.out/'annotator_A_UNLABELED.jsonl', blind)
    write_jsonl(args.out/'annotator_B_UNLABELED.jsonl', blind)
    write_jsonl(args.out/'PRIVATE_sampling_manifest.jsonl', [
        {'example_id': r['example_id'], 'source': r['source'], **r['_private']}
        for r in selection
    ])
    summary = {'status': 'UNLABELED_PILOT_ONLY', 'dataset_inventory': inventory,
               'selection': meta,
               'warning': 'Candidate classes are heuristics, not human gold; annotation packets contain no gold labels. Do not train or claim F1.'}
    (args.out/'pilot_sampling_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Prepared {len(selection)} UNLABELED cases from {inventory['distinct_dialogues']} dialogues in {args.out}")
    print('STOP: two independent human annotations, adjudication and data review required before any training.')


if __name__ == '__main__':
    main()
