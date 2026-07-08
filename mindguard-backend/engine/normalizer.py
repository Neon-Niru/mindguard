from .schema import ENGINE_SCHEMA

ORDINAL_MAP = {
    "Never": 0,
    "Rarely": 25,
    "Sometimes": 50,
    "Often": 75,
    "Always": 100,
    "Low": 25,
    "Moderate": 50,
    "High": 75,
    "Poor": 25,
    "Fair": 50,
    "Good": 75,
    "Excellent": 100,
    "No": 0,
    "Yes": 100,
    "Available": 75,
    "Regular": 75,
    "Irregular": 25,
    "Heavy": 75,
    "Several": 75,
    "Minor": 25,
    "Minor": 25,
}


def normalize_payload(payload: dict):
    normalized = {}

    for category, fields in payload.items():
        normalized[category] = {}
        schema_fields = ENGINE_SCHEMA.get(category, {})

        for field, value in fields.items():
            field_rules = schema_fields.get(field, {})
            orientation = field_rules.get("orientation", "positive")
            ftype = field_rules.get("type", "")

            if isinstance(value, (int, float)):
                normalized[category][field] = float(value)
            elif isinstance(value, str) and value in ORDINAL_MAP:
                mapped = ORDINAL_MAP[value]
                if orientation == "negative":
                    mapped = 100 - mapped
                normalized[category][field] = float(mapped)
            elif isinstance(value, str):
                normalized[category][field] = 50.0
            else:
                normalized[category][field] = 50.0

    return normalized
