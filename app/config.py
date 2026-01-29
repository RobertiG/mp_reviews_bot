from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "mp_reviews_bot"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/mp_reviews"
    redis_url: str = "redis://redis:6379/0"
    telegram_bot_token: str = ""
    telegram_channel_id: str = ""
    telegram_channel_url: str = ""
    tg_channel_url: str = ""
    api_base_url: str = "http://localhost:8000"
    encryption_key: str = ""
    free_tokens_per_month: int = 100
    log_retention_days: int = 90

    class Config:
        env_file = ".env"


settings = Settings()
