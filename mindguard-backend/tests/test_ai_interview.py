import json
import os
import unittest
from unittest.mock import patch, Mock

from ai_engine.conversation_manager import process_message
from ai_engine.llm_connector import ask_llm, LLMServiceError
from ai_engine.state_manager import (
    create_state,
    get_missing_fields,
    is_complete,
    update_state,
)
from ai_engine.question_builder import build_followup_question
from ai_engine.structured_extractor import parse_model_response
from engine.burnout_engine import BurnoutEngine
from engine.schema import ENGINE_SCHEMA


class StructuredExtractionTests(unittest.TestCase):
    def test_extracts_only_schema_values_with_evidence_from_latest_message(self):
        user_message = "I usually sleep 6 hours and my workload feels heavy."
        response = {
            "reply": "That sounds like a full week. How has your mood been?",
            "facts": [
                {
                    "category": "sleep",
                    "field": "hours",
                    "value": 6,
                    "evidence": "6 hours",
                },
                {
                    "category": "academic_load",
                    "field": "homework_load",
                    "value": "Heavy",
                    "evidence": "workload feels heavy",
                },
                {
                    "category": "mood",
                    "field": "positive_mood",
                    "value": "Low",
                    "evidence": "you seem sad",
                },
                {
                    "category": "sleep",
                    "field": "not_a_field",
                    "value": "Poor",
                    "evidence": "sleep",
                },
                {
                    "category": "sleep",
                    "field": "hours",
                    "value": 99,
                    "evidence": "6 hours",
                },
            ],
        }

        parsed = parse_model_response(json.dumps(response), user_message)

        self.assertEqual(parsed["facts"], {
            "sleep": {"hours": 6},
            "academic_load": {"homework_load": "Heavy"},
        })
        self.assertEqual(parsed["reply"], response["reply"])

    @patch("ai_engine.conversation_manager.ask_llm")
    def test_keeps_personalized_reply_instead_of_appending_a_scripted_question(self, mock_ask):
        natural_reply = "I'm sorry things feel heavy. How are you doing right now?"
        mock_ask.return_value = json.dumps({
            "reply": natural_reply,
            "facts": [],
        })

        result = process_message("Everything feels bad and I need a minute.", create_state())

        self.assertEqual(result["reply"], natural_reply)
        self.assertNotIn("asked_fields", result["state"]["history"][-1])

    def test_followup_rotates_to_next_category_after_progress(self):
        state = create_state()
        _, asked_sleep = build_followup_question(state)
        update_state(state, {"sleep": {"hours": 6.5}})

        _, asked_next = build_followup_question(
            state,
            previous_asked=set(asked_sleep),
            made_progress=True,
        )

        self.assertTrue(asked_next)
        self.assertTrue(all(category == "academic_load" for category, _ in asked_next))

    def test_unanswered_fields_stay_missing_until_all_required_engine_fields_arrive(self):
        state = create_state()
        self.assertFalse(is_complete(state))
        self.assertGreater(len(get_missing_fields(state)), 6)

        complete = {}
        for category, fields in ENGINE_SCHEMA.items():
            complete[category] = {}
            for field, rules in fields.items():
                if rules.get("type") in {"continuous", "percentage"}:
                    complete[category][field] = rules.get("min", 0)
                else:
                    complete[category][field] = "Sometimes"

        update_state(state, complete)

        self.assertTrue(is_complete(state))
        self.assertEqual(get_missing_fields(state), [])

        report = BurnoutEngine.generate_report(state["data"])
        self.assertIn("burnout_score", report)
        self.assertIn("wellness_score", report)

    @patch("ai_engine.conversation_manager.ask_llm")
    def test_conversation_uses_user_role_and_extracts_from_current_turn_only(self, mock_ask):
        mock_ask.return_value = json.dumps({
            "reply": "Thanks for sharing. How would you describe your sleep quality?",
            "facts": [
                {
                    "category": "stress",
                    "field": "stress_frequency",
                    "value": "High",
                    "evidence": "very stressed",
                },
                {
                    "category": "sleep",
                    "field": "hours",
                    "value": 7,
                    "evidence": "7 hours",
                },
            ],
        })

        state = create_state()
        state["history"].append({
            "role": "assistant",
            "content": "Earlier I asked about stress.",
        })

        result = process_message("I get 7 hours of sleep.", state)

        self.assertEqual(result["state"]["data"], {"sleep": {"hours": 7}})
        self.assertEqual(result["state"]["history"][-2]["role"], "user")
        self.assertFalse(result["complete"])

        sent = mock_ask.call_args.args[0]
        self.assertEqual(sent[0]["role"], "system")
        self.assertEqual(sent[1]["role"], "user")

    @patch("ai_engine.conversation_manager.ask_llm")
    def test_followups_are_chosen_after_each_turn_updates_the_state(self, mock_ask):
        mock_ask.side_effect = [
            json.dumps({
                "acknowledgement": "Got it, about five to six hours.",
                "facts": [
                    {
                        "category": "sleep",
                        "field": "hours",
                        "value": 5.5,
                        "evidence": "5-6",
                    }
                ],
            }),
            json.dumps({
                "acknowledgement": "I hear you describing the quality as mediocre.",
                "facts": [
                    {
                        "category": "sleep",
                        "field": "quality",
                        "value": "Fair",
                        "evidence": "mediocre",
                    }
                ],
            }),
            json.dumps({
                "acknowledgement": "Thanks for clarifying.",
                "facts": [],
            }),
        ]

        state = create_state()

        first = process_message("uh 5-6?", state)
        self.assertEqual(first["state"]["data"]["sleep"]["hours"], 5.5)
        self.assertNotIn(
            ["sleep", "hours"],
            first["state"]["history"][-1]["asked_fields"],
        )

        second = process_message("it was mediocre", first["state"])
        self.assertEqual(second["state"]["data"]["sleep"]["quality"], "Fair")

        asked_after_second = second["state"]["history"][-1]["asked_fields"]
        self.assertNotIn(["sleep", "hours"], asked_after_second)
        self.assertNotIn(["sleep", "quality"], asked_after_second)

        third = process_message("what?", second["state"])
        asked_after_third = third["state"]["history"][-1]["asked_fields"]
        self.assertNotIn(["sleep", "hours"], asked_after_third)
        self.assertNotIn(["sleep", "quality"], asked_after_third)
        self.assertIn("asked that unclearly", third["reply"])

    @patch("ai_engine.llm_connector.requests.post")
    def test_groq_uses_supported_default_model_and_json_mode(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "choices": [{"message": {"content": '{"reply":"ok","facts":[]}'}}]
        }
        response.raise_for_status.return_value = None
        mock_post.return_value = response

        with patch.dict(
            os.environ,
            {"LLM_PROVIDER": "groq", "GROQ_API_KEY": "test-key"},
            clear=True,
        ):
            result = ask_llm([{"role": "system", "content": "return JSON"}])

        self.assertEqual(result, '{"reply":"ok","facts":[]}')
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], "openai/gpt-oss-120b")
        self.assertEqual(payload["response_format"], {"type": "json_object"})

    def test_missing_provider_key_is_not_silently_treated_as_success(self):
        with patch.dict(os.environ, {"LLM_PROVIDER": "groq"}, clear=True):
            with self.assertRaises(LLMServiceError):
                ask_llm([])


if __name__ == "__main__":
    unittest.main()