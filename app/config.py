from pydantic_settings import BaseSettings  # ✅ use pydantic_settings not pydantic

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RESET_TOKEN_EXPIRE_MINUTES: int = 10
    MAIL_FROM: str
    EMAIL_BACKEND: str = "smtp"
    APP_HOST: str

    class Config:
        env_file = ".env"

settings = Settings()  # ✅ make sure this is at the bottom