import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# snapshot of the original in-memory database
_baseline_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the `activities` dict before every test."""
    activities.clear()
    activities.update(copy.deepcopy(_baseline_activities))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all(client):
    # Arrange: state reset by fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == _baseline_activities


def test_signup_successful(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@example.com"
    assert email not in activities[activity]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    assert email in activities[activity]["participants"]


def test_signup_activity_not_found(client):
    # Act
    response = client.post(
        "/activities/Nonexistent/signup", params={"email": "foo@bar.com"}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate(client):
    # Arrange
    activity = "Chess Club"
    email = "michael@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
