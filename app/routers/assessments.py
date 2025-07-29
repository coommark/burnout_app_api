from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import DailyAssessmentIn
from app.dependencies import get_db
from app.auth import get_current_user
from app.crud import add_assessment_and_prediction, compute_rolling_summary, log_action
from app.predict import predict_burnout
from ..models import User

router = APIRouter(prefix="/assessments", tags=["assessments"])

@router.post("/")
def submit_daily_assessment(
    data: DailyAssessmentIn,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user)
):
    summary = compute_rolling_summary(db, current)

    if not summary:
        assess, _ = add_assessment_and_prediction(db, current, data, None)
        log_action(db, current.id, "submit_assessment", details=f"assess_id={assess.id}")
        return {
            "burnout_risk": None,
            "confidence": None,
            "message": "Assessment saved. Burnout prediction will be available after 7 entries."
        }

    pred = predict_burnout(
        summary.avg_tired_last_7_days,
        summary.avg_capable_last_7_days,
        summary.avg_meaningful_last_7_days
    )
    assess, prediction = add_assessment_and_prediction(db, current, data, pred)
    log_action(db, current.id, "submit_assessment", details=f"assess_id={assess.id}")
    return {"burnout_risk": pred["burnout_risk"], "confidence": pred["confidence"]}
