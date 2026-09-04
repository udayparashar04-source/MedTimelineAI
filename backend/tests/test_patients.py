"""Patient API tests."""

from fastapi.testclient import TestClient


def test_create_patient(client: TestClient):
    response = client.post(
        "/patients",
        json={"display_name": "Alex Patient", "notes": "fixture"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["display_name"] == "Alex Patient"
    assert body["notes"] == "fixture"
    assert body["created_at"]
    assert body["updated_at"]


def test_list_and_get_patients(client: TestClient):
    created = client.post("/patients", json={"display_name": "Sam"}).json()
    listed = client.get("/patients")
    assert listed.status_code == 200
    ids = {row["id"] for row in listed.json()}
    assert created["id"] in ids

    fetched = client.get(f"/patients/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["display_name"] == "Sam"


def test_get_missing_patient_returns_404(client: TestClient):
    response = client.get("/patients/999999")
    assert response.status_code == 404
