from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    API_PREFIX: str
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: str
    LOGGING_CONFIG_FILE: str
    PROJECT_VERSION: str

    class Config:
        env_file = "./.env"


settings = Settings()
