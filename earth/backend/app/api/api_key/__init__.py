# ruff: noqa: F401

import logging
from uuid import UUID

from fastapi import HTTPException

from .crud import crud
from .endpoints import router
from .model import ApiKey, ApiKeyBase
from .schema import ApiKeyCreate, ApiKeyRead, ApiKeyUpdate

# TODO: implement api_key management


async def get_key(db_session, kid: str | None = None) -> ApiKeyRead:
    """
    Retrieve an API key from the database.

    Args:
        db_session: The database session.
        kid: The ID of the API key to retrieve (optional).

    Returns:
        Corresponding key if `kid` is provided, None otherwise.
        If `kid` not provided, returns the most recent key from the database.
    """
    api_keys = await crud.get_list(db_session=db_session)
    if api_keys == []:
        # create a first key
        obj_in = ApiKeyCreate()
        api_keys = [await crud.create(obj_in=obj_in, db_session=db_session)]
    if kid is None:
        # return the most recent key
        return api_keys[-1]  # type: ignore

    # find the key that matches the kid (str(key.uuid) == kid)
    for key in api_keys:
        if str(key.uuid) == kid:
            return key  # type: ignore
    raise HTTPException(status_code=404, detail="API key not found")
