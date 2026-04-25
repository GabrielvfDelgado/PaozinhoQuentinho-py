from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql+asyncpg://user:password@postgres:5432/evolution"
    evolution_api_url: str = "http://localhost:8080"
    evolution_api_instance: str = "paozinho"
    evolution_api_key: str = "your_global_api_key"
    admin_phone: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
