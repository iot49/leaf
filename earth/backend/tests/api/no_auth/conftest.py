import pytest
from app.dependencies.verify_cloudflare_cookie import verify_cloudflare_cookie
from app.env import env
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
async def create_api_key(async_client: AsyncClient) -> dict:
    async with override_user():
        print("create_api_key")
        response = await async_client.post("/api/api_key", json={})
        print("create_api_key response", response)
        return response.json()
