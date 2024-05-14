import re
from typing import Annotated

from pydantic import AfterValidator


def alphanumunderscore(value: str):
    assert re.match(r"^[a-z0-9_]+$", value) is not None, "Only lowercase alphanumeric characters and underscore allowed"
    return value


Id = Annotated[str, AfterValidator(alphanumunderscore)]


VALID_ROLES = [
    "admin",  # create and edit trees, branch onboarding
    "user",  # view trees and branches, connect to websockets (earth and local)
    "guest",  # same as user, except no websocket access
]


def validate_roles(role: str) -> str:
    role = role.lower()
    assert role in VALID_ROLES, f"Invalid role: {role}"
    return role


Role = Annotated[str, AfterValidator(validate_roles)]


def mac_addr(value: str):
    value = value.lower()
    regex = "^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})|([0-9a-f]{4}\\.[0-9a-f]{4}\\.[0-9a-f]{4})$"
    assert re.match(regex, value) is not None, "Not a valid MAC address"
    return value


MacAddr = Annotated[str, AfterValidator(mac_addr)]
MarkDown = str
