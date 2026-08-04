from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = (
        "postgresql+psycopg2://payment_copilot:payment_copilot@localhost:5433/payment_copilot"
    )
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"


settings = Settings()
