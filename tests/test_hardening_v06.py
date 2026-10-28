"""Regression tests for OVERRIDE handoff safety invariants (synthetic only)."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from test_annotation_contracts import example
from test_review_packets import raw
from validate_annotations import validate_rows
from annotation_agreement import compare
from normalize_review_packet import normalize
from freeze_gold_splits import freeze

class HandoffSafetyTests(unittest.TestCase):
    def test_reject_future_history(self):
        r=example(1)
        r['history']=[{'speaker':'USER','utterance':'A future message', 'turn_index':3}]
        self.assertEqual(validate_rows([r],True)['status'],'FAIL')

    def test_reject_history_index_duplicates(self):
        r=example(1)
        r['history']=[{'speaker':'USER','utterance':'a','turn_index':0},{'speaker':'SYSTEM','utterance':'b','turn_index':0}]
        self.assertEqual(validate_rows([r],True)['status'],'FAIL')

    def test_reject_gold_without_independent_review(self):
        r=example(1);r['annotation']['reviewers']=['A','A']
        self.assertEqual(validate_rows([r],True)['status'],'FAIL')

    def test_reject_synthetic_gold(self):
        r=example(1);r['source']['dataset']='SYNTHETIC_NOT_SGD'
        self.assertEqual(validate_rows([r],True)['status'],'FAIL')

    def test_reject_mismatched_reviewer_text(self):
        a=normalize([raw()],'human_A')
        other=raw();other['current_user_utterance']='No, Paris!'
        other['annotation']['value_spans'][0]['text']='Paris'
        b=normalize([other],'human_B')
        with self.assertRaisesRegex(ValueError,'not comparable'):
            compare(a,b)

    def test_reject_same_reviewer_both_packets(self):
        a=normalize([raw()],'human_A')
        with self.assertRaisesRegex(ValueError,'same reviewer_id'):
            compare(a,copy.deepcopy(a))

    def test_frozen_gold_is_bound_to_labels(self):
        a=[example(i) for i in range(1,61)]
        m1=freeze(a)
        b=copy.deepcopy(a)
        b[0]['cue_spans']=[]
        m2=freeze(b)
        self.assertNotEqual(m1['gold_content_sha256'],m2['gold_content_sha256'])
        self.assertNotEqual(m1['manifest_digest'],m2['manifest_digest'])
        self.assertEqual(m1['splits'],m2['splits'])

    def test_pilot_cli_refuses_existing_nonempty_folder(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)/'existing';out.mkdir()
            marker=out/'annotator_A_UNLABELED.jsonl';marker.write_text('IMPORTANT HUMAN ANNOTATIONS',encoding='utf-8')
            p=subprocess.run([sys.executable,str(ROOT/'scripts'/'prepare_annotation_pilot.py'),
               '--sgd-root',root,'--out',str(out)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertEqual(marker.read_text(encoding='utf-8'),'IMPORTANT HUMAN ANNOTATIONS')

if __name__=='__main__':unittest.main()
