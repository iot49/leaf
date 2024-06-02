import logging

from fastapi import HTTPException, WebSocket

from eventbus import serve

from ...bus import certificates, config, secrets
from ...env import Environment, env
from ...tokens import verify_gateway2earth
from ..tree.schema import TreeRead
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# /gateway/ws  (serve gateway)
@router.websocket("/ws")
async def tree_ws(websocket: WebSocket):
    param = {
        "client": str(websocket.client.host),  # type: ignore
        "versions": {"config": config.get("version")},
    }

    async def authenticate(token: str) -> str | None:
        try:
            tree: TreeRead = await verify_gateway2earth(token)
            param["versions"]["secrets"] = await secrets.get_version(tree.tree_id)
            if env.ENVIRONMENT == Environment.production:
                param["versions"]["certificate"] = certificates.get_version(tree.tree_id)
            return tree.tree_id
        except HTTPException:
            logger.error(f"authentication failed for {param.get('client')}, token = {token}")
            return None

    await websocket.accept()

    # won't return until the connection is closed
    await serve(websocket, authenticate, param, timeout=env.GATEWAY_WS_TIMEOUT)  # type: ignore
    logger.info(f"gateway connection closed {param}")

    try:
        await websocket.close()
    except Exception as e:
        logger.error(f"ws {id(websocket)} - close failed: {e}")
