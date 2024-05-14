from typing import Any
from uuid import UUID

from sqlmodel import SQLModel

from ...types import Id
from ..base.schema import BaseRead
from .model import TreeBase

# from ..branch import BranchRead


class TreeCreate(TreeBase):
    pass


class TreeRead(BaseRead):
    # do not include credentials
    tree_id: Id
    title: str
    description: str
    gateway: UUID | None


class TreeReadWithBraches(TreeRead):
    # branches: list[BranchRead]
    branches: list[Any]  # type: ignore # noqa: F821


# all fields are optional
class TreeUpdate(SQLModel):
    tree_id: str | None = None
    title: str | None = None
    description: str | None = None
    disabled: bool | None = None
