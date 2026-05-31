import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/detections.db")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")


settings = Settings()
