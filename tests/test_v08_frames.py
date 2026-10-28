import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from extract_frames_candidates import extract
from inspect_upstream_provenance import inspect

class TestFramesExtraction(unittest.TestCase):
    def test_blinded_and_backward_only(self):
        with tempfile.TemporaryDirectory() as td:
            file=Path(td)/'frames.json'
            file.write_text(json.dumps([{'id':'trip1','turns':[
                {'author':'user','text':'I want Paris.'},
                {'author':'wizard','text':'Okay.'},
                {'author':'user','text':'Go back to the first option, please.'},
                {'author':'wizard','text':'Confirmed.'},
                {'author':'user','text':'Actually keep the date.'}]}]))
            rows,meta=extract(file,limit=5,seed=3)
            self.assertEqual(len(rows),2)
            for r in rows:
                self.assertEqual(r['source']['dataset'],'FRAMES')
                self.assertIsNone(r['annotation']['value_spans'])
                self.assertTrue(all(h['turn_index']<r['source']['turn_index'] for h in r['history']))
            self.assertEqual(meta['dialogue_count'],1)
    def test_missing_source_refuses(self):
        with self.assertRaises(ValueError):inspect(Path('/tmp/not_a_real_sgd_source_foo_1337'))
if __name__=='__main__':unittest.main()
