import logging
import os
from fnmatch import fnmatch

import yaml
from fastapi import Depends, HTTPException, WebSocket
from fastapi.requests import HTTPConnection

from ..api.user.schema import UserRead
from .get_current_user import get_current_user

logger = logging.getLogger(__name__)

auth_file = os.path.join(os.path.dirname(__file__), "authorizations.yml")

with open(auth_file, "r") as file:
    AUTH = yaml.safe_load(file)


async def verify_roles(request: HTTPConnection, user: UserRead = Depends(get_current_user)):
    if isinstance(request, WebSocket):
        return

    roles = user.roles.copy()
    if user.superuser:
        roles.append("superuser")
    path = request.url.path
    method = request.method  # type: ignore
    logger.debug(f"{user.email} {roles}, {path}, {method}")

    for pattern in AUTH:
        logger.debug(f"path {path} matches {pattern}? {fnmatch(path, f'/api{pattern}')}")
        if fnmatch(path, f"/api{pattern}"):
            auth = AUTH[pattern]
            if method in auth["methods"]:
                logger.debug(f"method {method} is in {auth['methods']}")
                if not set(roles).isdisjoint(auth["roles"]):
                    logger.debug(f"roles {roles} is not disjoint with {auth['roles']}")
                    logger.debug(f"path {path} is authorized")
                    return

    logger.debug(f"{user.email} with roles {roles} is not authorized for {method} {path}")
    raise HTTPException(
        status_code=403, detail=f"{user.email} with roles {roles} is not authorized for {method} {path}"
    )
