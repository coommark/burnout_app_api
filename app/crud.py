from datetime import date, timedelta
import numpy as np
from sqlalchemy.orm import Session

from app.models import User, Assessment, Prediction, DailySummaryRolling7D, AuditLog
from app.schemas import DailyAssessmentIn as AssessmentCreate
from typing import Optional, Tuple
import uuid


def create_user(db: Session, email: str, password_hash: str, full_name: str) -> User:
    user = User(email=email, password_hash=password_hash, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter_by(email=email).first()


def update_user(db: Session, user: User, full_name: Optional[str] = None) -> User:
    if full_name:
        user.full_name = full_name
    db.commit()
    return user


def log_action(db: Session, user_id: str, action: str, details: str = "") -> None:
    entry = AuditLog(user_id=user_id, action=action, details=details)
    db.add(entry)
    db.commit()


def add_assessment_and_prediction(
    db: Session, user: User, assessment_data: AssessmentCreate, prediction_result: dict
) -> Tuple[Assessment, Prediction]:
    assess = Assessment(
        user_id=user.id,
        date=date.today(),
        tired_score=assessment_data.tired_score,
        capable_score=assessment_data.capable_score,
        meaningful_score=assessment_data.meaningful_score,
    )
    db.add(assess)
    db.commit()
    db.refresh(assess)

    pred = Prediction(
        assessment_id=assess.id,
        burnout_risk=prediction_result["burnout_risk"],
        confidence=prediction_result["confidence"],
        model_version=prediction_result["model_version"],
    )
    db.add(pred)
    db.commit()
    return assess, pred


def compute_rolling_summary(db: Session, user: User) -> Optional[DailySummaryRolling7D]:
    today = date.today()
    week_ago = today - timedelta(days=6)

    rows = db.query(Assessment).filter(
        Assessment.user_id == user.id,
        Assessment.date >= week_ago
    ).all()

    if not rows:
        return None

    arr = np.array([[r.tired_score, r.capable_score, r.meaningful_score] for r in rows])
    avg = np.mean(arr, axis=0)

    summary = DailySummaryRolling7D(
        user_id=user.id,
        summary_date=today,
        avg_tired_last_7_days=float(avg[0]),
        avg_capable_last_7_days=float(avg[1]),
        avg_meaningful_last_7_days=float(avg[2]),
        features_json={
            "avg_tired": avg[0],
            "avg_capable": avg[1],
            "avg_meaningful": avg[2]
        }
    )
    db.add(summary)
    db.commit()
    db.refresh(summary)
    return summary
