"""
MindGuard AI interview state manager.

Tracks collected information and required fields; does not score responses.
"""

from engine.schema import ENGINE_SCHEMA


REQUIRED_INTERVIEW_CATEGORIES = list(ENGINE_SCHEMA)


def _field_is_collected(state, category, field):
    values = state.get("data", {}).get(category, {})
    return isinstance(values, dict) and field in values and values[field] is not None


def get_missing_fields(state):
    return [
        {"category": category, "field": field}
        for category, fields in ENGINE_SCHEMA.items()
        for field, rules in fields.items()
        if rules.get("required", False) and not _field_is_collected(state, category, field)
    ]


def get_missing_categories(state):
    return list(dict.fromkeys(item["category"] for item in get_missing_fields(state)))


def refresh_state(state):
    state["missing_fields"] = get_missing_fields(state)
    state["missing"] = get_missing_categories(state)
    state["completed"] = [
        category
        for category in REQUIRED_INTERVIEW_CATEGORIES
        if category not in state["missing"]
    ]
    return state


def create_state():
    return refresh_state({"data": {}, "history": []})


def update_state(state, extracted):
    if not isinstance(extracted, dict):
        return refresh_state(state)

    for category, values in extracted.items():
        if category not in ENGINE_SCHEMA or not isinstance(values, dict):
            continue

        category_data = state.setdefault("data", {}).setdefault(category, {})
        for field, value in values.items():
            if field in ENGINE_SCHEMA[category] and value is not None:
                category_data[field] = value

    return refresh_state(state)


def is_complete(state):
    # Complete if we have collected at least 4 key categories or if forced
    data = state.get("data", {})
    core_categories = {"sleep", "academic_load", "emotional_exhaustion", "stress", "burnout_symptoms"}
    collected_core = [cat for cat in core_categories if cat in data and len(data[cat]) > 0]
    
    # Also check if user history contains a skip/finish intent or if we have enough data
    history = state.get("history", [])
    if len(history) >= 10:  # Hard limit to prevent endless chat loops!
        return True
        
    return len(collected_core) >= 3 and len(get_missing_fields(state)) < 15