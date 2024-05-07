from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_session


def create_endpoints(crud, CreateSchema, ReadSchema, UpdateSchema, *, router: APIRouter | None = None):
    if router is None:
        router = APIRouter()

    def model2read(model):
        return ReadSchema(**model.model_dump())

    @router.get("", response_model=list[ReadSchema])
    async def get_all(
        offset: int = 0,
        limit: int = Query(default=50, le=100),
        session: AsyncSession = Depends(get_session),
    ):
        return await crud.get_list(db_session=session, skip=offset, limit=limit)

    # declare ahead of get("/{uuid}") !
    @router.get("/count", response_model=int)
    async def count(session: AsyncSession = Depends(get_session)):
        return await crud.count(db_session=session)

    @router.get("/{uuid}", response_model=ReadSchema)
    async def get_by_uuid(
        uuid: UUID,
        session: AsyncSession = Depends(get_session),
    ):
        return await crud.get_by_uuid(id=uuid, db_session=session)

    @router.post("", status_code=status.HTTP_201_CREATED, response_model=ReadSchema)
    async def create(
        obj_in: CreateSchema,
        session: AsyncSession = Depends(get_session),
    ) -> ReadSchema:
        return model2read(await crud.create(obj_in=obj_in, db_session=session))

    @router.put("/{uuid}", response_model=ReadSchema)
    async def update(
        uuid: UUID,
        update: UpdateSchema,
        session: AsyncSession = Depends(get_session),
    ) -> ReadSchema:
        return model2read(await crud.update(uuid=uuid, obj_new=update, db_session=session))

    @router.delete("/{uuid}", response_model=ReadSchema)
    async def delete(
        uuid: UUID,
        session: AsyncSession = Depends(get_session),
    ) -> ReadSchema:
        obj = await crud.remove(uuid=uuid, db_session=session)
        return model2read(obj)

    return router
