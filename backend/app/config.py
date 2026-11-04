from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = (
        "postgresql+asyncpg://mathpractice:mathpractice@localhost:5432/mathpractice"
    )
    frontend_origin: str = "http://localhost:5173"
    google_api_key: str | None = None
    google_model: str = "gemini-flash-lite-latest"
    textbook_pdf_path: str = "../data/source/Maths_Textbook.pdf"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
