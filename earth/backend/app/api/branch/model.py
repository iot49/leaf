import re
import secrets
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from pydantic import AfterValidator
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from ..base import BaseUUIDModel
from ..tree.model import Id

if TYPE_CHECKING:
    from ..tree import Tree

# all users can modify their own profile


def mac_addr(value: str):
    value = value.lower()
    regex = "^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})|([0-9a-f]{4}\\.[0-9a-f]{4}\\.[0-9a-f]{4})$"
    assert re.match(regex, value) is not None, "Not a valid MAC address"
    return value


MacAddr = Annotated[str, AfterValidator(mac_addr)]
MarkDown = str


class BranchBase(SQLModel):
    branch_id: Id = Field(index=True, regex=r"^[a-z0-9_]+$")
    mac: MacAddr
    description: MarkDown = ""
    espnow_lmk: str = Field(default_factory=lambda: secrets.token_hex(16))
    tree_uuid: UUID = Field(foreign_key="tree.uuid")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "branch_id": "branch_1",
                    "mac": "12:34:56:78:9a:bc",
                    "description": "Branch 1 description (markdown supported)",
                    "tree_uuid": "00000000-0000-0000-0000-000000000000",
                }
            ]
        }
    }  # type: ignore


class Branch(BaseUUIDModel, BranchBase, table=True):
    __table_args__ = (
        UniqueConstraint("branch_id", "tree_uuid", name="uq_branch_id_tree"),
        UniqueConstraint("mac", "tree_uuid", name="uq_mac_tree"),
    )
    tree: "Tree" = Relationship(back_populates="branches")
