"""CR-1: personas koda pārbaude iesniegumā."""

import pytest


@pytest.mark.parametrize(
    ("code", "stored"),
    [
        ("010190-12349", "01019012349"),  # AK1 ar defisi
        ("01019012349", "01019012349"),  # AK2 bez defises
        ("321234-56789", "32123456789"),  # AK3 jaunais formāts
        (" 010190-12349 ", "01019012349"),  # AK9 atstarpes nogrieztas
        ("290200-20009", "29020020009"),  # 29.02.2000, garais gads
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
        "010190-12340",  # AK4 nepareizs kontrolcipars
        "310290-12345",  # AK5 31. februāris
        "310290-10002",  # 31. februāris ar pareizu kontrolciparu
        "010190-123",  # AK6 par maz ciparu
        "01019A-12349",  # AK7 satur burtu
        "010190-30002",  # gadsimta cipars 3
        "0101901-2349",  # defise nepareizā vietā
    ],
)
def test_invalid_personal_code_is_rejected(client, valid_payload, code):
    valid_payload["personalCode"] = code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "personalCode", "issue": "INVALID_FORMAT"}]


@pytest.mark.parametrize("code", ["", "   "])
def test_empty_personal_code_is_required(client, valid_payload, code):
    # AK8 tukšs lauks
    valid_payload["personalCode"] = code
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "personalCode", "issue": "REQUIRED"}
    ]


def test_missing_personal_code_is_required(client, valid_payload):
    # AK8 lauks iztrūkst
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "personalCode", "issue": "REQUIRED"}
    ]


def test_rejected_code_is_not_echoed(client, valid_payload):
    valid_payload["personalCode"] = "010190-12340"
    response = client.post("/submissions", json=valid_payload)
    assert "010190-12340" not in response.text


def test_omd_receives_normalized_code(client, valid_payload, fake_omd):
    valid_payload["personalCode"] = " 010190-12349 "
    client.post("/submissions", json=valid_payload)
    assert fake_omd.calls == ["01019012349"]
