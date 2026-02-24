from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DB_NAME: str = "goreos_model"
    DB_USER: str = "goreos"
    DB_PASSWORD: str = "goreos_2026"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5433

    JWT_SECRET: str = "goreos-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {"env_file": "../.env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
