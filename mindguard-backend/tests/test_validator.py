import unittest

from engine.validators import ValidationError, validate_payload
from tests.fixtures import BAD_PAYLOAD


class ValidatorTests(unittest.TestCase):

    def test_complete_payload_is_valid(self):
        self.assertTrue(validate_payload(BAD_PAYLOAD, require_all=True))

    def test_partial_payload_is_allowed_by_default(self):
        self.assertTrue(validate_payload({"sleep": {"hours": 7}}))

    def test_partial_payload_can_be_rejected(self):
        with self.assertRaises(ValidationError):
            validate_payload({"sleep": {"hours": 7}}, require_all=True)

    def test_unknown_category_rejected(self):
        with self.assertRaises(ValidationError):
            validate_payload({"made_up": {"x": 1}})

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValidationError):
            validate_payload({"sleep": {"made_up": 1}})

    def test_invalid_ordinal_rejected(self):
        with self.assertRaises(ValidationError):
            validate_payload({"sleep": {"quality": "bananas"}})

    def test_numeric_ordinal_out_of_range_rejected(self):
        with self.assertRaises(ValidationError):
            validate_payload({"sleep": {"quality": 150}})

    def test_continuous_range_enforced(self):
        with self.assertRaises(ValidationError):
            validate_payload({"sleep": {"hours": 99}})

    def test_continuous_requires_number(self):
        with self.assertRaises(ValidationError):
            validate_payload({"sleep": {"hours": "8"}})

    def test_non_dict_payload_rejected(self):
        with self.assertRaises(ValidationError):
            validate_payload([])


if __name__ == "__main__":
    unittest.main()
