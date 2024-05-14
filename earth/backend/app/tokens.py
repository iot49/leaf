from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from . import api
from .db import SessionLocal
from .env import env


async def new_client_token(*, user_uuid, tree=None, api_key=None, validity: timedelta = env.CLIENT_TOKEN_VALIDITY):
    payload = {
        "nbf": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + validity,
        "aud": "client->earth",
        "user_uuid": str(user_uuid),
    }
    if tree is None:
        key = api_key
        headers = {"kid": str(key.uuid)}  # type: ignore
    else:
        payload["tree_uuid"] = str(tree.uuid)
        key = tree.tree_key
        headers = {"kid": str(tree.kid)}

    return jwt.encode(payload, str(key), algorithm="HS256", headers=headers)


async def verify_client_token_(token):  # -> api.user.schema.UserRead:
    """Verifies the client token checking its validity and expiration.

    Args:
        token: The client token to be verified.

    Returns:
        The user associated with the token.

    Raises:
        HTTPException: If the token is invalid, expired, or the user is not known or suspended.
    """
    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    async with SessionLocal() as session:
        key = await api.api_key.get_key(db_session=session, kid=header.get("kid"))
        if key is None:
            raise HTTPException(status_code=401, detail="Invalid token (kid)")

        try:
            # verify that the token is valid and not expired (raises DecodeError if invalid)
            payload = jwt.decode(token, key=str(key), algorithms=["HS256"], audience="client->earth")
            user_ = await api.user.crud.get_by_uuid(db_session=session, uuid=payload.get("user_uuid"))  # type: ignore
            if user_ is None:
                raise HTTPException(status_code=401, detail="User not known")
            if user_.disabled:
                raise HTTPException(status_code=403, detail="User suspended")

            return user_

        except jwt.DecodeError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def new_gateway_token(tree_uuid, api_key, validity: timedelta = env.GATEWAY_TOKEN_VALIDITY):
    payload = {
        "nbf": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + validity,
        "aud": "gateway->earth",
        "tree_uuid": str(tree_uuid),
    }
    return jwt.encode(payload, api_key.key, algorithm="HS256", headers={"kid": str(api_key.uuid)})


async def verify_gateway_token_(token):  # -> api.tree.schema.TreeReadWithBraches:
    """
    Verify the authenticity and validity of a gateway token.

    Args:
        token: The token to be verified.

    Returns:
        The tree associated with the token.

    Raises:
        HTTPException: If the token is invalid, expired, or the associated tree is not found or disabled.
    """
    try:
        header = jwt.get_unverified_header(token)
    except jwt.DecodeError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    async with SessionLocal() as session:
        key: api.api_key.ApiKeyRead | None = await api.api_key.get_key(db_session=session, kid=header.get("kid"))
        if key is None:
            raise HTTPException(status_code=401, detail="Invalid token (kid)")

        try:
            # verify that the token is valid and not expired
            payload = jwt.decode(token, key=key.key, algorithms=["HS256"], audience="gateway->earth")
            # verify that the tree exists
            tree_ = await api.tree.crud.get_by_uuid(uuid=payload.get("tree_uuid"), db_session=session)  # type: ignore
            if tree_ is None:
                raise HTTPException(status_code=401, detail="Tree not found")
            if tree_.disabled:
                raise HTTPException(status_code=403, detail="Tree disabled")
            return tree_
        except jwt.DecodeError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")
