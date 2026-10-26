import unittest

from engine.config import CATEGORY_WEIGHTS
from engine.scoring import (
    calculate_burnout,
    category_score,
    classify_risk,
    rank_contributors,
)


class ScoringTests(unittest.TestCase):

    def test_empty_category_score_is_none(self):
        self.assertIsNone(category_score([]))

    def test_category_score_averages_values(self):
        self.assertEqual(category_score([0, 50, 100]), 50)

    def test_no_data_scores_zero_burnout(self):
        result = calculate_burnout({})
        self.assertEqual(result["burnout_score"], 0)
        self.assertEqual(result["wellness_score"], 100)
        self.assertEqual(result["data_completeness"], 0.0)

    def test_weights_renormalise_for_partial_data(self):
        # A single available category should be scored on its own, not
        # diluted by categories that were never collected.
        result = calculate_burnout({"sleep": 0})
        self.assertEqual(result["burnout_score"], 100)

    def test_protective_categories_reduce_burnout(self):
        without_support = calculate_burnout({"stress": 0})
        with_support = calculate_burnout({"stress": 0, "social_support": 100})
        self.assertLess(
            with_support["burnout_score"],
            without_support["burnout_score"],
        )

    def test_burnout_is_clamped(self):
        worst = {category: 0 for category in CATEGORY_WEIGHTS}
        result = calculate_burnout(worst)
        self.assertGreaterEqual(result["burnout_score"], 0)
        self.assertLessEqual(result["burnout_score"], 100)

    def test_risk_thresholds(self):
        self.assertEqual(classify_risk(0), "Low")
        self.assertEqual(classify_risk(34), "Low")
        self.assertEqual(classify_risk(35), "Moderate")
        self.assertEqual(classify_risk(64), "Moderate")
        self.assertEqual(classify_risk(65), "High")
        self.assertEqual(classify_risk(100), "High")

    def test_rank_contributors_orders_worst_first(self):
        ranked = rank_contributors({"sleep": 80, "stress": 10})
        self.assertEqual(next(iter(ranked)), "stress")


if __name__ == "__main__":
    unittest.main()
