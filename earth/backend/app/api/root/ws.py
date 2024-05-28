import logging

from fastapi import HTTPException, WebSocket

from eventbus import serve

from ...bus import config
from ...tokens import verify_client_token
from ..user.schema import UserRead
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_CLIENT_ADDR = 1


# /ws  (serve client)
@router.websocket("/ws")
async def client_ws(websocket: WebSocket):
    param = {
        "client": str(websocket.client.host),  # type: ignore
        # "host": str(websocket.headers.get("host")),
        # "url": str(websocket.url),
        "versions": {"config": config.get("version")},
    }

    async def authenticate(token: str) -> tuple[bool, str]:
        global _CLIENT_ADDR
        try:
            user: UserRead = await verify_client_token(token)  # type: ignore
            param["user"] = user.email
            _CLIENT_ADDR += 1
            client_addr = f"@{_CLIENT_ADDR}"
            return (True, client_addr)
        except HTTPException as e:
            logger.error(f"client authentication failed: {e}")
            return (False, "")

    await websocket.accept()
    # won't return until the connection is closed
    logger.debug(f"accepted connection {param}")
    await serve(websocket, authenticate, param)  # type: ignore
    logger.debug(f"closed connection {param}")
