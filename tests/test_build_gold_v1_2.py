"""Tests for the gold v1.2 EXT merge: decided set must match, decisions applied, solo fix fail-closed."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_gold_v1_2 import build_ext_rows  # noqa: E402


def row(rid, utt, value=(), cue=(), who='A'):
    mk = lambda sp: [{'start': s, 'end': e, 'label': lab, 'text': utt[s:e]} for lab, s, e in sp]
    return {'id': rid, 'source': {'split': 'train', 'dialogue_id': rid}, 'dialogue_family_id': rid, 'history': [],
            'current_user_utterance': utt, 'value_spans': mk(value), 'cue_spans': mk(cue),
            'annotation': {'reviewer_id': who, 'uncertainty_notes': None}}


U = 'Actually make it two'
A = [row('S1', U, [('NEW_VALUE', 17, 20)], [('UPDATE_CUE', 0, 8)]), row('S2', U, [('NEW_VALUE', 17, 20)]),
     row('SA', 'go back to it', cue=[('RESTORE_CUE', 3, 10)])]
B = [row('S1', U, [('NEW_VALUE', 17, 20)], [('UPDATE_CUE', 0, 8)], 'B'), row('S2', U, [('NEW_VALUE', 17, 20)], [('UPDATE_CUE', 9, 16)], 'B'),
     row('SB', U, [('NEW_VALUE', 17, 20)], who='B')]


class BuildGoldV12Tests(unittest.TestCase):
    def test_agreed_decided_and_solo_rows(self):
        out = {r['id']: r for r in build_ext_rows(A, B, ['S1', 'S2'], decisions={'S2': 'B'},
                                                    solo_removals={'SA': ('A', ('RESTORE_CUE', 3, 10, 'back to'))})}
        self.assertEqual(out['S1']['annotation']['issue_type'], 'ext_double_blind_agreed')
        self.assertEqual([s['text'] for s in out['S2']['cue_spans']], ['make it'])
        self.assertEqual(out['SA']['cue_spans'], [])
        self.assertEqual(out['SA']['annotation']['issue_type'], 'ext_single_annotation_rule_flag_joint_decision')
        self.assertIn('did not re-check', out['SB']['annotation']['decision_reason'])
        self.assertEqual(out['SB']['annotation']['reviewers'], ['reviewer_A_BURAK', 'reviewer_B_ENES'])

    def test_refuses_when_a_differing_record_is_undecided(self):
        with self.assertRaises(SystemExit):
            build_ext_rows(A, B, ['S1', 'S2'], decisions={}, solo_removals={})

    def test_d_decision_must_spell_the_text(self):
        with self.assertRaises(SystemExit):
            build_ext_rows(A, B, ['S1', 'S2'], decisions={'S2': [('NEW_VALUE', 16, 20, 'two')]}, solo_removals={})

    def test_solo_fix_requires_exact_before_state(self):
        with self.assertRaises(SystemExit):
            build_ext_rows(A, B, ['S1', 'S2'], decisions={'S2': 'A'},
                           solo_removals={'SA': ('B', ('RESTORE_CUE', 3, 10, 'back to'))})


if __name__ == '__main__':
    unittest.main()
