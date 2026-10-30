from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    
    DATABASE_URL: str
    LOG_LEVEL: str 
    MODEL_NAME: str | None
    GROQ_API_KEY: str | None

    @property
    def db_path(self) -> Path:
        return BASE_DIR / "data" / "enterprise.db"

    @property
    def seed_sql_path(self) -> Path:
        return BASE_DIR / "data" / "seed_data.sql"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()