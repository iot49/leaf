from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.utils.uuid6 import uuid7


def utcnow():
    # TODO: use utc time for postgresql
    # insertion in postgresql fails with
    #       can't subtract offset-naive and offset-aware datetimes
    # return datetime.now(timezone.utc).replace(tzinfo=None)
    return datetime.utcnow()


class BaseUUIDModel(SQLModel):
    uuid: UUID = Field(
        default_factory=lambda: uuid7(),
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={"onupdate": utcnow})
    created_at: datetime = Field(default_factory=utcnow)
    disabled: bool = False
