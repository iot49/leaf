import os
from datetime import timedelta
from enum import Enum
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, EmailStr, ValidationInfo, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    production = "prod"
    development = "dev"
    test = "test"


class Env(BaseSettings):
    """Loads the dotenv file. Including this is necessary to get
    pydantic to load a .env file."""

    ENVIRONMENT: Environment = Environment.production

    PROJECT_NAME: str = "leaf"
    DOMAIN: str = "leaf49.org"

    FIRST_SUPERUSER_EMAIL: EmailStr

    # database
    POSTGRES_USERNAME: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    DATABASE_ECHO: bool = False

    LOCAL_CONFIG_DIR: str = ""

    # cloudflare tunnel
    CF_POLICY_AUD: str
    CF_TEAM_DOMAIN: str = "https://leaf49.cloudflareaccess.com"

    # api keys
    API_KEY_VALIDITY: timedelta = timedelta(days=100 * 365)
    CLIENT_TOKEN_VALIDITY: timedelta = timedelta(days=30)
    GATEWAY_TOKEN_VALIDITY: timedelta = timedelta(days=90)

    # analytics
    ANALYTICS_API_KEY: str | None = None

    # CORS
    BACKEND_CORS_ORIGINS: list[str] | list[AnyHttpUrl] = ["http://localhost:5173", "http://localhost:4173"]  # ["*"]

    @field_validator("BACKEND_CORS_ORIGINS")
    def assemble_cors_origins(cls, v: str | list[str], info: ValidationInfo) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v

    model_config = SettingsConfigDict(
        # env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        if self.ENVIRONMENT == Environment.production:
            return f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@database:5432/{self.PROJECT_NAME}_{self.ENVIRONMENT.value}"
            # return f"sqlite+aiosqlite:///sqlite-{self.PROJECT_NAME}-{self.ENVIRONMENT.value}.db"
        if self.ENVIRONMENT == Environment.development:
            return f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@192.168.8.191:5432/{self.PROJECT_NAME}_{self.ENVIRONMENT.value}"
            # return f"sqlite+aiosqlite:///sqlite-{self.PROJECT_NAME}-{self.ENVIRONMENT.value}.db"
        # in memory database raises sqlalchemy.exc.InvalidRequestError: Could not refresh instance (on session.refresh(obj))
        return "sqlite+aiosqlite:///sqlite-test.db"

    @property
    def CONFIG_DIR(self) -> str:
        dir = "/home/config"
        return dir if os.path.isdir(dir) else env.LOCAL_CONFIG_DIR

    @property
    def UI_DIR(self) -> str:
        dir = "/home/ui"
        if not os.path.isdir(dir):
            dir = "../../ui/dist"
        return dir


@lru_cache()
def get_env():
    load_dotenv()
    return Env()  # type: ignore


env = get_env()
