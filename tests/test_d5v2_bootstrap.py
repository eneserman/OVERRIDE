import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from d5v2_bootstrap import counts, score  # noqa: E402


def row(values, cues=()):
    return {'value_spans': [{'start': s, 'end': e, 'label': l} for s, e, l in values],
            'cue_spans': [{'start': s, 'end': e, 'label': l} for s, e, l in cues]}


class TestBootstrapScore(unittest.TestCase):
    def test_exact_match_only(self):
        gold = row([(0, 5, 'NEW_VALUE')], [(6, 12, 'UPDATE_CUE')])
        pred = row([(0, 4, 'NEW_VALUE')], [(6, 12, 'UPDATE_CUE')])
        c = counts(gold, pred)
        self.assertEqual(c['value_spans'], (0, 1, 1))
        self.assertEqual(c['cue_spans'], (1, 1, 1))
        self.assertAlmostEqual(score([c]), 0.5)

    def test_label_must_match(self):
        c = counts(row([(0, 5, 'NEW_VALUE')]), row([(0, 5, 'REFERENCE')]))
        self.assertEqual(c['value_spans'], (0, 1, 1))

    def test_micro_pooling(self):
        a = counts(row([(0, 5, 'NEW_VALUE')]), row([(0, 5, 'NEW_VALUE')]))
        b = counts(row([(0, 5, 'NEW_VALUE')]), row([]))
        # value: tp 1, pred 1, gold 2 -> F1 2/3; cue layer empty -> 0
        self.assertAlmostEqual(score([a, b]), (2 / 3) / 2)


if __name__ == '__main__':
    unittest.main()
