"""Tests for the pre-registered gold v1 blind re-annotation audit tool."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from gold_v1_audit import pick, score_rows  # noqa: E402


def row(rid: str, value: list[tuple], cue: list[tuple] = ()) -> dict:
    return {'id': rid,
            'value_spans': [{'start': s, 'end': e, 'label': lab} for s, e, lab in value],
            'cue_spans': [{'start': s, 'end': e, 'label': lab} for s, e, lab in cue]}


class GoldAuditTests(unittest.TestCase):
    def test_pick_is_deterministic_and_order_independent(self):
        ids = [f'ID-{i}' for i in range(100)]
        first = pick(ids, 20261030, 24)
        self.assertEqual(first, pick(list(reversed(ids)), 20261030, 24))
        self.assertEqual(len(set(first)), 24)
        self.assertNotEqual(first, pick(ids, 1, 24))

    def test_pick_refuses_oversized_sample(self):
        with self.assertRaises(SystemExit):
            pick(['a', 'b'], 1, 3)

    def test_score_exact_agreement_and_per_label_counts(self):
        gold = {'a': row('a', [(0, 4, 'NEW_VALUE')]),
                'b': row('b', [(0, 4, 'NEW_VALUE'), (5, 9, 'REFERENCE')], [(10, 18, 'UPDATE_CUE')])}
        reann = {'a': row('a', [(0, 4, 'NEW_VALUE')]),
                 'b': row('b', [(0, 4, 'NEW_VALUE'), (5, 9, 'KEPT_VALUE')], [(10, 18, 'UPDATE_CUE')])}
        rep = score_rows(gold, reann, ['a', 'b'])
        self.assertEqual(rep['exact_layer_set_agreement'], 0.5)
        self.assertEqual(rep['disagreeing_ids'], ['b'])
        per = rep['layers']['value_spans']['per_label']
        self.assertEqual((per['NEW_VALUE']['tp'], per['REFERENCE']['fn'], per['KEPT_VALUE']['fp']), (2, 1, 1))
        self.assertFalse(per['KEPT_VALUE']['evaluable'])  # no gold support -> never a score
        self.assertEqual(rep['layers']['cue_spans']['micro']['f1'], 1.0)

    def test_empty_records_agree(self):
        rep = score_rows({'a': row('a', [])}, {'a': row('a', [])}, ['a'])
        self.assertEqual(rep['exact_layer_set_agreement'], 1.0)
        self.assertIsNone(rep['layers']['value_spans']['micro']['f1'])


if __name__ == '__main__':
    unittest.main()
