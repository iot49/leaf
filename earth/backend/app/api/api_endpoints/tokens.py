import logging

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ...api import api_key, tree
from ...bus.secrets import get_secrets
from ...db import get_session
from ...dependencies.get_current_user import get_current_user
from ...tokens import new_client_token, new_gateway_token
from ..user.model import User
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@router.get("/client_token")
async def get_client_token(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> str:
    # used only for login to websocket connections to earth
    # short validity requires getting a new token for each connection
    key: api_key.ApiKeyRead = await api_key.get_key(db_session=session)
    return await new_client_token(user_uuid=user.uuid, api_key=key)


@router.get("/gateway_token/{tree_uuid}")
async def get_gateway_token(
    tree_uuid: str,
    session: AsyncSession = Depends(get_session),
) -> str:
    # used for branch on-barding
    _tree: tree.schema.TreeRead = await tree.crud.get_by_uuid(uuid=tree_uuid, db_session=session)
    key: api_key.ApiKeyRead = await api_key.get_key(db_session=session)
    return await new_gateway_token(tree=_tree, api_key=key)


@router.get("/gateway_secrets/{tree_uuid}")
async def get_gateway_secrets(tree_uuid: str) -> dict:
    return await get_secrets(tree_uuid=tree_uuid) or {}
