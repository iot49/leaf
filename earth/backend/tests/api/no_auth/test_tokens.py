import jwt
from tests.util import is_subset


async def test_client_token(async_client, create_trees):
    me = await async_client.get("/api/me")
    assert me.status_code == 200
    user = me.json()

    # verify that user has a valid tree token for each tree
    for tree in user["trees"]:
        assert is_subset(
            {
                "aud": "client->gateway",
                "tree_uuid": tree["uuid"],
                "tree_id": tree["tree_id"],
            },
            jwt.decode(tree["client_token"], options={"verify_signature": False}),
        )
