import pytest
from app.api.api_key import get_key
from app.api.user.model import User
from app.db import SessionLocal
from app.tokens import new_client_token, verify_client_token_
from httpx import AsyncClient
from sqlalchemy import select
from tests.api.conftest import override_user
from tests.util import is_subset


@pytest.fixture
async def superuser_token(async_client):
    me = await async_client.get("/api/me")
    return me.json()["client_token"]


async def test_client_token():
    async with SessionLocal() as session:
        # create a client token
        query = select(User)
        response = await session.execute(query)
        user1 = response.one()[0]
        api_key = await get_key(db_session=session)
        token = await new_client_token(user_uuid=user1.uuid, api_key=api_key)
        user2 = await verify_client_token_(token=token)
        assert user1 == user2


async def test_get_put_me(async_client: AsyncClient, create_users, create_trees):
    # all users can get/put /api/me
    for user in create_users.values():
        async with override_user(user["email"]):
            # change name
            response = await async_client.put("/api/me", json={"name": "new name"})
            assert response.status_code == 200 if user["roles"] else 403
            if response.status_code == 200:
                assert is_subset({"uuid": user["uuid"], "name": "new name"}, response.json())

            # change roles - ignored on /api/me
            response = await async_client.put("/api/me", json={"roles": ["admin"]})
            assert response.status_code == 200 if user["roles"] else 403
            if response.status_code == 200:
                assert is_subset({"roles": user["roles"]}, response.json())


async def test_admin_role(async_client: AsyncClient, create_users, create_trees, client_token):
    # only admin can access /tree, /branch
    for user in create_users.values():
        async with override_user(user["email"]):
            response = await async_client.get("/api/me")
            assert response.status_code == 200 if user["roles"] else 403
            if response.status_code != 200:
                continue
            me = response.json()
            assert is_subset(user, me)
            has_roles = len(user["roles"]) > 0
            expected_status = 200 if "admin" in user["roles"] else 403

            # all users (except no role) can fetch trees by uuid
            for tree in me["trees"]:
                tree_uuid = tree["uuid"]
                response = await async_client.get(f"/api/tree/{tree_uuid}")
                assert response.status_code == 200 if has_roles else 403
                response = response.json()
                assert "uuid" in response if has_roles else "detail" in response

            # all users can fetch trees by uuid or get the count
            response = await async_client.get("/api/tree/count")
            assert response.status_code == 200 if has_roles else 403

            # only admin can fetch all trees
            response = await async_client.get("/api/tree")
            assert response.status_code == expected_status
            assert len(response.json()) == 2 if "admin" in user["roles"] else 1

            # only admin can fetch branches
            response = await async_client.get("/api/branch")
            assert response.status_code == expected_status
            assert len(response.json()) == 6 if "admin" in user["roles"] else 1

            # ditto for put, post, delete


async def test_superuser_role(async_client: AsyncClient, create_users):
    # only admin can access /tree, /branch
    for user in create_users.values():
        async with override_user(user["email"]):
            response = await async_client.get("/api/me")
            assert response.status_code == 200 if user["roles"] else 403
            me = response.json()
            if response.status_code == 200:
                assert is_subset(user, me)
            expected_status = 200 if user["superuser"] else 403

            # only admin can access /user
            response = await async_client.get("/api/user/count")
            assert response.status_code == expected_status

            response = await async_client.get("/api/user")
            assert response.status_code == expected_status
            assert len(response.json()) == 7 if user["superuser"] else 1

            response = await async_client.get("/api/api_key")
            assert response.status_code == expected_status

            response = await async_client.get("/api/dev/settings")
            assert response.status_code == expected_status


async def test_gateway(async_client: AsyncClient, create_users, create_trees):
    for tree in create_trees:
        gateway_token = tree["branches"][0]["gateway_token"]
        for user in create_users.values():
            async with override_user(user["email"]):
                response = await async_client.get("/api/me")
                assert response.status_code == 200 if user["roles"] else 403
                me = response.json()
                if response.status_code == 200:
                    assert is_subset(user, me)

                response = await async_client.get("/gateway/secrets", headers={"Authorization": "Bearer bad token"})
                assert response.status_code == 401

                response = await async_client.get(
                    "/gateway/secrets", headers={"Authorization": f"Bearer {gateway_token}"}
                )
                assert response.status_code == 200
