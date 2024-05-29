import logging
from uuid import UUID

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ... import db
from ...bus.secrets import get_secrets_uuid
from ...dependencies.get_current_user import get_current_user
from ...tokens import new_client2earth, new_gateway2earth
from .. import tree
from ..api_key import get_key
from ..user.model import User
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@router.get("/client_token")
async def get_client_token(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(db.get_session)
) -> str:
    # Note: no verification if user exists (checked anyways on token verification)
    api_key = await get_key(db_session=session)
    return await new_client2earth(user_uuid=user.uuid, api_key=api_key)


@router.get("/gateway_token/{tree_uuid}")
async def get_gateway_token(tree_uuid: UUID, session: AsyncSession = Depends(db.get_session)) -> str:
    # used for branch on-barding
    api_key = await get_key(db_session=session)
    _tree = await tree.crud.get_by_uuid(uuid=tree_uuid, db_session=session)
    return await new_gateway2earth(tree=_tree, api_key=api_key)


@router.get("/gateway_secrets/{tree_uuid}")
async def get_gateway_secrets(tree_uuid: str) -> dict:
    return await get_secrets_uuid(tree_uuid=tree_uuid) or {}
