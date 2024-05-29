import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import jwt
from fastapi import HTTPException

from . import api
from .db import get_session
from .env import Environment, env

if TYPE_CHECKING:
    from .api.tree.schema import TreeReadWithBraches
    from .api.user.schema import UserRead

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def new_client_token(*, user_uuid, tree=None, api_key=None, validity: timedelta = env.CLIENT_TOKEN_VALIDITY):
    payload = {
        "exp": datetime.now(timezone.utc) + validity,
        "aud": "client->earth",
        "user_uuid": str(user_uuid),
    }
    if tree is None:
        # earth ingress
        key = api_key
        headers = {"kid": str(key.uuid)}  # type: ignore
    else:
        # tree ingress
        payload["tree_uuid"] = str(tree.uuid)
        payload["tree_id"] = tree.tree_id
        key = tree.tree_key
        headers = {"kid": str(tree.kid)}
    token = jwt.encode(payload, str(key), headers=headers, algorithm="HS256")
    logger.debug(f"token: {token}")
    logger.debug(f"key:   {key}")
    return token


async def verify_client_token(token) -> "UserRead":  # type: ignore
    """Verifies the client token checking its validity and expiration.

    Args:
        token: The client token to be verified.

    Returns:
        The user associated with the token.

    Raises:
        HTTPException: If the token is invalid, expired, or the user is not known or suspended.
    """

    if token is None:
        logger.debug("no token provided (None)")
        raise HTTPException(status_code=401, detail="No token provided")

    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Corrupt token: {e}")

    async for session in get_session():
        key = await api.api_key.get_key(db_session=session, kid=header.get("kid"))
        logger.debug(f"token: {token}")
        logger.debug(f"key:   {key}")

        try:
            # verify that the token is valid and not expired (raises DecodeError if invalid)
            payload = jwt.decode(token, key=str(key), audience="client->earth", algorithms=["HS256"])
            user = await api.user.crud.get_by_uuid(db_session=session, uuid=payload.get("user_uuid"))
            if user.disabled:
                raise HTTPException(status_code=403, detail="User suspended")

            return user

        except jwt.DecodeError as e:
            logger.error(f"Invalid token: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def new_gateway_token(tree, api_key, validity: timedelta = env.GATEWAY_TOKEN_VALIDITY):
    payload = {
        "exp": datetime.now(timezone.utc) + validity,
        "aud": "gateway->earth",
        "tree_uuid": str(tree.uuid),
        "tree_id": tree.tree_id,
    }
    token = jwt.encode(payload, api_key.key, headers={"kid": str(api_key.uuid)}, algorithm="HS256")
    logger.debug(f"token: {token}")
    logger.debug(f"key:   {api_key.key}")
    return token


async def verify_gateway_token(token) -> "TreeReadWithBraches":  # type: ignore
    """
    Verify the authenticity and validity of a gateway token.

    Args:
        token: The token to be verified.

    Returns:
        The tree associated with the token.

    Raises:
        HTTPException: If the token is invalid, expired, or the associated tree is not found or disabled.
    """
    # during development, we don't verify the token to accept tokens generated by the production server
    # in any case, we return the tree
    verify = env.ENVIRONMENT != Environment.development

    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Corrupt token: {e}")

    async for session in get_session():
        key = (await api.api_key.get_key(db_session=session, kid=header.get("kid"))).key if verify else ""
        logger.debug(f"token: {token}")
        logger.debug(f"key:   {key}")
        try:
            # verify that the token is valid and not expired
            payload = jwt.decode(
                token,
                key=key,
                audience="gateway->earth",
                options={"verify_signature": verify},
                algorithms=["HS256"],
            )
            # verify that the tree exists
            tree_ = (
                await api.tree.crud.get_by_uuid(uuid=payload.get("tree_uuid"), db_session=session)
                if verify
                else await api.tree.crud.get_by_tree_id(tree_id=payload.get("tree_id"), db_session=session)
            )
            if tree_.disabled:
                raise HTTPException(status_code=403, detail="Tree disabled")
            return tree_
        except jwt.DecodeError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
