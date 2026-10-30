"""Tests for the gold v1.1 builder: exact-before-state assertions, label/offset changes only."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_gold_v1_1 import apply_changes  # noqa: E402


def row(rid: str, utt: str, spans: list[tuple]) -> dict:
    return {'id': rid, 'current_user_utterance': utt, 'cue_spans': [],
            'value_spans': [{'start': s, 'end': e, 'label': lab, 'text': utt[s:e]} for lab, s, e in spans],
            'annotation': {'status': 'ADJUDICATED', 'decision_reason': 'original'}}


CHANGES = {
    'R1': ([('KEPT_VALUE', 3, 11, 'same day')], [('REFERENCE', 3, 11, 'same day')]),
    'R2': ([('NEW_VALUE', 0, 14, 'hotel with two')], [('NEW_VALUE', 0, 5, 'hotel'), ('NEW_VALUE', 11, 14, 'two')]),
}


class BuildGoldV11Tests(unittest.TestCase):
    def rows(self):
        return [row('R1', 'on same day', [('KEPT_VALUE', 3, 11)]),
                row('R2', 'hotel with two', [('NEW_VALUE', 0, 14)]),
                row('R3', 'untouched row', [('NEW_VALUE', 0, 9)])]

    def test_changes_apply_and_other_rows_stay_identical(self):
        old = self.rows()
        new = apply_changes(old, CHANGES)
        self.assertEqual(new[2], old[2])
        self.assertEqual(new[0]['value_spans'][0]['label'], 'REFERENCE')
        self.assertEqual([s['text'] for s in new[1]['value_spans']], ['hotel', 'two'])
        self.assertIn('D3-V1_1', new[0]['annotation']['decision_reason'])
        self.assertEqual(new[0]['annotation']['adjudication_log_id'], 'D3-ADJ-2026-10-30-V1_1')

    def test_input_rows_are_not_mutated(self):
        old = self.rows()
        apply_changes(old, CHANGES)
        self.assertEqual(old, self.rows())

    def test_refuses_when_before_state_differs(self):
        old = self.rows()
        old[0]['value_spans'][0]['label'] = 'NEW_VALUE'
        with self.assertRaises(SystemExit):
            apply_changes(old, CHANGES)

    def test_refuses_unknown_decided_id(self):
        with self.assertRaises(SystemExit):
            apply_changes(self.rows()[:1], CHANGES)

    def test_refuses_offsets_that_do_not_spell_the_text(self):
        bad = {'R1': ([('KEPT_VALUE', 3, 11, 'same day')], [('REFERENCE', 3, 10, 'same day')])}
        with self.assertRaises(SystemExit):
            apply_changes([self.rows()[0]], bad)


if __name__ == '__main__':
    unittest.main()
