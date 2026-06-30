from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://localhost/credit_risk"
    groq_api_key: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
