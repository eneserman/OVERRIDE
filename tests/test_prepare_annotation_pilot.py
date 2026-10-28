"""Small synthetic fixtures test annotation queue; not actual SGD statistics."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from prepare_annotation_pilot import annotator_record, classify, mine_raw, select_pilot

class PilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        folder = Path(self.tmp.name)
        self.file = folder / 'dialogues_001.json'
        def frame(city):
            return {'service': 'Flights_1', 'state':{'slot_values':{'city':[city]},'active_intent':'Search'}}
        def dialogue(did):
            return {'dialogue_id':did,'services':['Flights_1'],'turns':[
                {'speaker':'USER','utterance':'Book for Paris','frames':[frame('Paris')]},
                {'speaker':'SYSTEM','utterance':'Okay, which city?','frames':[]},
                {'speaker':'USER','utterance':'Actually make it Berlin','frames':[frame('Berlin')]},
                {'speaker':'SYSTEM','utterance':'Done','frames':[]},
                {'speaker':'USER','utterance':"Don't cancel it, keep Friday",'frames':[frame('Berlin')]},
            ]}
        self.file.write_text(json.dumps([dialogue('d1'),dialogue('d2'),dialogue('d3')]),encoding='utf8')

    def test_negated_cancellation_not_gold_cancel(self):
        self.assertEqual(classify(['possible_cancel_cue'], [], "Don't cancel it", True), 'NEGATED_CANCEL_CUE')

    def test_no_gold_state_exposure(self):
        records, inventory = mine_raw([self.file], 5)
        self.assertEqual(inventory['distinct_dialogues'],3)
        example = next(r for r in records if 'Berlin' in r['utterance'])
        blind = annotator_record(example)
        raw = json.dumps(blind)
        self.assertNotIn('state_change_candidates', raw)
        self.assertNotIn('slot_values', raw)
        self.assertEqual(blind['annotation']['status'],'UNLABELED')
        self.assertIsNone(blind['annotation']['value_spans'])
        self.assertTrue(all(t['turn_index'] < blind['source']['turn_index'] for t in blind['history']))

    def test_determinism_group_exclusion_and_shortfall(self):
        records, _ = mine_raw([self.file],4)
        selected, meta = select_pilot(records,100,42)
        self.assertEqual(meta['actual_selected'],3)
        self.assertEqual(len(set(r['source']['dialogue_id'] for r in selected)),len(selected))
        self.assertEqual([r['example_id'] for r in selected], [r['example_id'] for r in select_pilot(records,100,42)[0]])

    def test_cli_outputs_separate_blinded_packets(self):
        root = Path(self.tmp.name)
        (root/'train').mkdir(exist_ok=True)
        (root/'train'/'dialogues_001.json').write_bytes(self.file.read_bytes())
        out = root/'out'
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'prepare_annotation_pilot.py'
        result = subprocess.run([sys.executable, str(script), '--sgd-root', str(root),
                                 '--out', str(out), '--sample-size', '2'],
                                capture_output=True, text=True, check=True)
        self.assertIn('UNLABELED cases', result.stdout)
        self.assertTrue((out/'pilot_sampling_summary.json').exists())
        self.assertTrue((out/'PRIVATE_sampling_manifest.jsonl').exists())
        a=(out/'annotator_A_UNLABELED.jsonl').read_bytes()
        b=(out/'annotator_B_UNLABELED.jsonl').read_bytes()
        self.assertEqual(a,b)
        self.assertNotIn(b'state_change_candidates', a)
        self.assertNotIn(b'slot_values', a)

    def test_no_future_turn_context(self):
        records, _ = mine_raw([self.file],8)
        r = next(r for r in records if 'Berlin' in r['utterance'])
        self.assertEqual(len(r['history']),2)
        self.assertEqual(r['history'][-1]['utterance'],'Okay, which city?')

if __name__ == '__main__':
    unittest.main()
