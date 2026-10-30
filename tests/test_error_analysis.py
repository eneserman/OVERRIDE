import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from error_analysis import classify  # noqa: E402


def s(start, end, label):
    return {'start': start, 'end': end, 'label': label}


class TestErrorClasses(unittest.TestCase):
    def test_classes(self):
        gold = s(10, 20, 'NEW_VALUE')
        self.assertEqual(classify(gold, [s(10, 20, 'NEW_VALUE')]), 'exact')
        self.assertEqual(classify(gold, [s(10, 20, 'REFERENCE')]), 'label')
        self.assertEqual(classify(gold, [s(14, 20, 'NEW_VALUE')]), 'boundary')
        self.assertEqual(classify(gold, [s(14, 25, 'REFERENCE')]), 'overlap')
        self.assertEqual(classify(gold, [s(20, 25, 'NEW_VALUE')]), 'missing')  # touching is not overlapping


if __name__ == '__main__':
    unittest.main()
