import pytest

from bri.validation import ValidationError, validate_intake


def valid_payload(**overrides):
    payload = {"title": "VPN access", "description": "Please grant VPN access for my new laptop.", "department": "IT", "channel": "Portal", "declared_urgency": "Normal"}
    payload.update(overrides)
    return payload


def test_intake_normalizes_safe_whitespace():
    command = validate_intake(valid_payload(title="  VPN access  "))
    assert command.title == "VPN access"


@pytest.mark.parametrize("field,value", [("title", " "), ("description", "short"), ("department", "Unknown")])
def test_intake_rejects_invalid_values(field, value):
    with pytest.raises(ValidationError):
        validate_intake(valid_payload(**{field: value}))

