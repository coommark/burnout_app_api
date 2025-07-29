from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from fastapi_mail import FastMail, MessageSchema, MessageType
from app.schemas import UserCreate, TokenWithUser, PasswordResetRequest, PasswordResetComplete, UserOut, ProfileEdit
from app.dependencies import get_db
from app.crud import create_user, get_user_by_email, update_user, log_action
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.config import settings
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut)
def register_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    pw_hash = hash_password(data.password)
    user = create_user(db, data.email, pw_hash, data.full_name)
    log_action(db, user.id, "register_user", f"email={user.email}")
    return user

@router.post("/login", response_model=TokenWithUser)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.id)
    user.last_login = datetime.utcnow(); db.commit()
    log_action(db, user.id, "login")
    return {"access_token": token, "user": user}

@router.post("/password-recover")
def recover_password(req: PasswordResetRequest, background_tasks: BackgroundTasks,
                     db: Session = Depends(get_db)):
    user = get_user_by_email(db, req.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    token_expires = timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": user.id,
                        "exp": datetime.utcnow() + token_expires},
                       settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    reset_link = f"{settings.APP_HOST}/reset-password?token={token}"
    message = MessageSchema(subject="Password Reset",
                             recipients=[user.email],
                             body=f"Click here: {reset_link}",
                             subtype=MessageType.html)
    fm = FastMail(settings)
    background_tasks.add_task(fm.send_message, message)
    log_action(db, user.id, "recover_password")
    return {"msg": "Password reset email sent"}

@router.post("/password-reset")
def complete_reset(req: PasswordResetComplete, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(req.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user = db.query(User).get(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user.password_hash = hash_password(req.new_password)
    db.commit()
    log_action(db, user.id, "reset_password")
    return {"msg": "Password updated"}

@router.put("/profile", response_model=UserOut)
def edit_profile(data: ProfileEdit, current=Depends(get_current_user), db: Session = Depends(get_db)):
    user = update_user(db, current, full_name=data.full_name)
    log_action(db, user.id, "edit_profile", details=f"name={data.full_name}")
    return user
