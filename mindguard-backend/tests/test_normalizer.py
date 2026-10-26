import unittest

from engine.normalizer import normalize_payload


class NormalizerTests(unittest.TestCase):

    def test_positive_continuous_scales_to_health(self):
        result = normalize_payload({"sleep": {"hours": 8}})
        self.assertGreater(result["sleep"]["hours"], 70)
        self.assertLessEqual(result["sleep"]["hours"], 100)

    def test_negative_continuous_is_inverted(self):
        low = normalize_payload({"academic_load": {"study_hours": 0}})
        high = normalize_payload({"academic_load": {"study_hours": 16}})

        self.assertEqual(low["academic_load"]["study_hours"], 100)
        self.assertEqual(high["academic_load"]["study_hours"], 0)

    def test_ordinal_labels_are_case_insensitive(self):
        result = normalize_payload({"stress": {"stress_frequency": "high"}})
        # Negative orientation: "High" risk becomes low health.
        self.assertEqual(result["stress"]["stress_frequency"], 25)

    def test_unknown_labels_are_dropped(self):
        result = normalize_payload({"stress": {"stress_frequency": "bananas"}})
        self.assertNotIn("stress", result)

    def test_unknown_categories_are_ignored(self):
        result = normalize_payload({"not_a_category": {"x": 1}})
        self.assertEqual(result, {})

    def test_invalid_type_is_dropped(self):
        result = normalize_payload({"sleep": {"hours": "not a number"}})
        self.assertEqual(result, {})

    def test_more_sleep_is_healthier(self):
        three = normalize_payload({"sleep": {"hours": 3}})
        nine = normalize_payload({"sleep": {"hours": 9}})
        self.assertGreater(
            nine["sleep"]["hours"],
            three["sleep"]["hours"],
        )


if __name__ == "__main__":
    unittest.main()
