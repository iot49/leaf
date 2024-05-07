from app.env import env
from httpx import AsyncClient
from tests.util import is_subset


async def test_init_db(async_client: AsyncClient):
    for path in ["tree", "branch", "api_key"]:
        response = await async_client.get(f"/api/{path}/count")
        assert response.status_code == 200
        assert response.json() == 0
        response = await async_client.get(f"/api/{path}")
        assert response.status_code == 200
        assert len(response.json()) == 0

    response = await async_client.get("/api/user/count")
    assert response.status_code == 200
    assert response.json() == 1
    response = await async_client.get("/api/user")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert is_subset(
        [
            {
                "email": env.FIRST_SUPERUSER_EMAIL,
                "roles": ["superuser", "admin"],
                "name": "first superuser",
                "profile": "",
                "trees": [],
            }
        ],
        response.json(),
    )


async def test_user(create_users, async_client: AsyncClient):
    users = create_users
    admin = users["admin@x.y"]

    # creating user with same email fails
    response = await async_client.post("/api/user", json={"email": admin["email"]})
    assert response.status_code == 409

    # creating user with new email
    response = await async_client.post("/api/user", json={"email": "other@blue.com"})
    assert response.status_code == 201

    # deleting a user
    response = await async_client.delete(f"/api/user/{admin['uuid']}")
    assert response.status_code == 200
    assert response.json() == admin


async def test_api_key(create_api_key, async_client: AsyncClient):
    response = await async_client.get("/api/api_key")
    assert response.status_code == 200
    api_keys = response.json()
    assert len(api_keys) == 1
    assert is_subset([create_api_key], api_keys)

    # creating a 2nd
    key2 = (await async_client.post("/api/api_key", json={})).json()
    response = await async_client.get("/api/api_key")
    api_keys = response.json()
    assert response.status_code == 200
    assert key2["key"] != create_api_key["key"]
    assert is_subset(api_keys, [create_api_key, key2])

    # delete
    response = await async_client.delete(f"/api/api_key/{create_api_key['uuid']}")
    assert response.status_code == 200
    assert response.json() == create_api_key
