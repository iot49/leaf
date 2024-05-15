from pydantic import EmailStr
from pydantic.functional_validators import AfterValidator
from sqlmodel import JSON, AutoString, Column, Field, SQLModel
from typing_extensions import Annotated

from ...types import Role
from ..base import BaseUUIDModel


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
                    "profile": "44th President",
                    "superuser": False,
                }
            ]
        }
    }  # type: ignore


class User(BaseUUIDModel, UserBase, table=True):
    # Note: id defined in BaseUUIDModel
    pass
