"""Tests for scripts/annotation_entry_helper.py (human data-entry facilitation).

The helper must NEVER invent labels: every span comes from a human-typed phrase.
These tests cover the mechanical layer (offsets, vocabulary, overlap, contract
compatibility) on synthetic fixtures only.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from annotation_entry_helper import (  # noqa: E402
    EntryError,
    check_same_layer_overlap,
    fill_record,
    find_occurrences,
    make_span,
    write_jsonl,
)
from normalize_review_packet import normalize  # noqa: E402
from validate_annotations import validate_rows  # noqa: E402

UTT = "Actually Paris, but keep Friday."


def packet_record():
    return {
        "example_id": "syn-001",
        "source": {
            "dataset": "SGD",
            "split": "train",
            "dialogue_id": "synthetic-family",
            "turn_index": 2,
            "service": "Flight_1",
        },
        "dialogue_family_id": "synthetic-family",
        "history": [
            {"speaker": "USER", "turn_index": 0, "utterance": "Two people to Berlin on Friday."},
            {"speaker": "SYSTEM", "turn_index": 1, "utterance": "Flying to Berlin on Friday."},
        ],
        "current_user_utterance": UTT,
        "annotation": {
            "status": "UNLABELED",
            "guideline_version": "pilot_v0.1",
            "value_spans": None,
            "cue_spans": None,
            "transitions": None,
            "uncertainty_notes": None,
        },
    }


class SpanMechanicsTest(unittest.TestCase):
    def test_find_occurrences_single_and_multiple(self):
        self.assertEqual(find_occurrences(UTT, "Paris"), [9])
        self.assertEqual(find_occurrences("go back to Paris and back to Berlin", "back to"), [3, 21])
        self.assertEqual(find_occurrences(UTT, "zzz"), [])

    def test_find_occurrences_rejects_empty_phrase(self):
        with self.assertRaises(EntryError):
            find_occurrences(UTT, "")

    def test_make_span_offsets_match_slice(self):
        span = make_span(UTT, "Paris", "NEW_VALUE")
        self.assertEqual((span["start"], span["end"]), (9, 14))
        self.assertEqual(UTT[span["start"]:span["end"]], span["text"])

    def test_make_span_occurrence_selection(self):
        utt = "back to Paris, back to Berlin"
        self.assertEqual(find_occurrences(utt, "back to"), [0, 15])
        span = make_span(utt, "back to", "RESTORE_CUE", occurrence=2)
        self.assertEqual((span["start"], span["end"]), (15, 22))
        self.assertEqual(utt[span["start"]:span["end"]], "back to")

    def test_make_span_unicode_offsets_are_characters(self):
        utt = "Actually İstanbul, not Ankara."
        span = make_span(utt, "İstanbul", "NEW_VALUE")
        self.assertEqual(utt[span["start"]:span["end"]], "İstanbul")

    def test_make_span_unknown_label_and_bad_occurrence(self):
        with self.assertRaises(EntryError):
            make_span(UTT, "Paris", "CITY")
        with self.assertRaises(EntryError):
            make_span(UTT, "Paris", "NEW_VALUE", occurrence=2)
        with self.assertRaises(EntryError):
            make_span(UTT, "zzz", "NEW_VALUE")

    def test_same_layer_overlap_rejected(self):
        spans = [make_span(UTT, "Paris", "NEW_VALUE"), make_span(UTT, "aris", "OLD_VALUE")]
        with self.assertRaises(EntryError):
            check_same_layer_overlap(spans)
        check_same_layer_overlap([make_span(UTT, "Paris", "NEW_VALUE"),
                                  make_span(UTT, "Friday", "KEPT_VALUE")])  # touching ok


class FillRecordTest(unittest.TestCase):
    def test_filled_record_passes_non_gold_contract(self):
        filled = fill_record(
            packet_record(), "reviewer_A_test",
            [make_span(UTT, "Paris", "NEW_VALUE"), make_span(UTT, "Friday", "KEPT_VALUE")],
            [make_span(UTT, "Actually", "UPDATE_CUE"), make_span(UTT, "keep", "KEEP_CUE")],
            [{"operation": "UPDATE", "slot": "city", "before": None, "after": "Paris"}],
            [], "L2", "",
        )
        self.assertEqual(filled["annotation"]["status"], "ANNOTATED")
        canonical = normalize([filled], "reviewer_A_test")
        self.assertEqual(validate_rows(canonical, require_gold=False)["status"], "PASS")

    def test_filled_record_is_never_gold(self):
        filled = fill_record(packet_record(), "reviewer_A_test", [], [], [], [], None, "looked twice, nothing")
        canonical = normalize([filled], "reviewer_A_test")
        self.assertEqual(validate_rows(canonical, require_gold=True)["status"], "FAIL")

    def test_reviewed_negative_is_empty_lists_not_null(self):
        filled = fill_record(packet_record(), "reviewer_A_test", [], [], [], [], None, "")
        self.assertEqual(filled["annotation"]["value_spans"], [])
        self.assertEqual(filled["annotation"]["cue_spans"], [])

    def test_fill_record_rejects_missing_reviewer_and_bad_inputs(self):
        with self.assertRaises(EntryError):
            fill_record(packet_record(), "  ", [], [], [], [], None, "")
        with self.assertRaises(EntryError):
            fill_record(packet_record(), "reviewer_A_test", [], [], [], [], "L9", "")
        with self.assertRaises(EntryError):
            fill_record(packet_record(), "reviewer_A_test",
                        [make_span(UTT, "Paris", "NEW_VALUE"), make_span(UTT, "aris", "OLD_VALUE")],
                        [], [], [], None, "")


class WriteSafetyTest(unittest.TestCase):
    def test_write_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "filled.jsonl")
            write_jsonl(path, [packet_record()])
            with self.assertRaises(EntryError):
                write_jsonl(path, [packet_record()])


class CliEndToEndTest(unittest.TestCase):
    """Runs the actual CLI with scripted stdin (regression: --packet/--out must be Paths)."""

    def test_cli_walks_packet_and_saves(self):
        scripts_dir = os.path.join(os.path.dirname(__file__), "..", "scripts")
        with tempfile.TemporaryDirectory() as tmp:
            packet = os.path.join(tmp, "packet.jsonl")
            rows = [packet_record(), packet_record()]
            rows[1]["example_id"] = "syn-002"
            rows[1]["source"]["dialogue_id"] = "synthetic-family-2"
            rows[1]["dialogue_family_id"] = "synthetic-family-2"
            with open(packet, "w", encoding="utf-8") as fh:
                for r in rows:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
            out = os.path.join(tmp, "filled.jsonl")
            r = subprocess.run(
                [sys.executable, os.path.join(scripts_dir, "annotation_entry_helper.py"),
                 "--packet", packet, "--reviewer-id", "reviewer_A_test",
                 "--out", out],
                input="k\nq\n", capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(os.path.exists(out))
            saved = [json.loads(x) for x in open(out, encoding="utf-8").read().splitlines() if x.strip()]
            self.assertEqual(len(saved), 1)  # one reviewed-negative saved, then quit
            self.assertEqual(saved[0]["annotation"]["status"], "ANNOTATED")
            self.assertEqual(saved[0]["annotation"]["value_spans"], [])


if __name__ == "__main__":
    unittest.main()
