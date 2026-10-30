"""Tests for the D3-EXT round-2 cross packets: only clean blind rows, deterministic per-reviewer order."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_ext2_packets import cross_packet  # noqa: E402


def blind(rid, labeled=False):
    return {'example_id': rid, 'source': {}, 'history': [], 'current_user_utterance': 'x',
            'annotation': {'status': 'ANNOTATED' if labeled else 'UNLABELED', 'value_spans': None, 'cue_spans': None}}


class CrossPacketTests(unittest.TestCase):
    def test_selects_only_requested_ids_in_stable_order(self):
        rows = [blind(f'R{i}') for i in range(6)]
        a = cross_packet(rows, ['R1', 'R3', 'R5'], 'A', seed=1)
        self.assertEqual(sorted(r['example_id'] for r in a), ['R1', 'R3', 'R5'])
        self.assertEqual(a, cross_packet(list(reversed(rows)), ['R5', 'R3', 'R1'], 'A', seed=1))

    def test_refuses_labeled_or_missing_rows(self):
        with self.assertRaises(SystemExit):
            cross_packet([blind('R1', labeled=True)], ['R1'], 'A')
        with self.assertRaises(SystemExit):
            cross_packet([blind('R1')], ['R2'], 'A')


if __name__ == '__main__':
    unittest.main()
