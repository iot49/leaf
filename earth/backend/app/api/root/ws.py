import logging

from fastapi import HTTPException, WebSocket

from app.tokens import verify_client_token_
from eventbus import serve

from ...bus import config
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
            user = await verify_client_token_(token)
            if user is None:
                return (False, "")
            param["user"] = user.email
            _CLIENT_ADDR += 1
            client_addr = f"@{_CLIENT_ADDR}"
            return (True, client_addr)
        except HTTPException:
            return (False, "")

    await websocket.accept()
    # won't return until the connection is closed
    logger.debug(f"accepted connection {param}")
    await serve(websocket, authenticate, param)  # type: ignore
    logger.debug(f"closed connection {param}")
