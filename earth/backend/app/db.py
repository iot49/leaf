from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

from .env import env

engine: AsyncEngine = create_async_engine(
    env.DATABASE_URL,  # type: ignore
    echo=env.DATABASE_ECHO,
    future=True,
    connect_args={"check_same_thread": False},  # for sqlite
    poolclass=StaticPool,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session


async def init_db():
    global _superuser
    # create tables (if not already created by alembic)
    async with engine.begin() as conn:  # type: ignore
        # Note: interferes with Alembic migrations (use alembic stamp head before migration)
        await conn.run_sync(SQLModel.metadata.create_all)

    # create defaults
    try:
        from .api import user

        async with SessionLocal() as session:
            # create first superuser
            obj_in = user.schema.UserCreate(
                name="first superuser",
                email=env.FIRST_SUPERUSER_EMAIL,
                superuser=True,
                roles=["admin"],
            )
            _superuser = await user.crud.create(obj_in=obj_in, db_session=session)  # type: ignore

    except HTTPException:
        pass


_superuser = None  # set in init_db (and used for testing)


def get_superuser():
    return _superuser
