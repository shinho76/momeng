import unittest
from datetime import datetime, timedelta

from flashcard import INTERVALS, apply_answer, pick_next

NOW = datetime(2026, 1, 1, 12, 0)


def fresh_progress():
    return {"cards": {}, "daily": {"date": "", "new": 0}}


class TestApplyAnswer(unittest.TestCase):
    def test_new_card_known_goes_to_box2(self):
        s = apply_answer(None, True, NOW)
        self.assertEqual(s["box"], 2)
        self.assertEqual(s["due"], (NOW + INTERVALS[2]).isoformat())

    def test_wrong_resets_to_box1_in_10_minutes(self):
        s = apply_answer({"box": 4, "streak": 0, "tries": 3, "wrong": 0, "mastered": False}, False, NOW)
        self.assertEqual((s["box"], s["wrong"], s["streak"]), (1, 1, 0))
        self.assertEqual(s["due"], (NOW + timedelta(minutes=10)).isoformat())

    def test_box_climbs_with_intervals(self):
        s = None
        for expected in (2, 3, 4, 5):
            s = apply_answer(s, True, NOW)
            self.assertEqual(s["box"], expected)
            self.assertEqual(s["due"], (NOW + INTERVALS[expected]).isoformat())

    def test_mastered_after_three_in_box5(self):
        s = {"box": 5, "streak": 0, "tries": 5, "wrong": 0, "mastered": False}
        for _ in range(3):
            self.assertFalse(s["mastered"])
            s = apply_answer(s, True, NOW)
        self.assertTrue(s["mastered"])

    def test_wrong_breaks_streak(self):
        s = {"box": 5, "streak": 2, "tries": 5, "wrong": 0, "mastered": False}
        s = apply_answer(s, False, NOW)
        self.assertEqual((s["box"], s["streak"]), (1, 0))


class TestPickNext(unittest.TestCase):
    cards = {"a": {}, "b": {}, "c": {}}

    def test_due_before_new(self):
        p = fresh_progress()
        p["cards"]["a"] = apply_answer(None, False, NOW - timedelta(hours=1))
        self.assertEqual(pick_next(self.cards, p, NOW, 20), "a")

    def test_not_yet_due_falls_back_to_new(self):
        p = fresh_progress()
        p["cards"]["a"] = apply_answer(None, True, NOW)
        self.assertIn(pick_next(self.cards, p, NOW, 20), ("b", "c"))

    def test_daily_new_limit(self):
        p = fresh_progress()
        p["daily"] = {"date": NOW.date().isoformat(), "new": 20}
        self.assertIsNone(pick_next(self.cards, p, NOW, 20))

    def test_mastered_excluded(self):
        p = fresh_progress()
        s = apply_answer(None, False, NOW - timedelta(days=1))
        s["mastered"] = True
        p["cards"]["a"] = s
        self.assertNotEqual(pick_next(self.cards, p, NOW, 20), "a")

    def test_notebook_only_wrong_cards(self):
        p = fresh_progress()
        p["cards"]["a"] = apply_answer(None, False, NOW)
        p["cards"]["b"] = apply_answer(None, True, NOW)
        self.assertEqual(pick_next(self.cards, p, NOW, 20, notebook=True), "a")


if __name__ == "__main__":
    unittest.main()
