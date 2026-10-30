"""Tests for the D3-EXT packet builder: exclusions, quotas, one-per-dialogue, deterministic assignment."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_ext_packets import assign, norm, select  # noqa: E402


def cand(bucket: str, i: int, did: str, text: str):
    rec = {'example_id': f'SGD-{i:04d}', 'current_user_utterance': text,
           'source': {'split': 'train', 'dialogue_id': did}, 'history': [],
           'annotation': {'status': 'UNLABELED'}}
    return (bucket, (), 'svc', rec)


class ExtPacketTests(unittest.TestCase):
    def test_norm_ignores_case_and_punctuation(self):
        self.assertEqual(norm('No, Actually -- 2 rooms!'), 'no actually 2 rooms')

    def test_select_excludes_seen_family_text_and_duplicates(self):
        rows = [cand('UPDATE', 1, 'd1', 'change it'), cand('UPDATE', 2, 'seen', 'other text'),
                cand('UPDATE', 3, 'd3', 'Seen sentence.'), cand('UPDATE', 4, 'd1', 'second in d1'),
                cand('UPDATE', 5, 'd5', 'CHANGE IT'), cand('UPDATE', 6, 'd6', 'fresh one')]
        chosen = select(rows, families={'seen'}, texts={'seen sentence'}, raw_shas=set(),
                        quotas={'UPDATE': 2}, seed=1)
        ids = {r[3]['example_id'] for r in chosen}
        dids = [r[3]['source']['dialogue_id'] for r in chosen]
        self.assertEqual(len(chosen), 2)
        self.assertEqual(len(set(dids)), 2)
        self.assertFalse(ids & {'SGD-0002', 'SGD-0003'})
        self.assertFalse({'SGD-0001', 'SGD-0005'} <= ids)  # normalized duplicates never both

    def test_select_fails_closed_when_quota_cannot_be_met(self):
        with self.assertRaises(SystemExit):
            select([cand('KEEP', 1, 'd1', 'keep it')], set(), set(), set(), quotas={'KEEP': 2}, seed=1)

    def test_assign_is_deterministic_and_partitions(self):
        chosen = [cand('UPDATE', i, f'd{i}', f't{i}') for i in range(10)]
        a, b = assign(chosen, shared={'UPDATE': 2}, seed=7), assign(list(reversed(chosen)), shared={'UPDATE': 2}, seed=7)
        self.assertEqual(a, b)
        all_ids = a['shared'] + a['A'] + a['B']
        self.assertEqual(len(all_ids), 10)
        self.assertEqual(len(set(all_ids)), 10)
        self.assertEqual((len(a['shared']), len(a['A']), len(a['B'])), (2, 4, 4))


if __name__ == '__main__':
    unittest.main()
