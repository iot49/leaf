from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ...api import api_key
from ...db import get_session
from ...dependencies.get_current_user import get_current_user
from ...tokens import new_client_token
from ..user.model import User
from ..user.schema import UserRead, UserUpdateNoRoles
from .crud import crud

router = APIRouter()


@router.get("/me")
async def read_me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    try:
        return await crud.get_me(uuid=user.uuid, db_session=session)
    except Exception as e:
        print(f"\n\n---------------------- junk in database {e}")
        raise HTTPException(status_code=404, detail=f"junk in database {e}")


@router.put("/me", response_model=UserRead)
async def update(
    update: UserUpdateNoRoles,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> UserRead:
    return await crud.update_me(uuid=user.uuid, obj_new=update, db_session=session)


@router.get("/client_token")
async def get_client_token(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> str:
    # used only for login to websocket connections to earth
    # short validity requires getting a new token for each connection
    key: api_key.ApiKeyRead | None = await api_key.get_key(db_session=session)
    if key is None:
        raise HTTPException(status_code=404, detail="API key not found")
    return await new_client_token(user_uuid=user.uuid, api_key=key, validity=timedelta(minutes=1))
