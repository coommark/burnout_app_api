import pytest
from app.models import User

@pytest.fixture
def test_user(client):  # use client so dependency override works
    response = client.post("/users/register", json={
        "email": "test@example.com",
        "password": "testpass",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    return response.json()

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/users/login", data={
        "username": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_submit_daily_assessment(auth_headers, client):
    response = client.post("/assessments/", json={
        "tired_score": 3,
        "capable_score": 2,
        "meaningful_score": 4
    }, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "burnout_risk" in data
    assert "confidence" in data

def test_prediction_integration_valid(auth_headers, client):
    response = client.post("/assessments/", json={
        "tired_score": 4, "capable_score": 1, "meaningful_score": 2
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["burnout_risk"] in [True, False]

def test_prediction_integration_malformed(auth_headers, client):
    response = client.post("/assessments/", json={
        "tired_score": "bad", "capable_score": 1
    }, headers=auth_headers)
    assert response.status_code == 422

def test_prediction_threshold_consistency(auth_headers, client):
    for score in range(0, 5):
        response = client.post("/assessments/", json={
            "tired_score": score,
            "capable_score": 2,
            "meaningful_score": 3
        }, headers=auth_headers)
        assert response.status_code == 200
        assert "burnout_risk" in response.json()
