from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    full_name: Optional[str]

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenWithUser(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    user_id: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetComplete(BaseModel):
    token: str
    new_password: constr(min_length=8)

class ProfileEdit(BaseModel):
    full_name: Optional[str]

class DailyAssessmentIn(BaseModel):
    tired_score: int
    capable_score: int
    meaningful_score: int

class DailyPredictionOut(BaseModel):
    date: date
    burnout_risk: bool
    confidence: float
    model_version: str


class DashboardOut(BaseModel):
    today_prediction: Optional[DailyPredictionOut]
    recent_predictions: List[DailyPredictionOut]