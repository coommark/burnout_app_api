from pydantic import BaseModel, EmailStr, constr
from typing import Optional

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

class DashboardOut(BaseModel):
    burnout_risk: bool
    confidence: float
    model_version: str
    summary: Optional[dict]
