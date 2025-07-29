from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth import get_current_user
from app.dependencies import get_db
from app.crud import compute_rolling_summary
from app.schemas import DashboardOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/", response_model=DashboardOut)
def dashboard(current=Depends(get_current_user), db: Session = Depends(get_db)):
    summary = compute_rolling_summary(db, current)
    last_pred = current.assessments[-1].prediction if current.assessments else None
    if not last_pred:
        return DashboardOut(burnout_risk=False, confidence=0.0, model_version="", summary=None)
    return DashboardOut(
        burnout_risk=last_pred.burnout_risk,
        confidence=last_pred.confidence,
        model_version=last_pred.model_version,
        summary=summary.features_json if summary else None
    )
