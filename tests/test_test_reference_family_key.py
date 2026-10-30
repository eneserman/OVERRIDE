import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_test_reference import family_key  # noqa: E402
from evaluate_frozen_test import canonical_gold_sha256, check_manifest  # noqa: E402
from test_annotation_contracts import example  # noqa: E402


def namespaced_manifest(gold, splits):
    assignment = {family_key(r['source']['split'], r['dialogue_family_id']): s
                  for s, ids in splits.items() for r in gold if r['id'] in ids}
    m = {'splits': splits, 'family_key': 'official_split::dialogue_id (DEV-002)', 'family_assignment': assignment,
         'gold_content_sha256': canonical_gold_sha256(gold)}
    m['manifest_digest'] = hashlib.sha256(json.dumps(m, sort_keys=True).encode()).hexdigest()
    return m


class TestNamespacedManifest(unittest.TestCase):
    def setUp(self):
        self.gold = [example(i) for i in range(1, 4)]
        test = copy.deepcopy(example(1))  # same dialogue number as EX-1, but from the official dev split
        test['id'] = 'EX-T'
        test['source']['split'] = 'dev'
        self.gold.append(test)
        self.splits = {'train': ['EX-1', 'EX-2'], 'dev': ['EX-3'], 'test': ['EX-T']}

    def test_same_number_other_split_is_accepted(self):
        held = check_manifest(self.gold, namespaced_manifest(self.gold, self.splits))
        self.assertEqual([r['id'] for r in held], ['EX-T'])

    def test_real_leakage_is_rejected(self):
        gold = copy.deepcopy(self.gold)
        gold[-1]['source']['split'] = 'train'  # now truly the same family as EX-1
        manifest = namespaced_manifest(gold, self.splits)
        manifest['family_assignment'][family_key('train', 'family-1')] = 'train'
        unhashed = {k: v for k, v in manifest.items() if k != 'manifest_digest'}
        manifest['manifest_digest'] = hashlib.sha256(json.dumps(unhashed, sort_keys=True).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError, 'Family leakage'):
            check_manifest(gold, manifest)


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
