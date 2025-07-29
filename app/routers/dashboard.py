from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Prediction
from app.schemas import DashboardOut, DailyPredictionOut
from app.dependencies import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardOut)
def dashboard(current=Depends(get_current_user), db: Session = Depends(get_db)):
    today = date.today()

    # Today's prediction (if any), based on predicted_at date
    today_prediction = (
        db.query(Prediction)
        .filter(
            Prediction.assessment.has(user_id=current.id),
            func.date(Prediction.predicted_at) == today,
        )
        .first()
    )

    # Last 5 predictions before today
    recent_predictions = (
        db.query(Prediction)
        .filter(
            Prediction.assessment.has(user_id=current.id),
            func.date(Prediction.predicted_at) < today,
        )
        .order_by(Prediction.predicted_at.desc())
        .limit(5)
        .all()
    )

    return DashboardOut(
        today_prediction=DailyPredictionOut(
            date=today_prediction.predicted_at.date(),
            burnout_risk=today_prediction.burnout_risk,
            confidence=today_prediction.confidence,
            model_version=today_prediction.model_version,
        ) if today_prediction else None,
        recent_predictions=[
            DailyPredictionOut(
                date=pred.predicted_at.date(),
                burnout_risk=pred.burnout_risk,
                confidence=pred.confidence,
                model_version=pred.model_version,
            )
            for pred in recent_predictions
        ],
    )
