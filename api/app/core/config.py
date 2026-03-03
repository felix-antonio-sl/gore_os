from pydantic import model_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

_INSECURE_JWT_SECRET = "goreos-dev-secret-change-in-production"


class Settings(BaseSettings):
    DB_NAME: str = "goreos_model"
    DB_USER: str = "goreos"
    DB_PASSWORD: str = "goreos_2026"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5433

    ENV: str = "development"
    JWT_SECRET: str = _INSECURE_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @model_validator(mode="after")
    def _check_jwt_secret(self):
        if self.JWT_SECRET == _INSECURE_JWT_SECRET and self.ENV != "development":
            raise ValueError(
                "JWT_SECRET must be changed from the default value in non-development environments. "
                "Set a strong secret via the JWT_SECRET environment variable."
            )
        return self

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {"env_file": "../.env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
