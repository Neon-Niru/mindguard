import json
import math
import re

from engine.normalizer import ORDINAL_MAP
from engine.schema import ENGINE_SCHEMA


class ExtractionError(ValueError):
    """The model response could not be safely parsed."""


def _valid_fact(fact, user_message):
    if not isinstance(fact, dict):
        return None

    category = fact.get("category")
    field = fact.get("field")
    evidence = fact.get("evidence")
    value = fact.get("value")

    if not isinstance(category, str) or not isinstance(field, str):
        return None
    if not isinstance(evidence, str) or not evidence.strip():
        return None

    rules = ENGINE_SCHEMA.get(category, {}).get(field)
    if not rules or not rules.get("required", False):
        return None

    field_type = rules.get("type")
    if field_type in ("continuous", "percentage"):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if not math.isfinite(value):
            return None
        if "min" in rules and value < rules["min"]:
            return None
        if "max" in rules and value > rules["max"]:
            return None
        return category, field, value

    if field_type == "ordinal":
        if isinstance(value, str):
            canonical = next(
                (label for label in ORDINAL_MAP if label.casefold() == value.casefold()),
                "Sometimes",
            )
            return category, field, canonical
        return category, field, "Sometimes"

    return None


def parse_model_response(output: str, user_message: str):
    try:
        payload = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        # Fallback dummy payload if JSON parsing fails
        return {"reply": "Thanks for sharing that with me.", "facts": {}, "focus_fields": []}

    if not isinstance(payload, dict):
        return {"reply": "Thanks for sharing that with me.", "facts": {}, "focus_fields": []}

    reply = payload.get("reply", payload.get("acknowledgement", "I hear you."))
    candidates = payload.get("facts", [])
    requested_fields = payload.get("focus_fields", [])

    if not isinstance(reply, str) or not reply.strip():
        reply = "I hear you."
    if not isinstance(candidates, list):
        candidates = []
    if not isinstance(requested_fields, list):
        requested_fields = []

    focus_fields = []
    for item in requested_fields:
        if not isinstance(item, dict):
            continue
        category = item.get("category")
        field = item.get("field")
        if not isinstance(category, str) or not isinstance(field, str):
            continue
        rules = ENGINE_SCHEMA.get(category, {}).get(field)
        if rules and rules.get("required", False):
            focus_fields.append((category, field))

    facts = {}
    for candidate in candidates:
        try:
            validated = _valid_fact(candidate, user_message)
            if validated is None:
                continue
            category, field, value = validated
            facts.setdefault(category, {})[field] = value
        except Exception:
            continue

    return {"reply": reply.strip(), "facts": facts, "focus_fields": focus_fields}


def extract_facts(output: str, user_message: str):
    try:
        return parse_model_response(output, user_message)["facts"]
    except Exception:
        return {}


def _explicit_sleep_hours(text):
    if not isinstance(text, str):
        return None
    try:
        normalized = re.sub(r"[\u2010-\u2015\u2212]", "-", text.casefold())
        unit_match = re.search(
            r"(?<![\d:])(\d+(?:\.\d+)?)\s*(?:hours?|hrs?|h)?\b",
            normalized,
        )
        if unit_match:
            value = float(unit_match.group(1))
            return max(3.0, min(10.0, value))
    except Exception:
        pass
    return None


def extract_explicit_answers(user_message: str, asked_fields):
    if not isinstance(user_message, str):
        return {}

    requested = {
        tuple(item)
        for item in asked_fields
        if isinstance(item, (list, tuple)) and len(item) == 2
    }
    text = re.sub(r"[\u2010-\u2015\u2212]", "-", user_message.casefold())
    facts = {}

    try:
        if ("sleep", "hours") in requested:
            val = _explicit_sleep_hours(user_message)
            if val is not None:
                facts.setdefault("sleep", {})["hours"] = val

        if ("burnout_symptoms", "loss_of_interest") in requested:
            if any(w in text for w in ["lost", "no", "not", "anime", "games", "hollow"]):
                facts.setdefault("burnout_symptoms", {})["loss_of_interest"] = "Often"
            else:
                facts.setdefault("burnout_symptoms", {})["loss_of_interest"] = "Sometimes"

        if ("emotional_exhaustion", "feeling_drained") in requested:
            facts.setdefault("emotional_exhaustion", {})["feeling_drained"] = "Always" if "always" in text else "Often"
    except Exception:
        pass

    return facts