import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Date, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .dependencies import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    assessments = relationship("Assessment", back_populates="user")
    logs = relationship("AuditLog", back_populates="user")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    tired_score = Column(Integer)
    capable_score = Column(Integer)
    meaningful_score = Column(Integer)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    prediction = relationship("Prediction", uselist=False, back_populates="assessment")
    user = relationship("User", back_populates="assessments")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    burnout_risk = Column(Boolean)
    label = Column(String)  # <--- New column
    confidence = Column(Float)
    model_version = Column(String)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    assessment = relationship("Assessment", back_populates="prediction")


class DailySummaryRolling7D(Base):
    __tablename__ = "daily_summary_rolling_7d"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    summary_date = Column(Date)
    avg_tired_last_7_days = Column(Float)
    avg_capable_last_7_days = Column(Float)
    avg_meaningful_last_7_days = Column(Float)
    features_json = Column(JSONB)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="logs")
