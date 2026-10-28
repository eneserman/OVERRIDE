"""Unit tests use fabricated toy SGD records, NEVER described as official SGD results."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from audit_sgd import inspect_dataset, normalized_set, state_deltas  # noqa: E402


class SgdAuditTests(unittest.TestCase):
    def test_state_candidates_are_not_gold(self):
        diff = state_deltas({'city':['Paris'], 'day':['Friday']}, {'city':['Rome'],'day':['Friday'], 'party':['3']})
        self.assertEqual([(x['slot'], x['kind']) for x in diff], [
            ('city','SLOT_CHANGED_CANDIDATE'), ('party','SLOT_ADDED_CANDIDATE')
        ])

    def test_alias_variations(self):
        self.assertEqual(normalized_set([' 6 PM ', 'evening at 6']), frozenset({'6 pm','evening at 6'}))
        self.assertEqual(state_deltas({'time':['6 pm']},{'time':['6 PM', 'evening at 6']})[0]['kind'],
                         'ALIAS_OR_STATE_VARIANT_CANDIDATE')

    def test_offsets_and_missing_original_fields(self):
        data = [{
            'dialogue_id':'synthetic_1', 'services':['Travel_1'], 'turns':[
                {'speaker':'USER','utterance':'Go to Paris','frames':[
                    {'service':'Travel_1','slots':[{'slot':'city','start':6,'exclusive_end':11}],
                     'state':{'active_intent':'Search','slot_values':{'city':['Paris']},'requested_slots':[]}}]},
                {'speaker':'SYSTEM','utterance':'Okay','frames':[]},
                {'speaker':'USER','utterance':'Actually Rome','frames':[
                    {'service':'Travel_1','slots':[{'slot':'city','start':9,'exclusive_end':13}],
                     'state':{'active_intent':'Search','slot_values':{'city':['Rome']},'requested_slots':[]}}]},
            ]
        }]
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'dialogues_001.json'
            file.write_text(json.dumps(data),encoding='utf-8')
            report,candidates = inspect_dataset([file],'train')
        self.assertEqual(report['counts']['dialogues'],1)
        self.assertEqual(report['counts']['valid_span_offsets'],2)
        self.assertEqual(report['counts']['SLOT_CHANGED_CANDIDATE'],1)
        self.assertEqual(candidates[0]['provenance'],'SGD_STATE_DIFF_UNREVIEWED_NOT_GOLD')


if __name__ == '__main__':
    unittest.main()
