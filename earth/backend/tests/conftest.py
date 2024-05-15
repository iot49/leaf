# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from app import db
from app.db import init_db
from app.main import app
from httpx import ASGITransport, AsyncClient
from httpx_ws.transport import ASGIWebSocketTransport


@pytest.fixture(scope="session", autouse=True)
async def initialize_db():
    await init_db()


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture()
async def async_client() -> AsyncGenerator:
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac


@pytest.fixture()
async def async_websocket_client() -> AsyncGenerator:
    transport = ASGIWebSocketTransport(app=app)
    async with AsyncClient(transport=transport, base_url="ws://localhost") as ac:
        yield ac


@pytest.fixture(autouse=True)
async def clear_db() -> AsyncGenerator:
    await db.db.clear()
    await db.db.populate()
    yield


@asynccontextmanager
async def override_dependency(override, dependency):
    cache = None
    try:
        cache = app.dependency_overrides[dependency]
    except KeyError:
        pass
    try:
        app.dependency_overrides[dependency] = override
        yield
    finally:
        if cache is not None:
            app.dependency_overrides[dependency] = cache
