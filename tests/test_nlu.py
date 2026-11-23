import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import numpy as np

from relay_intake import extract
from relay_interpretation import active_notice_model, interpret, interpret_notice, sent_date, visible_text
from relay_nlu import FIELDS, NoticeModel, Prediction, Span, decode_spans, deployed_model, tokens


SOCCER = ("Hey, soccer practice is Tuesday at 5 PM. Bring cleats and water. "
          "Meet Coach Alex at the community field by 4:45.")


class NoticeModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = deployed_model()
        assert cls.model is not None

    def test_learned_model_recovers_conversational_soccer_plan(self):
        values, evidence = interpret(SOCCER, ["Coach Alex", "Sam"], "2026-11-23", self.model)
        self.assertEqual(values, {
            "title": "soccer practice", "date": "2026-11-24", "time": "17:00",
            "location": "the community field", "preparation": "cleats and water",
            "instructions": "Meet Coach Alex at the community field by 4:45.",
        })
        self.assertEqual(evidence["_model"]["kind"], "sports")
        self.assertEqual(evidence["date"]["anchor"], "2026-11-23")
        for entry in evidence["location"]["evidence"]:
            self.assertEqual(SOCCER[entry["start"]:entry["end"]], entry["value"])
        self.assertGreaterEqual(evidence["location"]["confidence"], .75)

    def test_relative_date_requires_anchor_and_does_not_schedule_the_start(self):
        values, evidence = interpret(SOCCER, [], "", self.model)
        self.assertNotIn("date", values)
        self.assertNotIn("time", values)
        self.assertEqual(evidence["time"]["candidate"], "17:00")

    def test_low_confidence_and_ambiguous_roster_are_review_only(self):
        text = "Maybe Sam will take Mia to practice"

        class FixtureModel:
            def predict(self, text, members):
                return Prediction("sports", .9, "schedule", .9,
                                  (Span("responsibility", 6, 9, .95), Span("person", 20, 23, .64)))

        values, evidence = interpret(text, ["Sam Lee", "Sam Wang", "Mia"], "", FixtureModel())
        self.assertNotIn("responsibility", values)
        self.assertNotIn("person", values)
        self.assertEqual(evidence["responsibility"]["status"], "needs_context")
        self.assertEqual(evidence["person"]["status"], "low_confidence")

    def test_learned_cancellation_does_not_turn_old_date_into_a_plan(self):
        text = "Spring concert was called off. Please do not go to Room 12 at 5 PM.\nDate: 2026-12-04"
        values, evidence = interpret(text, (), "2026-11-23", self.model)
        self.assertEqual(evidence["_model"]["intent"], "cancel")
        self.assertNotIn("date", values)
        self.assertNotIn("time", values)

    def test_due_date_does_not_become_the_event_date(self):
        text = "Quick reminder—library book return is due Wednesday. Bring the library card."
        values, evidence = interpret(text, (), "2026-11-23", self.model)
        self.assertNotIn("date", values)
        self.assertEqual(values["deadline"], "2026-11-25")
        self.assertEqual(evidence["deadline"]["evidence"][0]["value"], "Wednesday")

    def test_appointment_binds_caregiver_and_affected_person_as_different_roles(self):
        text = "Please have Jules drive Amelia to her eye exam on Monday at 2 PM."
        values, evidence = interpret(text, ("Jules", "Amelia"), "2026-11-23", self.model)
        self.assertEqual(evidence["_model"]["kind"], "appointment")
        self.assertEqual((values["person"], values["responsibility"]), ("Amelia", "Jules"))

    def test_quotes_and_mail_headers_are_masked_without_shifting_offsets(self):
        text = "From: School <info@example.org>\r\nDate: Friday\r\n\r\nPractice at the field.\n>Old time: 5 pm"
        visible = visible_text(text)
        offset = text.index("Practice")
        self.assertEqual(len(visible), len(text))
        self.assertEqual(visible[offset:offset+8], "Practice")
        self.assertNotIn("example.org", visible)
        self.assertNotIn("5 pm", visible)

    def test_copied_email_header_resolves_relative_dates_with_visible_provenance(self):
        text = ("From: School <info@example.org>\nDate: Mon, 23 Nov 2026 09:00:00 -0600\n"
                "Subject: Chess club\n\nWhen: tomorrow at 4 PM")
        values, evidence = interpret(text, (), model=self.model)
        self.assertEqual((values["date"], values["time"]), ("2026-11-24", "16:00"))
        self.assertEqual(evidence["date"]["anchorOrigin"], "email_header")
        values, _ = interpret(text, (), "2026-11-24", self.model)
        self.assertEqual(values["date"], "2026-11-25")
        self.assertEqual(sent_date("Latest details below\nFrom: Old <old@example.org>\nDate: Mon, 23 Nov 2026 09:00:00 -0600"), "")

    def test_tentative_schedules_withhold_dates_even_with_explicit_fields(self):
        text = "The class might happen if the coach confirms. No decision yet.\nDate: 27 November 2026\nTime: 5 PM"
        values, evidence = interpret(text, (), model=self.model)
        self.assertNotIn("date", values)
        self.assertNotIn("time", values)
        self.assertEqual(evidence["_model"]["reviewReason"], "tentative")

    def test_span_decoder_uses_context_and_cannot_cross_lines(self):
        text = "winter concert\nprogram"
        matches = tokens(text)
        scores = np.tile([.99, .005, .005], (len(matches), len(FIELDS), 1))
        scores[:, 0] = [[.53, .46, .01], [.1, .05, .85], [.22, .03, .75]]
        spans = decode_spans(text, matches, scores)
        self.assertEqual([(s.field, text[s.start:s.end]) for s in spans], [("title", "winter concert")])

    def test_disabled_and_oversized_inputs_preserve_rule_fallback(self):
        text = "When: December 4, 2026 at 5 pm"
        with patch.dict(os.environ, {"RELAY_NLU_ENABLED": "0"}):
            self.assertIsNone(active_notice_model())
            self.assertEqual(interpret_notice(text, ()), extract(text, ()))
        long_message = text + "\n" + ("background " * 220)
        self.assertEqual(interpret(long_message, (), model=self.model), extract(long_message, ()))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                NoticeModel(Path(directory) / "missing.npz")
