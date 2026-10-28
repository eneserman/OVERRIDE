import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_annotations import validate_rows
from freeze_gold_splits import freeze
from evaluate_spans import evaluate


def example(i:int):
    txt='Actually Paris, but keep Friday.'
    return {
      'id':f'EX-{i}',
      'source':{'dataset':'SGD','split':'train','dialogue_id':f'family-{i}','turn_index':2,'service':'Flight_1'},
      'dialogue_family_id':f'family-{i}',
      'history':[{'speaker':'USER','utterance':'Berlin Friday'}],
      'current_user_utterance':txt,
      'value_spans':[{'start':9,'end':14,'text':'Paris','label':'NEW_VALUE'},{'start':25,'end':31,'text':'Friday','label':'KEPT_VALUE'}],
      'cue_spans':[{'start':0,'end':8,'text':'Actually','label':'UPDATE_CUE'},{'start':20,'end':24,'text':'keep','label':'KEEP_CUE'}],
      'annotation':{'status':'ADJUDICATED','guideline_version':'v0.1', 'reviewers':['human_A','human_B'], 'adjudication_log_id':f'adjudication-{i}'},
    }

class AnnotationContractsTest(unittest.TestCase):
    def test_valid_synthetic_gold(self):
        self.assertEqual(validate_rows([example(1)],True)['status'],'PASS')
    def test_invalid_offset(self):
        row=example(1);row['value_spans'][0]['end']=15
        self.assertEqual(validate_rows([row],True)['status'],'FAIL')
    def test_same_head_overlap(self):
        row=example(1);row['value_spans'].append({'start':12,'end':15,'text':'is,','label':'OLD_VALUE'})
        self.assertEqual(validate_rows([row],True)['status'],'FAIL')
    def test_non_gold_rejected(self):
        row=example(1);row['annotation']['status']='UNREVIEWED'
        self.assertEqual(validate_rows([row],True)['status'],'FAIL')
    def test_split_deterministic_group_safe(self):
        rows=[example(i) for i in range(1,51)]
        a=freeze(rows,42);b=freeze(rows,42)
        self.assertEqual(a,b)
        self.assertEqual(set(a['splits']['train']) & set(a['splits']['test']),set())
        self.assertEqual(sum(len(x) for x in a['splits'].values()),50)
    def test_scoring_identical(self):
        g=[example(1)]
        p=[{'id':'EX-1','value_spans':[{'start':9,'end':14,'label':'NEW_VALUE'},{'start':25,'end':31,'label':'KEPT_VALUE'}],
              'cue_spans':[{'start':0,'end':8,'label':'UPDATE_CUE'},{'start':20,'end':24,'label':'KEEP_CUE'}]}]
        result=evaluate(g,p)
        self.assertEqual(result['layers']['value_spans']['micro']['f1'],1.0)
        self.assertEqual(result['layers']['cue_spans']['micro']['f1'],1.0)
    def test_scoring_rejects_missing_id(self):
        with self.assertRaises(ValueError):evaluate([example(1)],[])

if __name__=='__main__':unittest.main()

# Additional regression cases: do not let malformed annotations crash validators
# or silently score impossible overlapping predictions.
class InvalidInputRegressionTest(unittest.TestCase):
    def test_invalid_source_type_returns_error(self):
        row=example(3);row['source']=None
        self.assertEqual(validate_rows([row],True)['status'],'FAIL')
    def test_unhashable_invalid_id_returns_error(self):
        row=example(3);row['id']=['bad']
        self.assertEqual(validate_rows([row],True)['status'],'FAIL')
    def test_predicted_same_layer_overlap_rejected(self):
        g=[example(4)]
        p=[{'id':'EX-4','value_spans':[{'start':9,'end':14,'label':'NEW_VALUE'},{'start':12,'end':15,'label':'OLD_VALUE'}], 'cue_spans':[]}]
        with self.assertRaises(ValueError):evaluate(g,p)
