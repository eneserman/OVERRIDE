import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import jev_alt_laya as J  # noqa: E402


class FakeRouter:
    """Answers each marked word from a fixed word -> label map, in the shape Laya returns."""

    def __init__(self, roles, qtype="choice"):
        self.roles, self.qtype, self.states = roles, qtype, []

    def predict_batch(self, requests, batch_size=None, sort_by_length=False):
        out = []
        for req in requests:
            self.states.append(req["state"])
            word = req["state"].split("<<")[1].split(">>")[0]
            lab = self.roles.get(word, "O")
            if self.qtype == "choice":
                out.append({"answers": {"role": {"choice": lab}}})
            else:
                out.append({"answers": {k: {"noul": 0.9 if k == lab else 0.1} for k in J.NOUL}})
        return out


ROW = {"id": "x", "current_user_utterance": "Actually, make it 7 pm at the same place.",
       "history": [{"speaker": "USER", "utterance": "Book Friday at 6."}]}


class TestLayaAdapter(unittest.TestCase):
    def test_words_merge_into_spans_and_punctuation_is_never_asked(self):
        roles = {"Actually": "UPDATE_CUE", "7": "NEW_VALUE", "pm": "NEW_VALUE", "the": "REFERENCE",
                 "same": "REFERENCE", "place": "REFERENCE"}
        router = FakeRouter(roles)
        pred = J.predict(router, [ROW], "choice_en", 8)[0]
        self.assertEqual([(s["text"], s["label"]) for s in pred["value_spans"]],
                         [("7 pm", "NEW_VALUE"), ("the same place", "REFERENCE")])
        self.assertEqual([(s["text"], s["label"]) for s in pred["cue_spans"]], [("Actually", "UPDATE_CUE")])
        self.assertFalse(any("<<,>>" in s or "<<.>>" in s for s in router.states))

    def test_noul_needs_probability_above_half(self):
        self.assertEqual(J.word_label({k: {"noul": 0.4} for k in J.NOUL}, "noul"), "O")
        self.assertEqual(J.word_label({"UPDATE_CUE": {"noul": 0.7}, "NEW_VALUE": {"noul": 0.8},
                                       "REFERENCE": {"noul": 0.1}}, "noul"), "NEW_VALUE")

    def test_state_marks_exactly_the_target_word(self):
        words = [t._asdict() for t in J.tokenize(ROW["current_user_utterance"])]
        state = J.state_for(ROW, words, 4)
        self.assertIn("Current user turn: Actually, make it <<7>> pm at the same place.", state)
        self.assertIn("USER: Book Friday at 6.", state)


if __name__ == "__main__":
    unittest.main()
