from fastapi.testclient import TestClient
from src.app import app, activities
import copy
import pytest

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # snapshot original state and restore after each test
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant():
    email = "test@example.com"
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_duplicate_signup_allowed():
    email = "dup@example.com"
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert activities["Chess Club"]["participants"].count(email) == 2


def test_signup_missing_activity():
    resp = client.post("/activities/Nope/signup?email=x@x.com")
    assert resp.status_code == 404


def test_delete_participant():
    email = "michael@mergington.edu"
    resp = client.delete(f"/activities/Chess%20Club/participants/{email}")
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_participant():
    resp = client.delete("/activities/Chess%20Club/participants/noone@x.com")
    assert resp.status_code == 404
