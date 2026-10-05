"""CR-1: personas koda pārbaude iesniegumā."""

import logging

import pytest


@pytest.mark.parametrize(
    ("code", "stored"),
    [
        ("32000000001", "32000000001"),  # AK1 11 cipari
        ("320000-00001", "32000000001"),  # AK2 ar defisi
        (" 32000000001 ", "32000000001"),  # AK3 atstarpes noņemtas
        ("311299-21233", "31129921233"),  # AK8 vecais formāts
        ("010190-12340", "01019012340"),  # kontrolciparu nepārbauda
        ("310290-12345", "31029012345"),  # datumu nepārbauda
    ],
)
def test_valid_personal_code_is_accepted(client, valid_payload, code, stored):
    valid_payload["personalCode"] = code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
    saved = client.get(f"/submissions/{response.json()['id']}").json()
    assert saved["personalCode"] == stored


@pytest.mark.parametrize(
    "code",
    [
        "3200000000",  # AK4 10 cipari
        "320000000012",  # AK5 12 cipari
        "32000000O01",  # AK6 burts O
        "3200-0000001",  # AK9 defise nepareizā vietā
        "320000--00001",  # divas defises
    ],
)
def test_invalid_personal_code_is_rejected(client, valid_payload, code):
    valid_payload["personalCode"] = code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "personalCode", "issue": "INVALID_FORMAT"}]


def test_missing_personal_code_is_required(client, valid_payload):
    # AK7 lauka nav
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "personalCode", "issue": "REQUIRED"}
    ]


@pytest.mark.parametrize("code", ["", "   "])
def test_empty_personal_code_is_required(client, valid_payload, code):
    # Precizējums: tukša virkne vai tikai atstarpes kā lauka nav
    valid_payload["personalCode"] = code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "personalCode", "issue": "REQUIRED"}
    ]


def test_rejected_code_is_not_echoed(client, valid_payload, caplog):
    # Precizējums: ievadīto kodu neatkārto ne atbildē, ne žurnālā
    valid_payload["personalCode"] = "32000000O01"
    with caplog.at_level(logging.DEBUG):
        response = client.post("/submissions", json=valid_payload)
    assert "32000000O01" not in response.text
    assert "32000000O01" not in caplog.text


def test_omd_receives_normalized_code(client, valid_payload, fake_omd):
    valid_payload["personalCode"] = " 320000-00001 "
    client.post("/submissions", json=valid_payload)
    assert fake_omd.calls == ["32000000001"]
