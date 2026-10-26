import unittest
from unittest.mock import patch

from ai_engine.conversation_manager import process_message
from ai_engine.extractor import CONTEXT_TARGETS
from ai_engine.fallback import (
    QUESTION_VARIANTS,
    derive_progress,
    looks_confused,
    next_question,
)
from ai_engine.state_manager import (
    REQUIRED_INTERVIEW_CATEGORIES,
    create_state,
)
from engine.normalizer import ORDINAL_LOOKUP
from engine.schema import ENGINE_SCHEMA


class FallbackQuestionTests(unittest.TestCase):
    """The deterministic interviewer that runs without an LLM key."""

    def test_every_category_has_a_question(self):
        for category in REQUIRED_INTERVIEW_CATEGORIES:
            self.assertIn(category, QUESTION_VARIANTS)
            self.assertTrue(QUESTION_VARIANTS[category])

    def test_questions_are_unique(self):
        questions = [
            question
            for variants in QUESTION_VARIANTS.values()
            for question in variants
        ]
        self.assertEqual(len(questions), len(set(questions)))

    def test_never_repeats_the_same_question_twice_in_a_row(self):
        state = create_state()
        previous = None

        # "mm" is a vague answer: nothing is extractable, so this exercises
        # exactly the bug where the same question was asked forever.
        for _ in range(12):
            current = next_question(state)
            self.assertIsNotNone(current)
            self.assertNotEqual(current, previous)
            previous = current

    def test_prefers_the_topic_that_was_questioned(self):
        state = create_state()
        state["last_topic"] = "sleep"
        state["asked"] = {"sleep": 1}

        question = next_question(state, prefer="sleep")

        self.assertIn(question, QUESTION_VARIANTS["sleep"])
        self.assertEqual(state["last_topic"], "sleep")

    def test_moves_on_after_too_many_probes(self):
        state = create_state()
        state["last_topic"] = "sleep"
        state["asked"] = {"sleep": 5}

        question = next_question(state, prefer="sleep")

        self.assertNotIn(question, QUESTION_VARIANTS["sleep"])

    def test_derive_progress_reads_the_transcript(self):
        history = [
            {"role": "student", "content": "hey"},
            {"role": "assistant", "content": QUESTION_VARIANTS["sleep"][0]},
            {"role": "student", "content": "5 hours"},
            {"role": "assistant", "content": QUESTION_VARIANTS["sleep"][1]},
            {"role": "assistant", "content": "Some free-form LLM reply"},
        ]

        asked, last_question, last_topic = derive_progress(history)

        self.assertEqual(asked, {"sleep": 2})
        self.assertEqual(last_topic, "sleep")
        self.assertEqual(last_question, QUESTION_VARIANTS["sleep"][1])

    def test_confusion_detection_uses_whole_words(self):
        self.assertTrue(looks_confused("huh"))
        self.assertTrue(looks_confused("why are you asking that again"))
        self.assertTrue(looks_confused("I don't know"))
        self.assertTrue(looks_confused("what do you mean?"))
        # "again" must not match inside "against".
        self.assertFalse(looks_confused("against all odds I study 6 hours"))
        self.assertFalse(looks_confused("its ok"))

    def test_contextual_labels_are_valid_for_the_engine(self):
        for category, targets in CONTEXT_TARGETS.items():
            self.assertIn(category, ENGINE_SCHEMA)

            for bucket, (field, label) in targets.items():
                self.assertIn(
                    field,
                    ENGINE_SCHEMA[category],
                    f"{category}/{bucket} uses unknown field {field}",
                )
                self.assertIn(
                    label.strip().lower(),
                    ORDINAL_LOOKUP,
                    f"{category}/{bucket} uses invalid label {label}",
                )


class FallbackConversationTests(unittest.TestCase):
    """End-to-end conversation behaviour with no LLM available."""

    def setUp(self):
        patcher = patch(
            "ai_engine.conversation_manager.ask_llm",
            return_value=None,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _say(self, message, state):
        result = process_message(message, state)
        return result["reply"], result["state"]

    def test_first_question_is_about_academic_load(self):
        reply, state = self._say("hey", create_state())

        self.assertIn(reply, QUESTION_VARIANTS["academic_load"])
        self.assertEqual(state["last_topic"], "academic_load")

    def test_vague_answers_do_not_repeat_the_question(self):
        state = create_state()
        replies = []

        for message in ["hey"] + ["mm"] * 8:
            reply, state = self._say(message, state)
            replies.append(reply)

        for previous, current in zip(replies, replies[1:]):
            self.assertNotEqual(previous, current)

    def test_terse_answer_is_bound_to_the_asked_topic(self):
        reply, state = self._say("hey", create_state())
        self.assertEqual(state["last_topic"], "academic_load")

        next_reply, state = self._say("its ok", state)

        self.assertEqual(
            state["data"]["academic_load"]["homework_load"],
            "Moderate",
        )
        self.assertNotEqual(reply, next_reply)

    def test_numeric_answer_is_bound_to_the_asked_topic(self):
        state = create_state()
        state["last_topic"] = "sleep"

        _, state = self._say("5 hours", state)

        self.assertEqual(state["data"]["sleep"]["hours"], 5)

    def test_negative_answer_is_interpreted_by_topic(self):
        state = create_state()
        state["last_topic"] = "stress"

        _, state = self._say("not good", state)

        self.assertEqual(
            state["data"]["stress"]["stress_frequency"],
            "High",
        )

    def test_long_answer_is_not_misattributed(self):
        state = create_state()
        state["last_topic"] = "academic_load"

        _, state = self._say(
            "I have been feeling really stressed and I cannot sleep well at night",
            state,
        )

        self.assertNotIn("academic_load", state["data"])
        self.assertIn("stress", state["data"])

    def test_confused_student_gets_an_explanation(self):
        reply, state = self._say("hey", create_state())

        confused_reply, state = self._say("why are you asking that again", state)

        self.assertTrue(
            confused_reply.startswith("That one helps me understand"),
            confused_reply,
        )
        self.assertNotEqual(reply, confused_reply)
        self.assertEqual(state["last_topic"], "academic_load")
        self.assertEqual(state["data"], {})

    def test_confused_student_with_an_answer_is_still_recorded(self):
        state = create_state()
        state["last_topic"] = "academic_load"

        _, state = self._say("what? it's heavy", state)

        self.assertEqual(
            state["data"]["academic_load"]["homework_load"],
            "Heavy",
        )


if __name__ == "__main__":
    unittest.main()
