import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from mine_sgd_revision_candidates import detect_bucket, scan_dialogues, sample, write

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
