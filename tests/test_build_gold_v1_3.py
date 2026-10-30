"""Tests for the gold v1.3 builder: identical records asserted, decisions applied, others untouched."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_gold_v1_3 import apply  # noqa: E402

U = 'make it two'


def row(rid, value=(), cue=()):
    mk = lambda sp: [{'start': s, 'end': e, 'label': lab, 'text': U[s:e]} for lab, s, e in sp]
    return {'id': rid, 'current_user_utterance': U, 'value_spans': mk(value), 'cue_spans': mk(cue),
            'annotation': {'issue_type': 'ext_single_annotation_rule_scan'}}


GOLD = [row('S1', [('NEW_VALUE', 8, 11)]), row('S2', [('NEW_VALUE', 8, 11)]), row('OLD', [('NEW_VALUE', 8, 11)])]
RA = [row('S1', [('NEW_VALUE', 8, 11)]), row('S2', [('NEW_VALUE', 8, 11)], [('UPDATE_CUE', 0, 7)])]
RB = [row('S1', [('NEW_VALUE', 8, 11)]), row('S2', [('NEW_VALUE', 8, 11)])]
DEC = {'S2': {'how': 'joint_decision', 'value_spans': [{'start': 8, 'end': 11, 'label': 'NEW_VALUE', 'text': 'two'}],
              'cue_spans': [{'start': 0, 'end': 7, 'label': 'UPDATE_CUE', 'text': 'make it'}]}}


class BuildGoldV13Tests(unittest.TestCase):
    def test_identical_and_decided_records(self):
        out = {r['id']: r for r in apply(GOLD, ['S1', 'S2'], RA, RB, DEC)}
        self.assertEqual(out['S1']['annotation']['issue_type'], 'ext_cross_double_blind_agreed')
        self.assertEqual([s['text'] for s in out['S2']['cue_spans']], ['make it'])
        self.assertEqual(out['S2']['annotation']['issue_type'], 'ext_cross_double_blind_joint_decision')
        self.assertEqual(out['OLD'], GOLD[2])

    def test_undecided_difference_fails_closed(self):
        with self.assertRaises(SystemExit):
            apply(GOLD, ['S1', 'S2'], RA, RB, {})

    def test_decided_span_must_spell_the_text(self):
        bad = {'S2': {'how': 'joint_decision', 'value_spans': [{'start': 7, 'end': 11, 'label': 'NEW_VALUE', 'text': 'two'}], 'cue_spans': []}}
        with self.assertRaises(SystemExit):
            apply(GOLD, ['S1', 'S2'], RA, RB, bad)


if __name__ == '__main__':
    unittest.main()
