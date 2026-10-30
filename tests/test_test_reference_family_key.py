import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_test_reference import family_key  # noqa: E402


class TestFamilyKey(unittest.TestCase):
    def test_same_number_in_different_official_splits_is_not_the_same_family(self):
        # SGD restarts numbering per split: train 10_00028 and dev 10_00028 are different dialogues (DEV-002)
        self.assertNotEqual(family_key('train', '10_00028'), family_key('dev', '10_00028'))

    def test_same_split_same_number_is_the_same_family(self):
        self.assertEqual(family_key('test', '23_00076'), family_key('test', '23_00076'))

    def test_leakage_still_detected_within_a_split(self):
        train = {family_key('train', d) for d in ('1_00001', '2_00002')}
        test = {family_key('train', '2_00002')}
        self.assertTrue(train & test)


if __name__ == '__main__':
    unittest.main()
