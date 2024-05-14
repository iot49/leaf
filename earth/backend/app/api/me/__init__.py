import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ...api import user
from ...db import get_session
from ...dependencies.get_current_user import get_current_user
from .crud import crud

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me")
async def read_me(
    user: user.model.User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> user.schema.UserRead:
    try:
        return await crud.get_me(uuid=user.uuid, db_session=session)
    except Exception as e:
        logger.error(f"junk in database {e}")
        raise HTTPException(status_code=404, detail=f"junk in database {e}")


@router.put("/me", response_model=user.schema.UserRead)
async def update(
    update: user.schema.UserUpdateNoRoles,
    session: AsyncSession = Depends(get_session),
    user: user.model.User = Depends(get_current_user),
) -> user.schema.UserRead:
    return await crud.update_me(uuid=user.uuid, obj_new=update, db_session=session)
