"""CR-3: iesniegumu saraksts darbiniekam (piegādātāja testi)."""

import pytest

from app import storage


def test_list_received(client):
    storage.reset()
    response = client.get("/submissions?status=RECEIVED")
    assert response.status_code == 200
    assert all(item["status"] == "RECEIVED" for item in response.json())


def test_list_by_topic(client):
    storage.reset()
    response = client.get("/submissions?topic=ROADS")
    assert response.status_code == 200
    assert all(item["topic"] == "ROADS" for item in response.json())


def test_list_all(client):
    storage.reset()
    response = client.get("/submissions")
    assert response.status_code == 200
    assert len(response.json()) == 3


# Regresija: filtri agrāk tika ielīmēti SQL vaicājumā kā teksts (SQL injekcija).
INJECTIONS = [
    "RECEIVED' OR '1'='1",
    "x' UNION SELECT * FROM submissions --",
    "received",
]


@pytest.mark.parametrize("value", INJECTIONS)
def test_list_rejects_status_outside_allowed_list(client, value):
    storage.reset()
    response = client.get("/submissions", params={"status": value})
    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert value not in response.text


@pytest.mark.parametrize("value", INJECTIONS)
def test_list_rejects_topic_outside_allowed_list(client, value):
    storage.reset()
    response = client.get("/submissions", params={"topic": value})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("field", ["status", "topic"])
def test_storage_rejects_filter_outside_allowed_list(field):
    storage.reset()
    with pytest.raises(ValueError):
        storage.list_submissions(**{field: "RECEIVED' OR '1'='1"})


def test_list_status_and_topic_combined(client):
    storage.reset()
    response = client.get(
        "/submissions", params={"status": "RECEIVED", "topic": "ROADS"}
    )
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(i["status"] == "RECEIVED" and i["topic"] == "ROADS" for i in items)
