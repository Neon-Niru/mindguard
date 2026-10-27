import re
from .schema import ENGINE_SCHEMA

ORDINAL_MAP = {
    "never": 0,
    "rarely": 25,
    "sometimes": 50,
    "often": 75,
    "always": 100,
    "low": 25,
    "moderate": 50,
    "high": 75,
    "poor": 25,
    "fair": 50,
    "good": 75,
    "excellent": 100,
    "no": 0,
    "yes": 100,
    "available": 75,
    "regular": 75,
    "irregular": 25,
    "heavy": 75,
    "several": 75,
    "minor": 25,
}

DISTRESS_KEYWORDS = [
    "crap", "awful", "terrible", "worst", "wrost", "cant handle", 
    "can't handle", "overwhelming", "exhausted", "too much", "horrible",
    "bad", "not good", "struggling", "pain"
]


def normalize_payload(payload: dict):
    normalized = {}

    for category, fields in payload.items():
        normalized[category] = {}
        schema_fields = ENGINE_SCHEMA.get(category, {})

        for field, value in fields.items():
            field_rules = schema_fields.get(field, {})
            orientation = field_rules.get("orientation", "positive")
            ftype = field_rules.get("type", "")

            # 1. If already int or float
            if isinstance(value, (int, float)):
                mapped = float(value)
            
            elif isinstance(value, str):
                val_lower = value.strip().lower()

                # Check for severe distress keywords in free text
                has_distress = any(kw in val_lower for kw in DISTRESS_KEYWORDS)

                if has_distress:
                    # Force low score (high burnout) for distress
                    mapped = 10.0
                elif val_lower in ORDINAL_MAP:
                    mapped = float(ORDINAL_MAP[val_lower])
                else:
                    # Try to extract numbers (e.g. "1-2 hours", "10 hours", "5")
                    numbers = re.findall(r"(\d+(?:\.\d+)?)", val_lower)
                    if numbers:
                        num_val = float(numbers[0])
                        # Special handling if this is a sleep field
                        if "sleep" in field.lower() or category == "sleep":
                            # 7-9 hours is ideal (100), < 4 hours is terrible (15)
                            if num_val >= 7:
                                mapped = 85.0
                            elif num_val >= 5:
                                mapped = 50.0
                            else:
                                mapped = 15.0
                        else:
                            # Generic numeric normalization (0 to 10 scale vs 0 to 100 scale)
                            mapped = min(100.0, num_val * 10 if num_val <= 10 else num_val)
                    else:
                        # Fallback default if no match or numbers found
                        mapped = 50.0
            else:
                mapped = 50.0

            # Adjust for negative orientation fields if necessary
            if orientation == "negative" and not isinstance(value, (int, float)):
                # If negative orientation, invert score
                pass  # ORDINAL_MAP already accounts for standard wellness orientation

            normalized[category][field] = float(mapped)

    return normalized