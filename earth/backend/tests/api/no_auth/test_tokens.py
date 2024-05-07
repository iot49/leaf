import jwt
from tests.util import is_subset


async def test_client_token(async_client, create_trees):
    me = await async_client.get("/api/me")
    assert me.status_code == 200
    user = me.json()

    # verify that user has a valid tree token for each tree
    for tree in user["trees"]:
        client_token = tree["client_token"]
        assert is_subset(
            {
                "aud": "client->earth",
                "tree_uuid": tree["uuid"],
                "user_uuid": user["uuid"],
            },
            jwt.decode(client_token, options={"verify_signature": False}),
        )


async def test_gateway_token(async_client, create_trees):
    for tree in create_trees:
        gateway_token = tree["branches"][0]["gateway_token"]
        assert is_subset(
            {
                "aud": "gateway->earth",
                "tree_uuid": tree["uuid"],
            },
            jwt.decode(gateway_token, options={"verify_signature": False}),
        )
        assert is_subset(
            {
                "aud": "gateway->earth",
                "tree_uuid": tree["uuid"],
            },
            jwt.decode(gateway_token, options={"verify_signature": False}),
        )

        # use the token to get the secrets (and permanent token)
        secrets = await async_client.get("/gateway/secrets", headers={"Authorization": f"Bearer {gateway_token}"})
        assert secrets.status_code == 200
        secrets = secrets.json()
        for branch in tree["branches"]:
            branch.pop("gateway_token")
        assert is_subset(tree, secrets["tree"])

        # permanent token, verify it's useable
        gateway_token = secrets["gateway-token"]
        response = await async_client.get("/gateway/secrets", headers={"Authorization": f"Bearer {gateway_token}"})
        assert response.status_code == 200
