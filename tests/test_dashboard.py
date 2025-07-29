def test_dashboard_data(auth_headers, client):
    response = client.get("/dashboard/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "burnout_risk" in data
    assert "confidence" in data
    assert "model_version" in data
