import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from normalize_review_packet import normalize
from annotation_agreement import compare


def raw():
    return {'example_id':'SAMPLE-1','source':{'dataset':'SGD','split':'train','dialogue_id':'d1','turn_index':2,'service':'Flight_1'},
            'history':[{'speaker':'USER','utterance':'Go to Berlin'}],
            'current_user_utterance':'No, Paris.',
            'annotation':{'status':'ANNOTATED','guideline_version':'pilot_v0.1',
                          'value_spans':[{'start':4,'end':9,'text':'Paris','label':'NEW_VALUE'}],
                          'cue_spans':[],'transitions':[]}}

class ReviewPacketsTest(unittest.TestCase):
    def test_normalization_keeps_non_gold(self):
        rows=normalize([raw()],'human_A')
        self.assertEqual(rows[0]['annotation']['status'],'ANNOTATED')
        self.assertEqual(rows[0]['value_spans'][0]['text'],'Paris')
    def test_unreviewed_refused(self):
        r=raw();r['annotation']['status']='UNLABELED'
        with self.assertRaises(ValueError):normalize([r],'human_A')
    def test_layer_agreement_counts(self):
        a=normalize([raw()],'human_A');b=normalize([raw()],'human_B')
        rep=compare(a,b)
        self.assertEqual(rep['exact_layer_set_agreement'],1.0)
    def test_disagreement_reported(self):
        a=normalize([raw()],'human_A')
        r=raw();r['annotation']['value_spans']=[]
        b=normalize([r],'human_B')
        rep=compare(a,b)
        self.assertEqual(len(rep['disagreements']),1)

if __name__=='__main__':unittest.main()
