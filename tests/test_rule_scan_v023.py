"""Tests for the mechanical v0.2.3 rule scan (flags only)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from rule_scan_v023 import scan_row  # noqa: E402


def row(utt, value=(), cue=()):
    mk = lambda spans: [{'start': s, 'end': e, 'label': lab} for lab, s, e in spans]
    return {'id': 'R', 'current_user_utterance': utt, 'value_spans': mk(value), 'cue_spans': mk(cue)}


class RuleScanTests(unittest.TestCase):
    def rules(self, r):
        return sorted(f['rule'] for f in scan_row(r))

    def test_clean_row_has_no_flags(self):
        self.assertEqual(self.rules(row('Actually, a table for three.', [('NEW_VALUE', 10, 17), ('NEW_VALUE', 22, 27)],
                                        [('UPDATE_CUE', 0, 8)])), [])

    def test_unsplit_and_leading_preposition(self):
        u = 'I need a hotel with 3 rooms on Friday'
        self.assertEqual(self.rules(row(u, [('NEW_VALUE', 7, 27), ('NEW_VALUE', 28, 37)])), ['C1-r/F2', 'F1'])

    def test_at_least_is_not_a_leading_preposition(self):
        self.assertEqual(self.rules(row('rated at least 4.2', [('NEW_VALUE', 6, 18)])), [])

    def test_refusal_cancel_and_discourse_keep(self):
        self.assertEqual(self.rules(row('No, not now.', cue=[('CANCEL_CUE', 0, 11)])), ['DP-1'])
        self.assertEqual(self.rules(row("Let's keep looking.", cue=[('KEEP_CUE', 6, 18)])), ['R9'])

    def test_occurrence_inside_another_token(self):
        u = 'for 5:30 in the evening for 3 instead'
        self.assertIn('offset', self.rules(row(u, [('NEW_VALUE', 6, 7)])))
        self.assertNotIn('offset', self.rules(row(u, [('NEW_VALUE', 28, 29)])))


if __name__ == '__main__':
    unittest.main()
