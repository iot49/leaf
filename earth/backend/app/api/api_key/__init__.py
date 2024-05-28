# ruff: noqa: F401

import logging
from uuid import UUID

from fastapi import HTTPException

from .crud import crud
from .endpoints import router
from .model import ApiKey, ApiKeyBase
from .schema import ApiKeyCreate, ApiKeyRead, ApiKeyUpdate

# TODO: implement api_key management

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
    logger.debug(f"api_key: get_key, kid = {kid}")
    api_keys = await crud.get_list(db_session=db_session)
    logger.debug(f"api_key: get_key, keys = {api_keys}")
    if api_keys == []:
        # create a first key
        logger.debug("create first key")
        obj_in = ApiKeyCreate()
        api_keys = [await crud.create(obj_in=obj_in, db_session=db_session)]
        logger.debug(f"api_key: get_key, first key = {api_keys}")
    if kid is None:
        # return the most recent key
        logger.debug(f"api_key: return most recent key: {api_keys[-1]}")
        return api_keys[-1]  # type: ignore

    # find the key that matches the kid (str(key.uuid) == kid)
    for key in api_keys:
        if str(key.uuid) == kid:
            return key  # type: ignore
    logger.debug(f"api_key: key not found for kid = {kid}")
    raise HTTPException(status_code=404, detail="API key not found")
