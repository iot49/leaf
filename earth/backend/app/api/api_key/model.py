import secrets
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.env import env

from ..base import BaseUUIDModel


class ApiKeyBase(SQLModel):
    key: str = Field(default_factory=lambda: secrets.token_urlsafe(128))
    expires_at: datetime = Field(default_factory=lambda: datetime.now() + env.API_KEY_VALIDITY)


class ApiKey(BaseUUIDModel, ApiKeyBase, table=True):
    # Note: id defined in BaseUUIDModel
    pass
