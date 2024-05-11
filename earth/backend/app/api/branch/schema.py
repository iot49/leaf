from uuid import UUID

from sqlmodel import SQLModel

from ..base.schema import BaseRead
from ..tree.model import Id
from .model import BranchBase, MacAddr


class BranchCreate(BranchBase):
    pass


class BranchRead(BaseRead):
    # omit lmk
    branch_id: Id
    description: str
    mac: MacAddr
    tree_uuid: UUID


# all fields are optional
class BranchUpdate(SQLModel):
    # comment next line to prevent update of branch_id (requires configuration changes)
    branch_id: str | None = None
    description: str | None = None
    disabled: bool | None = None
