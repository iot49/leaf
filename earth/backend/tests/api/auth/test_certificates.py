from app.bus.certificates import get_certificates
from app.env import get_env


async def test_certificates(create_trees):
    # there isn't much to test without the certbot ...
    for tree in create_trees:
        certs = get_certificates(tree["tree_id"])
        assert certs["domain"] == f"{tree['tree_id']}.ws.{get_env().DOMAIN}"
        assert all(k in certs.keys() for k in ["tree_id", "domain", "cert", "privkey", "version"])
        assert certs["tree_id"] == tree["tree_id"]
