from sqlmodel import SQLModel

from ...types import Id
from ..base.schema import BaseRead
from .model import TreeBase


class TreeCreate(TreeBase):
    pass


class TreeRead(BaseRead):
    # no branches
    tree_id: Id
    title: str
    description: str
    tree_key: str


# all fields are optional
class TreeUpdate(SQLModel):
    tree_id: str | None = None
    title: str | None = None
    description: str | None = None
    disabled: bool | None = None
