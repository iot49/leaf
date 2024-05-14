from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.utils.uuid6 import uuid7


class BaseRead(SQLModel):
    uuid: UUID = Field(
        default_factory=lambda: uuid7(),
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime
    created_at: datetime
    disabled: bool
