from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import DailyAssessmentIn
from app.dependencies import get_db
from app.auth import get_current_user
from app.crud import add_assessment_and_prediction, compute_rolling_summary, log_action
from app.predict import predict_burnout

router = APIRouter(prefix="/assessments", tags=["assessments"])

@router.post("/")
def submit_daily_assessment(data: DailyAssessmentIn, db: Session = Depends(get_db),
                            current=Depends(get_current_user)):
    # compute weekly summary, predict
    summary = compute_rolling_summary(db, current)
    if not summary:
        # fallback: only today
        avg_tired = data.tired_score; avg_capable = data.capable_score; avg_meaningful = data.meaningful_score
    else:
        avg_tired = summary.avg_tired_last_7_days
        avg_capable = summary.avg_capable_last_7_days
        avg_meaningful = summary.avg_meaningful_last_7_days
    pred = predict_burnout(avg_tired, avg_capable, avg_meaningful)
    assess, prediction = add_assessment_and_prediction(db, current, data, pred)
    log_action(db, current.id, "submit_assessment", details=f"assess_id={assess.id}")
    return {"burnout_risk": pred["burnout_risk"], "confidence": pred["confidence"]}

