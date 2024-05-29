import logging

from fastapi import HTTPException, WebSocket

from eventbus import serve

from ...bus import certificates, config, secrets
from ...env import env
from ...tokens import verify_gateway_token
from ..tree.schema import TreeRead
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# /gateway/ws  (serve gateway)
@router.websocket("/ws")
async def tree_ws(websocket: WebSocket):
    param = {
        "client": str(websocket.client.host),  # type: ignore
        "versions": {"config": config.get("version")},
    }

    async def authenticate(token: str) -> tuple[bool, str]:
        try:
            tree: TreeRead | None = await verify_gateway_token(token)
            if tree is None:
                return (False, "")
            param["versions"]["secrets"] = await secrets.get_version(tree.tree_id)
            # TODO: increase timeout except for testing
            param["versions"]["certificate"] = certificates.get_version(tree.tree_id, timeout=0.1)
            return (True, tree.tree_id)
        except HTTPException:
            return (False, "")

    await websocket.accept()
    # won't return until the connection is closed

    logger.debug(f"accepted gateway connection {param}")
    await serve(websocket, authenticate, param, timeout=env.GATEWAY_WS_TIMEOUT)  # type: ignore
    logger.debug(f"closed gateway connection {param}")
