"""Tests for D3 adjudication tooling (CTO prep): allowed-splits gold validation,
per-label agreement metrics and the human-decision gold builder.

Invariant under test throughout: nothing becomes gold without real human
review + human adjudication decisions.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))

from annotation_agreement import compare, span_label_metrics  # noqa: E402
from validate_annotations import validate_rows  # noqa: E402

UTT = "Actually Paris, but keep Friday."


def canonical(rid, reviewer_id, value_spans, cue_spans, split='train', did=None, notes=''):
    did = did or f'fam-{rid}'
    return {
        'id': rid,
        'source': {'dataset': 'SGD', 'split': split, 'dialogue_id': did, 'turn_index': 2, 'service': 'Flight_1'},
        'dialogue_family_id': did,
        'history': [{'speaker': 'USER', 'turn_index': 0, 'utterance': 'Two people to Berlin on Friday.'}],
        'current_user_utterance': UTT,
        'value_spans': value_spans,
        'cue_spans': cue_spans,
        'transitions': [],
        'links': [],
        'difficulty': 'L2',
        'annotation': {'status': 'ANNOTATED', 'guideline_version': 'pilot_v0.1',
                       'reviewer_id': reviewer_id, 'uncertainty_notes': notes},
    }


def span(start, end, text, label):
    return {'start': start, 'end': end, 'text': text, 'label': label}


V = [span(9, 14, 'Paris', 'NEW_VALUE'), span(25, 31, 'Friday', 'KEPT_VALUE')]
C = [span(0, 8, 'Actually', 'UPDATE_CUE'), span(20, 24, 'keep', 'KEEP_CUE')]


class AllowedSplitsTest(unittest.TestCase):
    def test_train_gold_default_and_test_gold_needs_explicit_splits(self):
        train_gold = canonical('g1', 'rev_a', V, C, split='train')
        train_gold['annotation'] = {'status': 'ADJUDICATED', 'guideline_version': 'v1',
                                   'reviewers': ['rev_a', 'rev_b'], 'adjudication_log_id': 'LOG-1'}
        self.assertEqual(validate_rows([train_gold], True)['status'], 'PASS')

        test_gold = canonical('g2', 'rev_a', V, C, split='test', did='t-fam')
        test_gold['annotation'] = {'status': 'ADJUDICATED', 'guideline_version': 'v1',
                                  'reviewers': ['rev_a', 'rev_b'], 'adjudication_log_id': 'LOG-1'}
        self.assertEqual(validate_rows([test_gold], True)['status'], 'FAIL')  # default: train only
        self.assertEqual(validate_rows([test_gold], True, ('dev', 'test'))['status'], 'PASS')


class AgreementMetricsTest(unittest.TestCase):
    def test_per_label_span_agreement(self):
        # A: x1 has NEW+KEPT, x2 has NEW ; B: x1 has NEW only, x2 nothing
        a = [canonical('x1', 'rev_a', V, C), canonical('x2', 'rev_a', [span(9, 14, 'Paris', 'NEW_VALUE')], [])]
        b = [canonical('x1', 'rev_b', [V[0]], C), canonical('x2', 'rev_b', [], [])]
        rep = compare(a, b)
        m = rep['span_level_agreement_by_label']
        new = m['value_spans']['NEW_VALUE']
        self.assertEqual((new['matched_exact_spans'], new['only_in_A'], new['only_in_B']), (1, 1, 0))
        self.assertAlmostEqual(new['agreement_f1_symmetric'], 2 / 3, places=6)
        kept = m['value_spans']['KEPT_VALUE']
        self.assertEqual((kept['matched_exact_spans'], kept['only_in_A']), (0, 1))
        self.assertAlmostEqual(kept['agreement_f1_symmetric'], 0.0)
        self.assertEqual(m['cue_spans']['UPDATE_CUE']['agreement_f1_symmetric'], 1.0)
        self.assertIn('difficulty_agreement', rep)
        self.assertEqual(rep['uncertainty_flagged']['reviewer_A'], [])

    def test_span_label_metrics_empty(self):
        self.assertEqual(span_label_metrics({'x': {'value_spans': [], 'cue_spans': []}},
                                            {'x': {'value_spans': [], 'cue_spans': []}}),
                         {'value_spans': {}, 'cue_spans': {}})


class BuildAdjudicatedGoldTest(unittest.TestCase):
    def _write(self, tmp, name, rows):
        p = Path(tmp) / name
        p.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
        return p

    def _run(self, *argv):
        return subprocess.run([sys.executable, str(SCRIPTS / 'build_adjudicated_gold.py'), *argv],
                              capture_output=True, text=True)

    def test_gold_built_only_from_human_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self._write(tmp, 'a.jsonl', [canonical('x1', 'rev_a', V, C), canonical('x2', 'rev_a', [], [])])
            b = self._write(tmp, 'b.jsonl', [canonical('x1', 'rev_b', V, C), canonical('x2', 'rev_b', [V[0]], [])])
            dec = self._write(tmp, 'dec.jsonl', [
                {'example_id': 'x1', 'value_spans': V, 'cue_spans': C, 'transitions': [],
                 'links': [], 'difficulty': 'L2', 'issue_type': 'boundary', 'decision_reason': 'both agree'},
                {'example_id': 'x2', 'value_spans': [], 'cue_spans': [], 'transitions': [],
                 'links': [], 'difficulty': 'L1', 'issue_type': 'class', 'decision_reason': 'B saw a false positive'},
            ])
            out = Path(tmp) / 'gold.jsonl'
            r = self._run('--a', str(a), '--b', str(b), '--decisions', str(dec),
                          '--adjudicator', 'hakem_1', '--log-id', 'ADJ-2026-001', '--out', str(out))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rows = [json.loads(x) for x in out.read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['annotation']['status'], 'ADJUDICATED')
            self.assertEqual(rows[0]['annotation']['reviewers'], ['rev_a', 'rev_b'])
            self.assertEqual(validate_rows(rows, True)['status'], 'PASS')
            # and it must FAIL non-gold-safe expectations: two distinct reviewers enforced
            self.assertEqual(validate_rows(rows, True, ('dev', 'test'))['status'], 'FAIL')  # split=train not in dev,test

    def test_missing_decision_reported_and_require_all_aborts(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self._write(tmp, 'a.jsonl', [canonical('x1', 'rev_a', V, C), canonical('x2', 'rev_a', [], [])])
            b = self._write(tmp, 'b.jsonl', [canonical('x1', 'rev_b', V, C), canonical('x2', 'rev_b', [], [])])
            dec = self._write(tmp, 'dec.jsonl', [
                {'example_id': 'x1', 'value_spans': V, 'cue_spans': C, 'decision_reason': 'ok'}])
            out = Path(tmp) / 'gold.jsonl'
            r = self._run('--a', str(a), '--b', str(b), '--decisions', str(dec),
                          '--adjudicator', 'h', '--log-id', 'L', '--require-all', '--out', str(out))
            self.assertEqual(r.returncode, 1)
            self.assertFalse(out.exists())

    def test_invalid_decision_span_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self._write(tmp, 'a.jsonl', [canonical('x1', 'rev_a', V, C)])
            b = self._write(tmp, 'b.jsonl', [canonical('x1', 'rev_b', V, C)])
            bad = [span(0, 5, 'WRONG', 'NEW_VALUE')]  # text != slice
            dec = self._write(tmp, 'dec.jsonl', [{'example_id': 'x1', 'value_spans': bad, 'cue_spans': [], 'decision_reason': 'x'}])
            out = Path(tmp) / 'gold.jsonl'
            r = self._run('--a', str(a), '--b', str(b), '--decisions', str(dec),
                          '--adjudicator', 'h', '--log-id', 'L', '--out', str(out))
            self.assertEqual(r.returncode, 1)
            self.assertFalse(out.exists())
            self.assertIn('text does not equal', r.stdout)

    def test_same_reviewer_rejected_and_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self._write(tmp, 'a.jsonl', [canonical('x1', 'same_rev', V, C)])
            b = self._write(tmp, 'b.jsonl', [canonical('x1', 'same_rev', V, C)])
            dec = self._write(tmp, 'dec.jsonl', [{'example_id': 'x1', 'value_spans': V, 'cue_spans': C, 'decision_reason': 'x'}])
            out = Path(tmp) / 'gold.jsonl'
            r = self._run('--a', str(a), '--b', str(b), '--decisions', str(dec),
                          '--adjudicator', 'h', '--log-id', 'L', '--out', str(out))
            self.assertEqual(r.returncode, 1)
            self.assertIn('independent review not established', r.stdout)


class AgreementExclusionTest(unittest.TestCase):
    def test_practice_items_excluded_from_primary_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            practice = canonical('cal1', 'rev_a', V, C)
            practice_b = canonical('cal1', 'rev_b', [], [])  # discussed item: would look like disagreement
            real_a = canonical('t1', 'rev_a', V, C)
            real_b = canonical('t1', 'rev_b', V, C)
            for name, rows in (('a.jsonl', [practice, real_a]), ('b.jsonl', [practice_b, real_b])):
                (Path(tmp) / name).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
            excl = Path(tmp) / 'cal.jsonl'
            excl.write_text(json.dumps({'ids': ['cal1']}), encoding='utf-8')
            out = Path(tmp) / 'agr.jsonl'
            r = subprocess.run([sys.executable, str(SCRIPTS / 'annotation_agreement.py'),
                                '--a', str(Path(tmp) / 'a.jsonl'), '--b', str(Path(tmp) / 'b.jsonl'),
                                '--exclude-ids', str(excl), '--out', str(out)],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            rep = json.loads(out.read_text(encoding='utf-8'))
            self.assertEqual(rep['excluded_ids'], ['cal1'])
            primary = rep['agreement_excluding_practice_items']
            full = rep['agreement_including_practice_items']
            self.assertEqual(primary['examples'], 1)
            self.assertEqual(primary['exact_layer_set_agreement'], 1.0)   # practice item not counted
            self.assertEqual(full['examples'], 2)
            self.assertLess(full['exact_layer_set_agreement'], 1.0)        # disclosed but not primary


if __name__ == '__main__':
    unittest.main()
