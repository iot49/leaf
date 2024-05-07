from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ...db import get_session
from ..base import create_endpoints
from .crud import crud
from .schema import TreeCreate, TreeRead, TreeReadWithBraches, TreeUpdate

router = APIRouter()


# "predefine" here so that /count appears before /{id} in path matching
@router.get("/count", response_model=int)
async def count_branches(session: AsyncSession = Depends(get_session)):
    return await crud.count(db_session=session)


# redefine with different response_model to include branches
@router.get("/{uuid}", response_model=TreeReadWithBraches)
async def get_by_uuid(uuid: UUID, session: AsyncSession = Depends(get_session)):
    res = await crud.get_by_uuid(uuid=uuid, db_session=session)
    return res


# add the default endpoints
router = create_endpoints(crud, TreeCreate, TreeRead, TreeUpdate, router=router)
