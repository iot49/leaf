from sqlmodel import SQLModel

from ..base.schema import BaseRead
from ..tree.schema import TreeRead
from .model import Name, Profile, Role, UserBase


class UserCreate(UserBase):
    pass


class TreeReadWithToken(TreeRead):
    client_token: str


class UserRead(BaseRead, UserBase):
    trees: list[TreeReadWithToken] = []


# all fields are optional
class UserUpdateNoRoles(SQLModel):
    name: Name | None = None
    profile: Profile | None = None


class UserUpdate(UserUpdateNoRoles):
    roles: list[Role] | None = None
    disabled: bool | None = None
