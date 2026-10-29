"""Regression tests for DEV-001 consensus-reference acceptance (v0.8 protocol).

Strict defaults MUST stay strict: annotation.status=CONSENSUS_REFERENCE is
accepted only with the explicit flag, and only when the remainder of the gold
contract (two reviewers, adjudication log id, guideline version, offsets)
still holds. The prospective test reference is double-annotated consensus,
never claimed to be adjudicated for the 60 unresolved disputes.
"""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from test_annotation_contracts import example  # noqa: E402
from validate_annotations import validate_rows  # noqa: E402
from freeze_gold_splits import freeze  # noqa: E402
from evaluate_frozen_test import canonical_gold_sha256, check_manifest  # noqa: E402
from evaluate_spans import evaluate  # noqa: E402


def rehash(manifest: dict, gold: list[dict]) -> dict:
    """Recompute content SHA + manifest digest after a sanctioned test edit."""
    manifest = copy.deepcopy(manifest)
    manifest['gold_content_sha256'] = canonical_gold_sha256(gold)
    manifest['manifest_digest'] = hashlib.sha256(json.dumps(
        {k: v for k, v in manifest.items() if k != 'manifest_digest'},
        sort_keys=True).encode()).hexdigest()
    return manifest


def consensus_row(i: int = 1) -> dict:
    row = example(i)
    row['annotation']['status'] = 'CONSENSUS_REFERENCE'
    return row


class ConsensusReferenceTests(unittest.TestCase):
    def test_strict_default_rejects_consensus_status(self):
        rows = [consensus_row()]
        report = validate_rows(rows, True)
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('ADJUDICATED', report['errors'][0])

    def test_explicit_flag_accepts_consensus_status(self):
        rows = [consensus_row()]
        self.assertEqual(validate_rows(rows, True, accept_consensus=True)['status'], 'PASS')

    def test_flag_does_not_waive_adjudication_log(self):
        rows = [consensus_row()]
        del rows[0]['annotation']['adjudication_log_id']
        self.assertEqual(validate_rows(rows, True, accept_consensus=True)['status'], 'FAIL')

    def test_flag_does_not_waive_two_reviewers(self):
        rows = [consensus_row()]
        rows[0]['annotation']['reviewers'] = ['human_A']
        self.assertEqual(validate_rows(rows, True, accept_consensus=True)['status'], 'FAIL')

    def test_flag_does_not_waive_offsets(self):
        rows = [consensus_row()]
        rows[0]['value_spans'][0]['end'] = 15  # breaks text == utterance slice
        self.assertEqual(validate_rows(rows, True, accept_consensus=True)['status'], 'FAIL')

    def test_check_manifest_end_to_end_with_flag(self):
        rows = [example(i) for i in range(1, 61)]
        manifest = freeze(rows, 42)
        gold = copy.deepcopy(rows)
        gold[0]['annotation']['status'] = 'CONSENSUS_REFERENCE'
        gold[0]['source']['split'] = 'dev'  # holdout rows come from official dev/test
        manifest = rehash(manifest, gold)
        with self.assertRaisesRegex(ValueError, 'status'):
            check_manifest(gold, manifest)  # strict default refuses
        heldout = check_manifest(gold, manifest, accept_consensus=True)
        self.assertEqual(len(heldout), len(manifest['splits']['test']))

    def test_evaluate_requires_flag_for_consensus_gold(self):
        gold = [consensus_row()]
        preds = [{'id': 'EX-1', 'value_spans': [], 'cue_spans': []}]
        with self.assertRaisesRegex(ValueError, 'status'):
            evaluate(gold, preds, allowed_splits=('train', 'dev', 'test'))
        report = evaluate(gold, preds, accept_consensus=True,
                          allowed_splits=('train', 'dev', 'test'))
        self.assertEqual(report['status'], 'MEASURED_FROM_SUPPLIED_GOLD_AND_PREDICTIONS')

    def test_evaluate_default_still_strict_for_adjudicated_train_gold(self):
        gold = [example(1)]
        preds = [{'id': 'EX-1', 'value_spans': [], 'cue_spans': []}]
        report = evaluate(gold, preds)
        self.assertEqual(report['status'], 'MEASURED_FROM_SUPPLIED_GOLD_AND_PREDICTIONS')


if __name__ == '__main__':
    unittest.main()
