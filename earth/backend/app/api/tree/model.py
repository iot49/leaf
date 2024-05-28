import secrets
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from ...types import Id
from ...utils.uuid6 import uuid7
from ..base import BaseUUIDModel

if TYPE_CHECKING:
    from ..branch import Branch


class TreeCredentials(SQLModel):
    kid: UUID = Field(default_factory=uuid7)
    # tree_key handing out client tokens for /app/ui on trees
    # Note: on the cloud, /app/ui is behind a cf cookie
    tree_key: str = Field(default_factory=lambda: secrets.token_urlsafe(128))
    espnow_pmk: str = Field(default_factory=lambda: secrets.token_hex(16))


class TreeBase(TreeCredentials, SQLModel):
    tree_id: Id = Field(unique=True, index=True, regex=r"^[a-z0-9_]+$")
    title: str
    description: str = ""
    # gateway: UUID | None = None  # default gatway for this tree

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tree_id": "tree_1",
                    "title": "One-line description of tree",
                    "description": "Description (markdown supported)",
                    "gateway": None,
                }
            ]
        }
    }  # type: ignore


class Tree(BaseUUIDModel, TreeBase, table=True):
    # Note: id defined in BaseUUIDModel
    branches: list["Branch"] = Relationship(back_populates="tree")
