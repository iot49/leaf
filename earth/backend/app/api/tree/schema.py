from sqlmodel import SQLModel

from ...types import Id
from ..base.schema import BaseRead
from ..branch.schema import BranchRead
from .model import TreeBase


class TreeCreate(TreeBase):
    pass


class TreeRead(BaseRead):
    # do not include credentials
    tree_id: Id
    title: str
    description: str
    # gateway: UUID | None


class TreeReadWithBraches(TreeRead):
    branches: list[BranchRead]


# all fields are optional
class TreeUpdate(SQLModel):
    tree_id: str | None = None
    title: str | None = None
    description: str | None = None
    disabled: bool | None = None
