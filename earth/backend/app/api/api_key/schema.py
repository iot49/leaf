from datetime import datetime

from sqlmodel import SQLModel

from ..base.schema import BaseRead
from .model import ApiKeyBase


class ApiKeyCreate(ApiKeyBase):
    pass


class ApiKeyRead(ApiKeyBase, BaseRead):
    pass


# all fields are optional
class ApiKeyUpdate(SQLModel):
    expires_at: datetime | None = None
    disabled: bool | None = None
