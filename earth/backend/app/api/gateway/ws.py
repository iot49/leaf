from fastapi import HTTPException, WebSocket

from eventbus import serve

from ...bus import certificates, config, secrets
from ...tokens import verify_gateway_token_
from . import router


# /gateway/ws  (serve gateway)
@router.websocket("/ws")
async def tree_ws(websocket: WebSocket):
    param = {
        "host": str(websocket.headers.get("host")),
        "url": str(websocket.url),
        "versions": {"config": config.get("version")},
    }

    async def authenticate(token: str) -> tuple[bool, str]:
        try:
            tree = await verify_gateway_token_(token)
            param["versions"]["secrets"] = await secrets.get_version(tree.tree_id)
            # TODO: increase timeout except for testing
            param["versions"]["certificate"] = certificates.get_version(tree.tree_id, timeout=0.1)
            return (True, tree.tree_id)
        except HTTPException:
            return (False, "")

    await websocket.accept()
    # won't return until the connection is closed
    await serve(websocket, authenticate, param)  # type: ignore