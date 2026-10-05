"""CR-4: publisks iesnieguma statuss iedzīvotājam."""


def test_status_returns_only_id_status_due_date(client, valid_payload):
    created = client.post("/submissions", json=valid_payload).json()
    response = client.get(f"/submissions/{created['id']}/status")
    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "status": "RECEIVED",
        "dueDate": created["dueDate"],
    }


def test_status_has_no_personal_data(client, valid_payload):
    created = client.post("/submissions", json=valid_payload).json()
    text = client.get(f"/submissions/{created['id']}/status").text
    for value in (
        valid_payload["personalCode"],
        valid_payload["fullName"],
        valid_payload["email"],
        valid_payload["body"],
    ):
        assert value not in text


def test_status_unknown_returns_404(client):
    response = client.get("/submissions/IES-2026-999999/status")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_status_page_is_served(client):
    response = client.get("/ui/statuss.html")
    assert response.status_code == 200
    assert "/status" in response.text
