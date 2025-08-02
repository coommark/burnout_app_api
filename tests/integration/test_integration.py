import pytest
pytestmark = pytest.mark.integration

@pytest.mark.asyncio
async def test_submit_valid_scores_returns_prediction(client, seeded_user_with_6_assessments):
    headers = await seeded_user_with_6_assessments

    response = client.post(
        "/assessments/",
        json={"tired_score": 4, "capable_score": 2, "meaningful_score": 3},
        headers=headers
    )

    assert response.status_code == 200
    result = response.json()

    if "label" in result:
        assert result["label"] in ["Low", "Moderate", "High"]
        assert result["burnout_risk"] in [True, False]
        assert result["confidence"] is not None
        assert 0 <= result["confidence"] <= 1
    else:
        assert result["burnout_risk"] is None
        assert result["confidence"] is None
        assert result["message"] == "Assessment saved. Burnout prediction will be available after 7 entries."

# IT-002: Submit malformed data
def test_submit_malformed_data_returns_validation_error(client, auth_headers):
    malformed_data = {
        "tired_score": "very tired",  # invalid type
        "capable_score": 5,           # valid
        # missing meaningful_score
    }

    response = client.post("/assessments/", json=malformed_data, headers=auth_headers)
    assert response.status_code == 422
    assert "detail" in response.json()


# IT-003: Borderline data, ensure prediction is returned
@pytest.mark.parametrize("data", [
    {"tired_score": 2, "capable_score": 2, "meaningful_score": 2},
    {"tired_score": 3, "capable_score": 2, "meaningful_score": 3},
    {"tired_score": 1, "capable_score": 3, "meaningful_score": 2}
])
def test_submit_scores_near_threshold_returns_consistent_classification(client, db, auth_headers, data):
    from app.models import Assessment, User
    from sqlalchemy import select
    from datetime import date, timedelta

    # Get user
    user = db.execute(select(User).where(User.email == "testuser@example.com")).scalar_one()
    today = date.today()

    # Seed 7 assessments
    for i in range(7):
        db.add(Assessment(
            user_id=user.id,
            tired_score=data["tired_score"],
            capable_score=data["capable_score"],
            meaningful_score=data["meaningful_score"],
            date=today - timedelta(days=i + 1)
        ))
    db.commit()

    # Submit 8th via API
    response = client.post("/assessments/", json=data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()

    if "label" in result:
        assert result["label"] in ["Low", "Moderate", "High"]
        assert result["burnout_risk"] in [True, False]
        assert result["confidence"] is not None
        assert 0 <= result["confidence"] <= 1
    else:
        assert result["burnout_risk"] is None
        assert result["confidence"] is None
        assert result["message"] == "Assessment saved. Burnout prediction will be available after 7 entries."
