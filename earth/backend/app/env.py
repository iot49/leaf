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

    DATABASE_URL: str | None = None
    DATABASE_ECHO: bool = False

    # directory which to serve the UI from
    UI_DIR: str | None = None

    # yaml config
    CONFIG_DIR: str | None = None

    CF_POLICY_AUD: str
    CF_TEAM_DOMAIN: str = "https://leaf49.cloudflareaccess.com"

    API_KEY_VALIDITY: timedelta = timedelta(days=100 * 365)

    # clients to gatway websocket
    CLIENT_TOKEN_VALIDITY: timedelta = timedelta(days=30)

    # gateway to earth websocket
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


@lru_cache()
def get_env():
    load_dotenv()
    env = Env()  # type: ignore

    # DATABASE_URL
    if env.DATABASE_URL is None:
        if env.ENVIRONMENT == Environment.production:
            env.DATABASE_URL = "sqlite+aiosqlite:///sqlite-prod.db"
        elif env.ENVIRONMENT == Environment.development:
            env.DATABASE_URL = "sqlite+aiosqlite:///sqlite-dev.db"
        else:
            env.DATABASE_URL = "sqlite+aiosqlite://"

    # CONFIG_DIR
    if env.CONFIG_DIR is None:
        env.CONFIG_DIR = "/home/config"
        if not os.path.isdir(env.CONFIG_DIR):
            env.CONFIG_DIR = "/Users/boser/Dropbox/Apps/leaf49 (1)"

    # UI_DIR
    if env.UI_DIR is None:
        env.UI_DIR = "/home/ui"
        if not os.path.isdir(env.UI_DIR):
            env.UI_DIR = "../../ui/dist"

    return env


env = get_env()
