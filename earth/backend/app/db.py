import logging
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.util import greenlet_spawn
from sqlalchemy_utils import create_database
from sqlmodel import SQLModel

from .env import env

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DBEngine:
    def __init__(self, url: str):
        self.url = url
        self.engine: AsyncEngine
        self.session_local: async_sessionmaker

    async def configure(self, echo: bool = False):
        url = self.url
        logger.debug("configuring database {url}")
        self.engine = create_async_engine(
            url,
            echo=echo,
            future=True,
            connect_args={"check_same_thread": False} if "sqlite" in url else {},
        )

        # create tables; this will fail if the database does not exist
        try:
            logger.debug("creating tables ...")
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
        except Exception:
            # create database
            logger.debug("database does not exist")

            def _create_db():
                logger.debug("creating database")
                create_database(url)

            logger.debug("greenlet spawning _create_db")
            await greenlet_spawn(_create_db)

            # try again creating tables
            async with self.engine.begin() as conn:
                logger.debug("creating tables, 2nd attempt ...")
                await conn.run_sync(SQLModel.metadata.create_all)

        self.session_local = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

        await self.populate()

    async def populate(self):
        # create default database entries
        try:
            from .api import user

            logger.debug("create first superuser ...")
            async with self.session_local() as session:
                # create first superuser
                obj_in = user.schema.UserCreate(
                    name="first superuser",
                    email=env.FIRST_SUPERUSER_EMAIL,
                    superuser=True,
                    roles=["admin"],
                )
                await user.crud.create(obj_in=obj_in, db_session=session)

        except HTTPException as e:
            logger.debug(f"first superuser already exists {e}")

    async def clear(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)


db: DBEngine


async def init_db(url=env.DATABASE_URL, echo=env.DATABASE_ECHO):
    global db
    logger.debug(f"initializing database {url}, echo={echo}")
    db = DBEngine(url)
    await db.configure(echo=echo)


async def get_session() -> AsyncGenerator:
    global db
    async with db.session_local() as session:
        yield session


def get_engine() -> AsyncEngine:
    global db
    return db.engine
