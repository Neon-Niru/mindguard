import unittest

from engine.burnout_engine import BurnoutEngine
from tests.fixtures import BAD_PAYLOAD, GOOD_PAYLOAD


class EngineTests(unittest.TestCase):

    def test_good_payload_is_low_risk(self):
        report = BurnoutEngine.generate_report(GOOD_PAYLOAD)
        self.assertLess(report["burnout_score"], 35)
        self.assertEqual(report["risk_level"], "Low")
        self.assertGreater(report["wellness_score"], 65)

    def test_bad_payload_is_high_risk(self):
        report = BurnoutEngine.generate_report(BAD_PAYLOAD)
        self.assertGreaterEqual(report["burnout_score"], 65)
        self.assertEqual(report["risk_level"], "High")

    def test_bad_payload_scores_worse_than_good(self):
        good = BurnoutEngine.generate_report(GOOD_PAYLOAD)
        bad = BurnoutEngine.generate_report(BAD_PAYLOAD)
        self.assertGreater(bad["burnout_score"], good["burnout_score"])

    def test_empty_payload_does_not_invent_burnout(self):
        report = BurnoutEngine.generate_report({})
        self.assertEqual(report["burnout_score"], 0)
        self.assertEqual(report["risk_level"], "Low")
        self.assertEqual(report["categories_assessed"], 0)

    def test_partial_payload_is_scored(self):
        report = BurnoutEngine.generate_report({"sleep": {"hours": 5}})
        self.assertEqual(report["categories_assessed"], 1)
        self.assertEqual(report["category_scores"]["sleep"] > 0, True)

    def test_sleep_hours_are_monotonic(self):
        three = BurnoutEngine.generate_report({"sleep": {"hours": 3}})
        nine = BurnoutEngine.generate_report({"sleep": {"hours": 9}})
        self.assertGreater(
            three["burnout_score"],
            nine["burnout_score"],
        )

    def test_report_contains_engine_metadata(self):
        report = BurnoutEngine.generate_report(GOOD_PAYLOAD)
        self.assertTrue(report["engine_version"])
        self.assertEqual(report["data_completeness"], 1.0)
        self.assertIn("category_summaries", report)
        self.assertLessEqual(len(report["recovery_focus_areas"]), 3)

    def test_category_scores_are_health_values(self):
        report = BurnoutEngine.generate_report(BAD_PAYLOAD)
        for score in report["category_scores"].values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)

    def test_recovery_suggestions_are_not_empty(self):
        report = BurnoutEngine.generate_report(BAD_PAYLOAD)
        self.assertTrue(report["primary_contributors"])
        self.assertTrue(report["recovery_focus_areas"])


if __name__ == "__main__":
    unittest.main()
