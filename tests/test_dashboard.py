from datetime import timedelta, date

def test_dashboard_data(auth_headers, client):
    # Submit 7 assessments to qualify for prediction
    for _ in range(7):
        response = client.post("/assessments/", json={
            "tired_score": 3,
            "capable_score": 2,
            "meaningful_score": 4
        }, headers=auth_headers)
        assert response.status_code == 200

    # Fetch dashboard
    response = client.get("/dashboard/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Ensure structure is present
    assert "today_prediction" in data
    assert "recent_predictions" in data

    # If prediction is available, check it
    prediction = data["today_prediction"]
    if prediction is not None:
        assert prediction["burnout_risk"] in [True, False]
        assert 0 <= prediction["confidence"] <= 1
        assert prediction["label"] in ["Low", "Moderate", "High"]
        assert isinstance(prediction["model_version"], str)
