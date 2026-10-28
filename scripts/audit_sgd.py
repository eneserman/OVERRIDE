#!/usr/bin/env python3
"""Read-only audit of original Google SGD JSON; NOT a correction gold generator.

Outputs aggregate schema/offset statistics and unreviewed revision CANDIDATES.
No model labels, training data or corrected SGD files are emitted.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

CUE_PATTERNS = {
    'possible_revision_cue': re.compile(r'\b(?:actually|instead|rather|change|switch|replace|no,?)\b', re.I),
    'possible_keep_cue': re.compile(r'\b(?:keep|remain|unchanged|same)\b', re.I),
    'possible_cancel_cue': re.compile(r'\b(?:cancel|delete|remove|stop)\b', re.I),
    'possible_restore_cue': re.compile(r'\b(?:back to|original|first (?:one|option)|previous)\b', re.I),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def as_strings(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    return tuple(str(v).strip() for v in values if str(v).strip())


def normalized_set(values: Any) -> frozenset[str]:
    # Lexical normalization only. Does NOT establish semantic equivalence.
    return frozenset(' '.join(v.casefold().split()) for v in as_strings(values))


def state_deltas(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate unverified *candidates*, never gold correction labels."""
    changes = []
    for slot in sorted(set(before) | set(after)):
        old = normalized_set(before.get(slot))
        new = normalized_set(after.get(slot))
        if not old and new:
            kind = 'SLOT_ADDED_CANDIDATE'
        elif old and not new:
            kind = 'SLOT_CLEARED_CANDIDATE'
        elif old == new:
            continue
        elif old.intersection(new):
            # SGD slot_values may store many equivalent realizations; overlap
            # is evidence for possible alias variation, not a revision.
            kind = 'ALIAS_OR_STATE_VARIANT_CANDIDATE'
        else:
            kind = 'SLOT_CHANGED_CANDIDATE'
        changes.append({'slot': slot, 'kind': kind, 'before': sorted(old), 'after': sorted(new)})
    return changes


def inspect_dataset(dataset_files: list[Path], split: str, max_candidates: int = 100) -> tuple[dict, list[dict]]:
    counts: collections.Counter[str] = collections.Counter()
    services: collections.Counter[str] = collections.Counter()
    domains: collections.Counter[str] = collections.Counter()
    candidates: list[dict] = []
    file_hashes: dict[str, str] = {}
    invalid_examples: list[dict] = []
    unique_dialogue_ids: set[str] = set()
    for path in sorted(dataset_files):
        file_hashes[str(path.resolve())] = sha256(path)
        with path.open(encoding='utf-8') as fh:
            dialogues = json.load(fh)
        if not isinstance(dialogues, list):
            raise ValueError(f'{path}: expected a list of dialogues')
        counts['source_files'] += 1
        for dialogue in dialogues:
            did = str(dialogue.get('dialogue_id', ''))
            if not did:
                counts['dialogues_missing_id'] += 1
                continue
            if did in unique_dialogue_ids:
                counts['repeated_dialogue_id'] += 1
            unique_dialogue_ids.add(did)
            counts['dialogues'] += 1
            prior_per_service: dict[str, dict] = {}
            prior_turn_idx: dict[str, int] = {}
            for i, turn in enumerate(dialogue.get('turns', [])):
                speaker = turn.get('speaker')
                utterance = turn.get('utterance', '')
                if not isinstance(utterance, str):
                    counts['invalid_utterance_type'] += 1
                    continue
                counts['turns'] += 1
                if speaker == 'USER':
                    counts['user_turns'] += 1
                elif speaker == 'SYSTEM':
                    counts['system_turns'] += 1
                else:
                    counts['unknown_speaker_turns'] += 1
                flags = [name for name, pattern in CUE_PATTERNS.items() if pattern.search(utterance)]
                if speaker == 'USER':
                    for flag in flags:
                        counts[f'lexical_{flag}_turns'] += 1
                for frame in turn.get('frames', []):
                    service = frame.get('service')
                    if not service:
                        counts['missing_frame_service'] += 1
                        continue
                    if speaker == 'USER':
                        counts['user_frames'] += 1
                        services[service] += 1
                        domains[service.split('_')[0]] += 1
                    for span in frame.get('slots', []):
                        counts['reported_span_offsets'] += 1
                        start, end = span.get('start'), span.get('exclusive_end')
                        valid = (
                            isinstance(start, int) and not isinstance(start, bool)
                            and isinstance(end, int) and not isinstance(end, bool)
                            and 0 <= start < end <= len(utterance)
                            and bool(utterance[start:end].strip())
                        )
                        counts['valid_span_offsets' if valid else 'invalid_span_offsets'] += 1
                        if not valid and len(invalid_examples) < 10:
                            invalid_examples.append({'dialogue_id': did, 'turn_index': i, 'service': service, 'span': span})
                    if speaker != 'USER':
                        continue
                    state = frame.get('state')
                    if not isinstance(state, dict):
                        counts['user_frames_missing_state'] += 1
                        continue
                    slot_values = state.get('slot_values', {})
                    if not isinstance(slot_values, dict):
                        counts['invalid_slot_values_mapping'] += 1
                        continue
                    counts['nonempty_slot_state_frames'] += bool(slot_values)
                    counts['state_slot_entries'] += len(slot_values)
                    if service in prior_per_service:
                        counts['same_service_state_comparisons'] += 1
                        if prior_turn_idx[service] != i - 2:
                            # Diagnostic only: a gap need not indicate a domain switch.
                            counts['same_service_non_adjacent_user_frames'] += 1
                        deltas = state_deltas(prior_per_service[service], slot_values)
                        for change in deltas:
                            counts[change['kind']] += 1
                        if deltas:
                            counts['state_comparisons_with_candidates'] += 1
                        if deltas and len(candidates) < max_candidates:
                            candidates.append({
                                'provenance': 'SGD_STATE_DIFF_UNREVIEWED_NOT_GOLD',
                                'split': split, 'dialogue_id': did, 'turn_index': i,
                                'service': service, 'utterance': utterance,
                                'change_candidates': deltas,
                                'lexical_flags': flags,
                                'previous_same_service_turn_index': prior_turn_idx[service],
                            })
                    else:
                        counts['first_observed_user_frame_for_service'] += 1
                    prior_per_service[service] = slot_values
                    prior_turn_idx[service] = i
    result = {
        'status': 'OBSERVATIONAL_AUDIT_ONLY',
        'split': split,
        'source_files_sha256': file_hashes,
        'counts': dict(sorted(counts.items())),
        'services_user_frames': dict(sorted(services.items())),
        'domains_user_frames': dict(sorted(domains.items())),
        'invalid_offset_examples_up_to_10': invalid_examples,
        'unique_dialogue_ids': len(unique_dialogue_ids),
        'limits': [
            'State differences are only candidates; no UPDATE, KEEP, RESTORE or CANCEL gold is inferred.',
            'SGD contains lexical slot aliases; changed strings are not necessarily changed meaning.',
            'Sparse or missing L4/L5 corrections cannot be ruled in or out from these statistics.',
            'Current-user state is source supervision only; it must not leak into model inputs at test time.',
            'Sampled candidate list is capped and cannot be treated as a random unbiased sample.',
        ],
    }
    return result, candidates


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit raw Google SGD. NO annotation/model training.')
    parser.add_argument('--sgd-root', required=True, type=Path, help='Original downloaded SGD repository root')
    parser.add_argument('--split', choices=['train', 'dev', 'test'], default='train')
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--limit-files', type=int, default=0, help='For smoke tests only; 0 means all files')
    parser.add_argument('--sample-limit', type=int, default=100)
    parser.add_argument('--allow-eval-split', action='store_true', help='Explicit opt-in for read-only dev/test inspection')
    args = parser.parse_args()
    if args.split != 'train' and not args.allow_eval_split:
        parser.error('Only train is audited by default; --allow-eval-split required for dev/test')
    files = sorted((args.sgd_root / args.split).glob('dialogues_*.json'))
    if args.limit_files > 0:
        files = files[:args.limit_files]
    if not files:
        parser.error('No dialogues_*.json in given split directory; download official SGD first')
    report, candidates = inspect_dataset(files, args.split, args.sample_limit)
    report['sampling_mode'] = f'first_{args.limit_files}_files_for_smoke_test' if args.limit_files else 'all_matching_split_files'
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'sgd_audit_summary.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (args.out / 'UNREVIEWED_candidate_examples.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in candidates), encoding='utf-8')
    with (args.out / 'service_counts.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['service', 'user_frames'])
        writer.writerows(report['services_user_frames'].items())
    print(f'Audit complete: {report["counts"].get("dialogues",0)} dialogues; output={args.out}')
    print('WARNING: unreviewed candidates are NOT human-verified gold labels.')


if __name__ == '__main__':
    main()
