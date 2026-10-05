"""CR-1: personas koda pārbaude (tracker/CR-1.md). Viena kritēriju rinda = viens tests.

Sagaidāmās vērtības ņemtas no pieteikuma kritērijiem un docs/openapi.yaml.
"Saglabāts" pārbauda caur GET /submissions/{id} (shēma Submission satur personalCode);
POST 201 atbildē (SubmissionCreated) personalCode pēc līguma nav.
"""

import pytest

ISSUE_ENUM = {"REQUIRED", "INVALID_FORMAT", "TOO_LONG"}


def _submit(client, payload, personal_code):
    payload["personalCode"] = personal_code
    return client.post("/submissions", json=payload)


def _stored_code(client, response):
    submission_id = response.json()["id"]
    stored = client.get(f"/submissions/{submission_id}")
    assert stored.status_code == 200
    return stored.json()["personalCode"]


def _assert_contract_error(response, issue, raw_input=None):
    """400 atbilst līguma Error shēmai (components/schemas/Error) un neatkārto ievadi."""
    assert response.status_code == 400
    body = response.json()
    assert set(body) == {"error"}
    error = body["error"]
    assert isinstance(error.get("code"), str)
    assert isinstance(error.get("message"), str)
    assert error["code"] == "VALIDATION_ERROR"
    assert isinstance(error.get("details"), list)
    for item in error["details"]:
        assert {"field", "issue"} <= set(item)
        assert isinstance(item["field"], str)
        assert item["issue"] in ISSUE_ENUM
    assert {"field": "personalCode", "issue": issue} in error["details"]
    if raw_input is not None:
        # Precizējums: kļūdā ievadīto kodu neatkārto (ne neapstrādāto, ne normalizēto).
        assert raw_input not in response.text
        normalised = raw_input.strip().replace("-", "")
        assert normalised not in response.text


def test_cr1_ac1_new_format_accepted(client, valid_payload):
    """AC1: "32000000001" -> 201, saglabāts "32000000001"."""
    response = _submit(client, valid_payload, "32000000001")
    assert response.status_code == 201
    assert _stored_code(client, response) == "32000000001"


def test_cr1_ac2_hyphen_normalised(client, valid_payload):
    """AC2: "320000-00001" -> 201, saglabāts "32000000001"."""
    response = _submit(client, valid_payload, "320000-00001")
    assert response.status_code == 201
    assert _stored_code(client, response) == "32000000001"


def test_cr1_ac3_outer_spaces_removed(client, valid_payload):
    """AC3: " 32000000001 " -> 201, atstarpes noņemtas."""
    response = _submit(client, valid_payload, " 32000000001 ")
    assert response.status_code == 201
    assert _stored_code(client, response) == "32000000001"


def test_cr1_ac4_ten_digits_invalid(client, valid_payload):
    """AC4: "3200000000" (10 cipari) -> 400 INVALID_FORMAT."""
    code = "3200000000"
    _assert_contract_error(_submit(client, valid_payload, code), "INVALID_FORMAT", code)


def test_cr1_ac5_twelve_digits_invalid(client, valid_payload):
    """AC5: "320000000012" (12 cipari) -> 400 INVALID_FORMAT."""
    code = "320000000012"
    _assert_contract_error(_submit(client, valid_payload, code), "INVALID_FORMAT", code)


def test_cr1_ac6_letter_o_invalid(client, valid_payload):
    """AC6: "32000000O01" (burts O) -> 400 INVALID_FORMAT."""
    code = "32000000O01"
    _assert_contract_error(_submit(client, valid_payload, code), "INVALID_FORMAT", code)


def test_cr1_ac7_missing_field_required(client, valid_payload):
    """AC7: lauka nav -> 400 REQUIRED."""
    del valid_payload["personalCode"]
    _assert_contract_error(client.post("/submissions", json=valid_payload), "REQUIRED")


@pytest.mark.parametrize("blank", ["", "   "])
def test_cr1_blank_value_required(client, valid_payload, blank):
    """Precizējums: tukša virkne vai tikai atstarpes -> 400 REQUIRED (tāpat kā lauka nav)."""
    _assert_contract_error(_submit(client, valid_payload, blank), "REQUIRED")


def test_cr1_ac8_old_format_accepted(client, valid_payload):
    """AC8: "311299-21233" -> 201, saglabāts "31129921233"."""
    response = _submit(client, valid_payload, "311299-21233")
    assert response.status_code == 201
    assert _stored_code(client, response) == "31129921233"


def test_cr1_ac9_hyphen_wrong_place_invalid(client, valid_payload):
    """AC9: "3200-0000001" (defise nepareizā vietā) -> 400 INVALID_FORMAT."""
    code = "3200-0000001"
    _assert_contract_error(_submit(client, valid_payload, code), "INVALID_FORMAT", code)
