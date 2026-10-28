"""Synthetic regression tests for locked test split evaluation."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from test_annotation_contracts import example
from freeze_gold_splits import freeze
from evaluate_frozen_test import check_manifest
from evaluate_spans import evaluate

class FrozenEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gold=[example(i) for i in range(1,61)]
        cls.manifest=freeze(cls.gold)

    def test_selection_only_test_ids(self):
        heldout=check_manifest(self.gold,self.manifest)
        self.assertEqual({r['id'] for r in heldout},set(self.manifest['splits']['test']))
        self.assertFalse({r['id'] for r in heldout} & set(self.manifest['splits']['train']))

    def test_reject_modified_gold(self):
        changed=copy.deepcopy(self.gold)
        changed[0]['cue_spans']=[]
        with self.assertRaisesRegex(ValueError,'gold SHA-256'):
            check_manifest(changed,self.manifest)

    def test_reject_modified_manifest(self):
        modified=copy.deepcopy(self.manifest)
        modified['seed']+=1
        with self.assertRaisesRegex(ValueError,'manifest digest'):
            check_manifest(self.gold,modified)

    def test_reject_split_leakage(self):
        modified=copy.deepcopy(self.manifest)
        rid=modified['splits']['train'][0]
        modified['splits']['test'].append(rid)
        # Rehash so that tampering is detected by the structural partition, not checksum alone.
        import hashlib,json
        modified['manifest_digest']=hashlib.sha256(json.dumps({k:v for k,v in modified.items() if k!='manifest_digest'},sort_keys=True).encode()).hexdigest()
        with self.assertRaisesRegex(ValueError,'partition'):
            check_manifest(self.gold,modified)

    def test_evaluator_rejects_training_ids(self):
        heldout=check_manifest(self.gold,self.manifest)
        preds=[{'id':i,'value_spans':[], 'cue_spans':[]} for i in self.manifest['splits']['train']]
        with self.assertRaisesRegex(ValueError,'Prediction IDs'):
            evaluate(heldout,preds)

if __name__=='__main__':unittest.main()
