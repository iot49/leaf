from uuid import UUID

from sqlmodel import SQLModel

from ..base.schema import BaseRead
from ..branch import BranchRead
from .model import Id, TreeBase


class TreeCreate(TreeBase):
    pass


class TreeRead(BaseRead):
    # do not include credentials
    tree_id: Id
    title: str
    description: str
    gateway: UUID | None


class TreeReadWithBraches(TreeRead):
    branches: list[BranchRead]


# all fields are optional
class TreeUpdate(SQLModel):
    tree_id: str | None = None
    title: str | None = None
    description: str | None = None
    disabled: bool | None = None
