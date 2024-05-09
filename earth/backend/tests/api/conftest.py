from contextlib import asynccontextmanager

import pytest
from app.dependencies.verify_cloudflare_cookie import verify_cloudflare_cookie
from app.env import env
from fastapi.requests import HTTPConnection
from httpx import AsyncClient
from tests.conftest import override_dependency


@asynccontextmanager
async def override_user(email: str = env.FIRST_SUPERUSER_EMAIL):
    """Override the user email (for role verification)."""

    async def verify_cloudflare_token_override(request: HTTPConnection):
        request.state.user_email = email
        request.state.user = None  # get_superuser()

    async with override_dependency(verify_cloudflare_token_override, verify_cloudflare_cookie):
        yield


@pytest.fixture
async def create_users(async_client: AsyncClient, client_token):
    users = [
        {"name": "superuser", "email": "superuser@x.y", "roles": ["admin"], "superuser": True},
        {"name": "superuser_only", "email": "superuser_only@x.y", "roles": [], "superuser": True},
        {"name": "admin", "email": "admin@x.y", "roles": ["admin"]},
        {"name": "user", "email": "user@x.y", "roles": ["user"]},
        {"name": "guest", "email": "guest@x.y", "roles": ["guest"]},
        {"name": "no_roles", "email": "no_roles@x.y", "roles": []},
    ]
    res = {}
    for user in users:
        response = await async_client.post("/api/user", json=user)
        assert response.status_code == 201
        u = response.json()
        res[user["email"]] = u
    return res


@pytest.fixture
async def create_trees(async_client: AsyncClient, client_token, tree_count: int = 2, branch_count: int = 3) -> list:
    """
    Creates `tree_count` trees with `branch_count` branches each.

    Args:
        tree_count (int, optional): The number of trees to create. Defaults to 2.
        branch_count (int, optional): The number of branches to create for each tree. Defaults to 3.

    Returns:
        list of trees (json)
    """
    async with override_user():
        trees = []
        for i in range(tree_count):
            # create a tree
            response = await async_client.post(
                "/api/tree",
                json={
                    "tree_id": f"tree_{i}",
                    "title": f"Title of Tree {i}",
                    "description": f"Description of Tree {i}",
                },
                headers={"Authorization": f"Bearer {client_token}"},
            )
            assert response.status_code == 201
            tree = response.json()
            assert tree["tree_id"] == f"tree_{i}"
            tree["branches"] = []

            # add N branches
            for j in range(branch_count):
                response = await async_client.post(
                    "/api/branch",
                    json={
                        "tree_uuid": tree["uuid"],
                        "mac": f"12:34:56:78:9a:{j:02x}",
                        "branch_id": f"branch{j}_of_tree_{i}",
                        "description": f"Description of Branch {j}",
                    },
                    headers={"Authorization": f"Bearer {client_token}"},
                )
                assert response.status_code == 201
                # add the branch to the tree with the temporary gateway token
                tree["branches"].append(response.json())
            trees.append(tree)
        return trees


@pytest.fixture
async def client_token(async_client):
    token = await async_client.get("/api/client_token")
    assert token.status_code == 200
    return token.json()
