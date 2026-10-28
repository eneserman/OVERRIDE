import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_synthetic_bootstrap import CATEGORIES, generate, make, validate_record, V_LABELS, C_LABELS
from mine_sgd_revision_candidates import detect_bucket, scan_dialogues, sample, write
from build_ai_review_triage import run as triage
from audit_research_dataset import audit

ROOT=Path(__file__).resolve().parents[1]

class SyntheticTests(unittest.TestCase):
    def test_counts_and_every_category(self):
        d=generate()
        self.assertEqual({s:len(x) for s,x in d.items()},{'train':504,'dev':126,'challenge':126})
        for split, rs in d.items():
            self.assertEqual(set(CATEGORIES),{x['source']['recipe_id'] for x in rs})
    def test_exact_offsets_full_corpus(self):
        for rs in generate().values():
            for r in rs:self.assertTrue(validate_record(r))
    def test_all_eight_labels_on_train(self):
        rs=generate()['train']; got={s['label'] for r in rs for k in ('value_spans','cue_spans') for s in r[k]}
        self.assertEqual(got,V_LABELS|C_LABELS)
    def test_template_families_heldout(self):
        d=generate(); families={split:{r['source']['template_family'] for r in rs} for split,rs in d.items()}
        for a in d:
            for b in d:
                if a!=b:self.assertFalse(families[a]&families[b])
    def test_reproducibility(self):
        self.assertEqual(generate(),generate())
    def test_negated_cancel_has_no_cancel_operation(self):
        d=generate(); rs=[r for rows in d.values() for r in rows if r['source']['recipe_id']=='negated_cancel_update']
        self.assertTrue(all('CANCEL_INTENT' not in [t['operation'] for t in r['transitions']] for r in rs))
        self.assertTrue(all(any(c['polarity']=='NEGATED' and c['label']=='CANCEL_CUE' for c in r['cue_spans']) for r in rs))
    def test_add_is_not_update(self):
        for r in generate()['train']:
            if r['source']['recipe_id']=='add_preference':
                self.assertEqual([x['operation'] for x in r['transitions']],['ADD'])
    def test_restore_backward_ref_target(self):
        for r in generate()['challenge']:
            if r['source']['recipe_id']=='restore_reference':
                self.assertEqual(r['links'][0]['target_turn_index'],0)
                self.assertTrue(r['links'][0]['resolved_value'] in r['history'][0]['utterance'])
    def test_syn_not_gold(self):
        self.assertTrue(all(not r['annotation']['is_gold'] for z in generate().values() for r in z))
    def test_bad_offset_rejected(self):
        import copy
        a=next(r for r in generate()['train'] if r['value_spans']); b=copy.deepcopy(a);b['value_spans'][0]['end']+=1
        with self.assertRaises(AssertionError):validate_record(b)
    def test_gold_gate_is_off(self):
        out=audit(ROOT)
        self.assertTrue(out['structural_pass']);self.assertFalse(out['academic_gold_ready'])
        self.assertEqual(out['sgd_pilot']['examples'],100)

class MinerTests(unittest.TestCase):
    def test_buckets(self):
        self.assertEqual(detect_bucket('Actually change it',[(1,2)])[0],'UPDATE')
        self.assertEqual(detect_bucket('Please keep Friday and change city',[1,2])[0],'MIXED')
    def test_mine_toy_dialogue(self):
        with tempfile.TemporaryDirectory() as t:
            folder=Path(t)/'train';folder.mkdir()
            ds=[{'dialogue_id':f'd-{j}','services':['Flights_1'],'turns':[
               {'speaker':'USER','utterance':f'Book my trip to Rome on day {j}.'},
               {'speaker':'SYSTEM','utterance':'Okay.'},
               {'speaker':'USER','utterance':f'Actually change that to Paris {j}.'}]} for j in range(4)]
            (folder/'dialogues_001.json').write_text(json.dumps(ds),encoding='utf-8')
            records,obs,per=scan_dialogues(t)
            self.assertEqual(len(records),8)
            chosen,picked=sample(records,per_bucket=2,seed=0)
            self.assertEqual(len({x[3]['source']['dialogue_id'] for x in chosen}),len(chosen))
            result=write(Path(t)/'pack',chosen,obs,per,picked,'train',0)
            self.assertEqual(result['selected'],len(chosen))
            A=(Path(t)/'pack'/'reviewer_A_BLIND.jsonl').read_bytes()
            B=(Path(t)/'pack'/'reviewer_B_BLIND.jsonl').read_bytes()
            self.assertEqual(A,B)
            self.assertNotIn(b'mining_bucket',A)
            with self.assertRaises(FileExistsError):write(Path(t)/'pack',chosen,obs,per,picked,'train',0)

if __name__=='__main__': unittest.main()
