
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):

    app_name: str = "Books Library API"
    database_url: str = "sqlite+aiosqlite:///./library.db"
    static_dir: str = "app/static"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = AppSettings()
