from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.utils.uuid6 import uuid7


def utcnow():
    return datetime.now(timezone.utc)


class BaseUUIDModel(SQLModel):
    uuid: UUID = Field(
        default_factory=lambda: uuid7(),
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime | None = Field(default_factory=utcnow, sa_column_kwargs={"onupdate": utcnow})
    created_at: datetime | None = Field(default_factory=utcnow)
    disabled: bool = False
