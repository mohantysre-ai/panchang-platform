from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "State-Adaptive Panchang API"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    redis_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl_seconds: int = 86400
    postgres_enabled: bool = False
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/panchang"
    json_storage_enabled: bool = True
    data_dir: str = "./data"
    default_lat: float = 12.9716
    default_lon: float = 77.5946
    default_timezone: str = "Asia/Kolkata"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def absolute_data_dir(self):
        return Path(self.data_dir).resolve()

settings = Settings()
