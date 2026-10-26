import unittest

from ai_engine.extractor import extract_facts


class ExtractorTests(unittest.TestCase):

    def test_sleep_hours_and_quality(self):
        facts = extract_facts(
            "I sleep about 5 hours on school nights and wake up tired. "
            "My sleep quality is poor and it is irregular."
        )
        self.assertEqual(facts["sleep"]["hours"], 5)
        self.assertEqual(facts["sleep"]["quality"], "Poor")
        self.assertEqual(facts["sleep"]["consistency"], "Irregular")

    def test_does_not_fabricate_attendance(self):
        facts = extract_facts("I sleep about 5 hours on school nights.")
        self.assertNotIn("academic_load", facts)

    def test_explicit_attendance_is_recorded(self):
        facts = extract_facts("My attendance is 72% this semester.")
        self.assertEqual(facts["academic_load"]["attendance"], 72)

    def test_latest_statement_wins(self):
        facts = extract_facts(
            "I sleep 5 hours. I study 4 hours a day. "
            "Actually, I sleep 8 hours now."
        )
        self.assertEqual(facts["sleep"]["hours"], 8)

    def test_academic_load(self):
        facts = extract_facts(
            "I study for 10 hours a day and have several assignments. "
            "Exams are next week and school is overwhelming."
        )
        self.assertEqual(facts["academic_load"]["study_hours"], 10)
        self.assertEqual(facts["academic_load"]["homework_load"], "Heavy")
        self.assertEqual(facts["academic_load"]["assignments"], "Several")

    def test_exhaustion(self):
        facts = extract_facts(
            "I feel drained and exhausted every day. "
            "I cannot recover even after rest."
        )
        self.assertEqual(
            facts["emotional_exhaustion"]["feeling_drained"],
            "Always",
        )
        self.assertEqual(
            facts["emotional_exhaustion"]["recovery_after_rest"],
            "Rarely",
        )

    def test_positive_support_and_exercise(self):
        facts = extract_facts(
            "I have good friends and I go to the gym daily. "
            "My routine is regular."
        )
        self.assertEqual(
            facts["social_support"]["support_availability"],
            "Available",
        )
        self.assertEqual(
            facts["exercise"]["physical_activity"],
            "Regular",
        )

    def test_empty_text(self):
        self.assertEqual(extract_facts(""), {})

    def test_all_emitted_labels_are_valid_schema_values(self):
        from engine.validators import validate_payload

        facts = extract_facts(
            "I sleep 5 hours, quality is poor. I am stressed and anxious. "
            "I cannot focus. I have no motivation. I feel sad and lonely. "
            "My routine is irregular, my screen time is too much, "
            "and I have too many assignments."
        )
        # Should not raise
        validate_payload(facts)


if __name__ == "__main__":
    unittest.main()
