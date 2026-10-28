import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lock_prospective_holdout import create_lock, verify_lock
from run_synthetic_token_baseline import tokenize, gold_tags,decode,metrics

class TestV08Research(unittest.TestCase):
    def source(self, id, dialog, split='test', txt='Change the destination to Paris.', turn=2):
        return {'example_id':id,'current_user_utterance':txt,'source':{
            'dataset':'SGD','split':split,'dialogue_id':dialog,'turn_index':turn},
            'history':[{'speaker':'USER','turn_index':0,'utterance':'Berlin please.'}],
            'annotation':{'status':'UNLABELED','cue_spans':None,'value_spans':None,'transitions':None}}
    def write(self,p,records):
        p.write_text(''.join(json.dumps(x)+'\n' for x in records),encoding='utf-8')
    def test_prospective_lock_and_verify(self):
        with TemporaryDirectory() as d:
            p=Path(d);pool=p/'pool.jsonl';seen=p/'seen.jsonl'
            self.write(seen,[self.source('old','TRAIN-0','train','Please book tickets.')]);
            self.write(pool,[self.source('new','TEST-1')]);
            manifest=create_lock(pool,[seen],'abcdef012345','VERIFIED')
            self.assertEqual(manifest['counts']['candidate_examples'],1)
            self.assertTrue(verify_lock(pool,[seen],manifest))
            self.assertEqual(manifest['status'],'RAW_POOL_LOCKED_NOT_HUMAN_GOLD')
            self.write(pool,[self.source('new','TEST-1',txt='Change it to Rome.')])
            with self.assertRaises(ValueError):verify_lock(pool,[seen],manifest)
    def test_reject_seen_family(self):
        with TemporaryDirectory() as d:
            p=Path(d);pool=p/'p.jsonl';seen=p/'s.jsonl'
            self.write(seen,[self.source('a','X','train')]);
            self.write(pool,[self.source('b','X','dev','Go back.')]);
            with self.assertRaises(ValueError):create_lock(pool,[seen],'abcdef012345','VERIFIED')
    def test_reject_train_split(self):
        with TemporaryDirectory() as d:
            p=Path(d);pool=p/'p.jsonl';seen=p/'s.jsonl'
            self.write(seen,[self.source('a','X','train')]);
            self.write(pool,[self.source('b','Y','train','Go back.')]);
            with self.assertRaises(ValueError):create_lock(pool,[seen],'abcdef012345','VERIFIED')
    def test_reject_future_context(self):
        with TemporaryDirectory() as d:
            p=Path(d);pool=p/'p.jsonl';seen=p/'s.jsonl'
            self.write(seen,[self.source('a','X','train')]);
            item=self.source('b','Y','test','No, use Paris.');item['history'][0]['turn_index']=3
            self.write(pool,[item]);
            with self.assertRaises(ValueError):create_lock(pool,[seen],'abcdef012345','VERIFIED')
    def test_decode_and_f1(self):
        toks=tokenize('No, change to Paris!');tags=['O','O','B-UPDATE_CUE','O','B-NEW_VALUE','O'];
        self.assertEqual(decode(tags,toks)[-1]['start'],14)
        m=metrics([[{'start':14,'end':19,'label':'NEW_VALUE'}]],[[{'start':14,'end':19,'label':'NEW_VALUE'}]])
        self.assertEqual(m['strict_micro_f1'],1.0)
    def test_invalid_boundary_raises(self):
        r={'id':'x','current_user_utterance':'New York',
           'value_spans':[{'start':1,'end':4,'text':'ew ','label':'NEW_VALUE'}]}
        with self.assertRaises(ValueError):gold_tags(r,tokenize('New York'),'value_spans')

if __name__=='__main__':unittest.main()
