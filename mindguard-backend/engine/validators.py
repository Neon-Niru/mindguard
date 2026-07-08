from .schema import ENGINE_SCHEMA


class ValidationError(Exception):
    pass



def validate_payload(data: dict):

    if not isinstance(data, dict):
        raise ValidationError(
            "Input payload must be a dictionary"
        )


    for category, fields in ENGINE_SCHEMA.items():

        if category not in data:
            raise ValidationError(
                f"Missing category: {category}"
            )


        if not isinstance(data[category], dict):
            raise ValidationError(
                f"Category '{category}' must be an object"
            )


        for field_name, rules in fields.items():


            if rules.get("required", False):

                if field_name not in data[category]:

                    raise ValidationError(
                        f"Missing field '{field_name}' in '{category}'"
                    )


            if field_name not in data[category]:
                continue


            value = data[category][field_name]


            expected_type = rules.get("type")


            if expected_type:

                if expected_type == "number":

                    if not isinstance(value, (int, float)):
                        raise ValidationError(
                            f"Field '{field_name}' must be a number"
                        )


                elif expected_type == "string":

                    if not isinstance(value, str):
                        raise ValidationError(
                            f"Field '{field_name}' must be a string"
                        )


            if "enum" in rules:

                if value not in rules["enum"]:

                    raise ValidationError(
                        f"Invalid value '{value}' for '{field_name}'"
                    )


            if "min" in rules:

                if value < rules["min"]:
                    raise ValidationError(
                        f"'{field_name}' below minimum range"
                    )


            if "max" in rules:

                if value > rules["max"]:
                    raise ValidationError(
                        f"'{field_name}' above maximum range"
                    )


    return True



# Backwards compatibility
# Some tests/services may use validate()

def validate(data: dict):

    return validate_payload(data)