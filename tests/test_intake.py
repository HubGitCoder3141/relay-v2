"""Regression examples for pasted notices and unsafe interpretations."""
import unittest

from relay_intake import extract


class NoticeInterpretationTests(unittest.TestCase):
    def test_plain_text_school_sports_and_family_messages(self):
        cases = [
            ("Chess club is on Fri, Dec 4 at 3:30 pm at the library.\nBring a board.\nPlease RSVP by tomorrow.",
             "2026-11-29", {"title": "Chess club", "date": "2026-12-04", "time": "15:30",
                            "location": "the library", "preparation": "a board", "deadline": "2026-11-30"}),
            ("Sam has swimming on December 5, 2026 at noon. Pack a towel.\nPack a water bottle.",
             "", {"title": "swimming", "person": "Sam", "date": "2026-12-05", "time": "12:00",
                  "preparation": "a towel\na water bottle"}),
            ("Winter assembly starts at 9 am on December 4, 2026 in the gym.\nArrive ten minutes early.",
             "", {"title": "Winter assembly", "date": "2026-12-04", "time": "09:00", "location": "the gym",
                  "instructions": "Arrive ten minutes early."}),
            ("Subject: Practice update\n- When: Dec 5, 2026, 1 pm–2:30 pm at Field 4\n> Time: 12:30",
             "", {"title": "Practice update", "date": "2026-12-05", "time": "13:00", "location": "Field 4"}),
            ("Subject: Time change\nWhen: December 5, 2026 at 6 pm\nOn Friday, Alex wrote:\nDate: 2026-12-04\nTime: 16:00",
             "", {"title": "Time change", "date": "2026-12-05", "time": "18:00"}),
            ("From: Club <club@example.com>\nDate: Dec 1, 2026\nSubject: Chess practice\n\nChess practice is on Dec 4, 2026 at 3 pm.",
             "", {"title": "Chess practice", "date": "2026-12-04", "time": "15:00"}),
        ]
        for notice, anchor, expected in cases:
            with self.subTest(notice=notice):
                values, report = extract(notice, ["Sam", "Alex"], anchor)
                for field, value in expected.items():
                    self.assertEqual(values.get(field), value, report)
                    self.assertEqual(report[field]["status"], "suggested")

    def test_unclear_dates_and_schedule_options_are_not_guessed(self):
        for notice in [
            "When: December 5 at 6 pm",
            "When: December 5, 2026 or December 6, 2026",
            "When: 12/05/2026 at 6 pm",
            "When: Monday, December 5, 2026 at 6 pm",
            "When: December 5, 2026 at 6 pm or 7 pm",
            "Subject: Practice\nPractice is cancelled.\nDate: 2026-12-05\nTime: 17:00",
            "Soccer is on Dec 5, 2026 at 6 pm.\nSwimming is on Dec 5, 2026 at 6 pm.",
        ]:
            with self.subTest(notice=notice):
                values, report = extract(notice, ["Sam"])
                self.assertNotIn("date", values)
                self.assertNotIn("time", values)
                self.assertIn(report["date"]["status"], ("invalid", "conflicting"))

    def test_relative_evidence_records_the_user_supplied_message_date(self):
        values, report = extract("When: tomorrow at noon\nRSVP by: today", [], "2026-12-31")
        self.assertEqual((values["date"], values["time"], values["deadline"]),
                         ("2027-01-01", "12:00", "2026-12-31"))
        self.assertEqual(report["date"]["anchor"], "2026-12-31")
        self.assertEqual(report["deadline"]["evidence"], [{"line": 2, "value": "today"}])
