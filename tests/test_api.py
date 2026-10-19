import pytest
from app import create_app
from app import db as dbmod

VALID = {"name": "Ravi Kumar", "category": "Technical",
         "description": "Internet is not working since morning.", "priority": "Medium"}


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_create_complaint_success(client):
    res = client.post("/api/complaints", json=VALID)
    assert res.status_code == 201
    body = res.get_json()
    assert body["complaint_id"].startswith("CMP-")
    assert body["priority"] == "High"          # escalated by "not working"
    assert body["assigned_to"] == "Tech Support Team"


def test_create_complaint_invalid(client):
    res = client.post("/api/complaints", json={**VALID, "name": ""})
    assert res.status_code == 422
    assert "name" in res.get_json()["fields"]


def test_non_json_body_rejected(client):
    res = client.post("/api/complaints", data="hello", content_type="text/plain")
    assert res.status_code == 400


def test_track_and_not_found(client):
    cid = client.post("/api/complaints", json=VALID).get_json()["complaint_id"]
    assert client.get(f"/api/complaints/{cid}").status_code == 200
    assert client.get("/api/complaints/CMP-0000-9999").status_code == 404


def test_status_update_and_counts(client):
    cid = client.post("/api/complaints", json=VALID).get_json()["complaint_id"]
    assert client.patch(f"/api/complaints/{cid}/status", json={"status": "Resolved"}).status_code == 200
    counts = client.get("/api/complaints").get_json()["counts"]
    assert counts["Resolved"] == 1 and counts["Pending"] == 0


def test_invalid_status_rejected(client):
    cid = client.post("/api/complaints", json=VALID).get_json()["complaint_id"]
    assert client.patch(f"/api/complaints/{cid}/status", json={"status": "Done"}).status_code == 400


def test_two_complaints_get_unique_ids(client):
    a = client.post("/api/complaints", json=VALID).get_json()["complaint_id"]
    b = client.post("/api/complaints", json=VALID).get_json()["complaint_id"]
    assert a != b


def test_database_failure_returns_500(client, monkeypatch):
    def boom(*a, **k):
        raise dbmod.DatabaseError("disk full")
    monkeypatch.setattr(dbmod, "insert_complaint", boom)
    res = client.post("/api/complaints", json=VALID)
    assert res.status_code == 500
    assert "error" in res.get_json()
