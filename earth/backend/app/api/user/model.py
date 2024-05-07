from pydantic import EmailStr
from pydantic.functional_validators import AfterValidator
from sqlmodel import JSON, AutoString, Column, Field, SQLModel
from typing_extensions import Annotated

from ..base import BaseUUIDModel

VALID_ROLES = [
    "admin",  # create and edit trees, branch onboarding
    "user",  # view trees and branches, connect to websockets (earth and local)
    "guest",  # same as user, except no websocket access
]

# all users can modify their own profile


def validate_roles(role: str) -> str:
    role = role.lower()
    assert role in VALID_ROLES, f"Invalid role: {role}"
    return role


Role = Annotated[str, AfterValidator(validate_roles)]


def validate_length(value: str, max_length) -> str:
    assert len(value) <= max_length, f"Length of '{value}' is {len(value)}, must be <= {max_length}"
    return value


Name = Annotated[str, AfterValidator(lambda value: validate_length(value, 100))]
Profile = Annotated[str, AfterValidator(lambda value: validate_length(value, 5000))]


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, nullable=False, index=True, sa_type=AutoString)
    superuser: bool = False
    roles: list[Role] = Field(default=[], sa_column=Column(JSON))
    name: Name = ""
    profile: Profile = ""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "obama@whitehouse.gov",
                    "roles": ["user"],
                    "name": "Barack Obama",
                    "profile": "Barack Obama, 44th President of the United States (**markdown** supported in profile)",
                }
            ]
        }
    }  # type: ignore


class User(BaseUUIDModel, UserBase, table=True):
    # Note: id defined in BaseUUIDModel
    pass
