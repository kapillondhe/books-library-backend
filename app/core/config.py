
from pydantic import field_validator
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):

    app_name: str = "Books Library API"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/library_db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("database_url")
    @classmethod
    def force_asyncpg_driver(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+asyncpg://", 1)
        return value


settings = AppSettings()
