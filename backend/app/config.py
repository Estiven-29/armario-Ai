from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    database_url: str = f"sqlite:///{BASE_DIR / 'armario.db'}"
    uploads_dir: Path = BASE_DIR / "uploads"

    @property
    def ai_enabled(self) -> bool:
        return bool(self.gemini_api_key)


settings = Settings()
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
