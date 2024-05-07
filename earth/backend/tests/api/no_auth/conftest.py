import pytest
from app.dependencies.verify_cloudflare_cookie import verify_cloudflare_cookie
from app.dependencies.verify_jwt import verify_client_token
from app.env import env
from fastapi import Request
from fastapi.requests import HTTPConnection
from httpx import AsyncClient
from tests.api.conftest import override_user
from tests.conftest import override_dependency


@pytest.fixture(autouse=True)
async def no_cf_auth():
    """Disable CF cookie verification."""

    async def verify_cloudflare_cookie_override(request: HTTPConnection):
        request.state.user_email = env.FIRST_SUPERUSER_EMAIL
        request.state.user = None  # get_superuser()

    async with override_dependency(verify_cloudflare_cookie_override, verify_cloudflare_cookie):
        yield


@pytest.fixture
async def no_client_auth(asyn_client):
    """Disable client_token verification"""

    async def verify_client_token_override(request: Request):
        request.state.user_email = env.FIRST_SUPERUSER_EMAIL

    async with override_dependency(verify_client_token_override, verify_client_token):
        yield


@pytest.fixture
async def create_api_key(async_client: AsyncClient) -> dict:
    async with override_user():
        response = await async_client.post("/api/api_key", json={})
        return response.json()
