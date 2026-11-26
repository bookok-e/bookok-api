from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data4library_key: str | None = None
    yes24_key: str | None = None
    ai_api_key: str | None = None
    embedding_model: str | None = None
    llm_model: str | None = None
    database_url: str | None = None


settings = Settings()
