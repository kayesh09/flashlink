from functools import lru_cache
from pydantic import Field, PostgresDsn, RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # APP
    app_name: str = "FlashLink"
    environment: str = "local"
    debug: bool = False

    # DB
    postgres_dsn: PostgresDsn
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_max_timeout: int = 30

    # REDIS (Fixed capital D here)
    redis_dsn: RedisDsn

    # Auth
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 60

    # Cache
    redirect_cache_ttl_seconds: int = 3600
    negative_cache_ttl_seconds: int = 30

    # Rate limit
    rate_limit_redirect_per_minute: int = 60
    rate_limit_api_per_minute: int = 120

    short_code_length: int = 7

    @computed_field
    @property
    def async_db_url(self) -> str:
        return str(self.postgres_dsn).replace(
            "postgresql://", "postgresql+asyncpg://"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()