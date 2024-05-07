import re
import secrets
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from pydantic import AfterValidator
from sqlmodel import Field, Relationship, SQLModel

from app.utils.uuid6 import uuid7

from ..base import BaseUUIDModel

if TYPE_CHECKING:
    from ..branch import Branch


def alphanumunderscore(value: str):
    assert re.match(r"^[a-z0-9_]+$", value) is not None, "Only lowercase alphanumeric characters and underscore allowed"
    return value


Id = Annotated[str, AfterValidator(alphanumunderscore)]


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
    gateway: UUID | None = None  # default gatway for this tree

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
