from app.bus.secrets import get_secrets_tree_id
from app.env import get_env


async def test_secrets(create_trees):
    for tree in create_trees:
        secrets = await get_secrets_tree_id(tree_id=tree["tree_id"])
        assert secrets is not None
        assert secrets["domain"] == f"{tree['tree_id']}.ws.{get_env().DOMAIN}"
        assert all(k in secrets.keys() for k in ["gateway-token", "version", "tree"])
        assert secrets["tree"]["tree_id"] == tree["tree_id"]
