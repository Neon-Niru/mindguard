from .schema import ENGINE_SCHEMA
from .normalizer import ORDINAL_LOOKUP


class ValidationError(Exception):
    pass


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_payload(data: dict, require_all: bool = False):

    if not isinstance(data, dict):
        raise ValidationError(
            "Input payload must be a dictionary"
        )

    unknown_categories = [
        category for category in data
        if category not in ENGINE_SCHEMA
    ]
    if unknown_categories:
        raise ValidationError(
            f"Unknown categories: {', '.join(sorted(unknown_categories))}"
        )

    for category, fields in ENGINE_SCHEMA.items():

        if category not in data:
            if require_all:
                raise ValidationError(
                    f"Missing category: {category}"
                )
            continue

        category_data = data[category]

        if not isinstance(category_data, dict):
            raise ValidationError(
                f"Category '{category}' must be an object"
            )

        unknown_fields = [
            field_name for field_name in category_data
            if field_name not in fields
        ]
        if unknown_fields:
            raise ValidationError(
                f"Unknown fields in '{category}': "
                f"{', '.join(sorted(unknown_fields))}"
            )

        for field_name, rules in fields.items():

            if field_name not in category_data:
                if require_all and rules.get("required", False):
                    raise ValidationError(
                        f"Missing field '{field_name}' in '{category}'"
                    )
                continue

            value = category_data[field_name]

            if value is None:
                continue

            expected_type = rules.get("type")

            if expected_type in ("continuous", "percentage"):

                if not _is_number(value):
                    raise ValidationError(
                        f"Field '{field_name}' must be a number"
                    )

                if expected_type == "percentage" and not (0 <= value <= 100):
                    raise ValidationError(
                        f"'{field_name}' must be between 0 and 100"
                    )

                if "min" in rules and value < rules["min"]:
                    raise ValidationError(
                        f"'{field_name}' below minimum range"
                    )

                if "max" in rules and value > rules["max"]:
                    raise ValidationError(
                        f"'{field_name}' above maximum range"
                    )

            elif expected_type == "ordinal":

                if isinstance(value, str):
                    if value.strip().lower() not in ORDINAL_LOOKUP:
                        raise ValidationError(
                            f"Invalid value '{value}' for '{field_name}'"
                        )
                elif not _is_number(value) or not (0 <= value <= 100):
                    raise ValidationError(
                        f"Field '{field_name}' must be an ordinal label "
                        "or a number between 0 and 100"
                    )

            if "enum" in rules and value not in rules["enum"]:
                raise ValidationError(
                    f"Invalid value '{value}' for '{field_name}'"
                )

    return True


# Backwards compatibility
# Some tests/services may use validate()

def validate(data: dict):

    return validate_payload(data)
