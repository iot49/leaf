from typing import Generic, TypeVar
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import exc, func
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T")
ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, ReadSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        :param model: a SQLModel class
        """
        self.model = model

    async def get_by_uuid(
        self,
        *,
        uuid: UUID | str,
        db_session: AsyncSession,
    ) -> ReadSchemaType:
        res = await db_session.get(self.model, uuid)
        if res is None:
            raise HTTPException(status_code=404, detail="Object not found")
        # TODO: convert to ReadSchemaType - how?
        return res  # type: ignore

    async def get_list(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "uuid",
        db_session: AsyncSession,
    ) -> list[ModelType]:
        query = select(self.model).offset(skip).limit(limit).order_by(order_by)
        response = await db_session.execute(query)
        return response.scalars().all()  # type: ignore

    async def create(
        self,
        *,
        obj_in: CreateSchemaType | ModelType,
        db_session: AsyncSession,
    ) -> ReadSchemaType:
        db_obj = self.model(**obj_in.model_dump())
        try:
            db_session.add(db_obj)
            await db_session.commit()
        except exc.IntegrityError as e:
            raise HTTPException(
                status_code=409,
                detail=f"Object already exists {e}",
            )
        await db_session.refresh(db_obj)
        return db_obj  # type: ignore

    async def update(
        self,
        *,
        uuid: UUID,
        obj_new: UpdateSchemaType,
        db_session: AsyncSession,
    ) -> ReadSchemaType:
        obj = await db_session.get(self.model, uuid)
        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")
        obj.sqlmodel_update(obj_new.model_dump(exclude_unset=True))
        db_session.add(obj)
        await db_session.commit()
        await db_session.refresh(obj)
        return obj  # type: ignore

    async def remove(self, *, uuid: UUID | str, db_session: AsyncSession) -> ReadSchemaType:
        obj = await db_session.get(self.model, uuid)
        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")
        await db_session.delete(obj)
        await db_session.commit()
        return obj  # type: ignore

    async def count(self, *, db_session: AsyncSession) -> int:
        res = await db_session.execute(select(func.count(self.model.uuid)))
        return res.one()[0]
