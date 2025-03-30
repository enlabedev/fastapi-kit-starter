from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLITE_URL: str = ""
    API_PREFIX: str = ""
    PROJECT_NAME: str = ""
    BACKEND_CORS_ORIGINS: str = ""
    LOGGING_CONFIG_FILE: str = ""
    PROJECT_VERSION: str = ""

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        env_file="./.env",
        arbitrary_types_allowed=True,
    )


settings = Settings()
