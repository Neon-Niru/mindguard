"""Convert raw interview facts into uniform health values.

Every value produced here is on a 0-100 scale where:

    0   = worst possible health signal for that field
    100 = best possible health signal for that field

Orientation is applied here so scoring never has to care whether a field
is protective ("sleep hours") or a risk factor ("study hours").
"""

from .schema import ENGINE_SCHEMA


# Raw ordinal value before orientation is applied.
ORDINAL_MAP = {
    # None / absence
    "Never": 0,
    "None": 0,
    "No": 0,
    "Not at all": 0,
    "Nothing": 0,

    # Low
    "Rarely": 25,
    "Seldom": 25,
    "Minor": 25,
    "Low": 25,
    "Poor": 25,
    "Mild": 25,
    "Light": 25,
    "A few": 25,
    "One": 25,
    "Irregular": 25,

    # Moderate
    "Sometimes": 50,
    "Moderate": 50,
    "Fair": 50,
    "Okay": 50,
    "Average": 50,
    "Occasionally": 50,

    # High
    "Often": 75,
    "Frequently": 75,
    "High": 75,
    "Heavy": 75,
    "Several": 75,
    "Good": 75,
    "Regular": 75,
    "Available": 75,
    "Major": 75,
    "Many": 75,
    "Mostly": 75,

    # Maximum
    "Always": 100,
    "Yes": 100,
    "Excellent": 100,
    "Constant": 100,
    "Constantly": 100,
    "Severe": 100,
    "Extreme": 100,
    "Every day": 100,
}


ORDINAL_LOOKUP = {
    label.lower(): score for label, score in ORDINAL_MAP.items()
}


def _coerce_number(value):
    if isinstance(value, bool):
        return 100.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except (TypeError, ValueError):
            return None
    return None


def _scale_continuous(value, rules):
    minimum = float(rules.get("min", 0))
    maximum = float(rules.get("max", 100))

    if maximum <= minimum:
        return 50.0

    clamped = max(minimum, min(maximum, value))
    return (clamped - minimum) / (maximum - minimum) * 100.0


def _normalize_value(value, rules):
    """Return a 0-100 health value, or None when it cannot be interpreted."""
    ftype = rules.get("type", "")
    orientation = rules.get("orientation", "positive")

    if ftype == "ordinal":
        if isinstance(value, str):
            raw = ORDINAL_LOOKUP.get(value.strip().lower())
            if raw is None:
                return None
        else:
            # Some callers may already supply a 0-100 ordinal score.
            raw = _coerce_number(value)
            if raw is None:
                return None
            raw = max(0.0, min(100.0, raw))
        score = float(raw)

    elif ftype == "percentage":
        numeric = _coerce_number(value)
        if numeric is None:
            return None
        score = max(0.0, min(100.0, numeric))

    elif ftype == "continuous":
        numeric = _coerce_number(value)
        if numeric is None:
            return None
        score = _scale_continuous(numeric, rules)

    else:
        numeric = _coerce_number(value)
        if numeric is None:
            return None
        score = max(0.0, min(100.0, numeric))

    if orientation == "negative":
        score = 100.0 - score

    return round(score, 2)


def normalize_payload(payload: dict):
    normalized = {}

    for category, fields in payload.items():
        schema_fields = ENGINE_SCHEMA.get(category)
        if not schema_fields or not isinstance(fields, dict):
            continue

        normalized_fields = {}

        for field, value in fields.items():
            field_rules = schema_fields.get(field)
            if not field_rules or value is None:
                continue

            score = _normalize_value(value, field_rules)
            if score is not None:
                normalized_fields[field] = score

        if normalized_fields:
            normalized[category] = normalized_fields

    return normalized
