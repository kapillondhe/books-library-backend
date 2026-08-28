
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):

    app_name: str = "Books Library API"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/library_db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = AppSettings()
