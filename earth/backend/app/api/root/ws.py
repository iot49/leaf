import logging

from fastapi import HTTPException, WebSocket

from eventbus import serve

from ...bus import config
from ...env import env
from ...tokens import verify_client2earth
from ..user.schema import UserRead
from . import router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_CLIENT_ADDR = 1


# /ws  (serve client)
@router.websocket("/ws")
async def client_ws(websocket: WebSocket):
    param = {
        "client": str(websocket.client.host),  # type: ignore
        "versions": {"config": config.get("version")},
    }

    async def authenticate(token: str) -> str | None:
        """
        Authenticates the client connection using the provided token.

        Args:
            token (str): The token submitted for client authentication.

        Returns:
            client address or None if client is not authenticated
        """
        if token is None:
            logger.error(f"no token submitted for client connection {param}")
            return None
        global _CLIENT_ADDR
        try:
            logger.debug(f"client authentication: {token}")
            user: UserRead = await verify_client2earth(token)
            param["user"] = user.email
            _CLIENT_ADDR += 1
            client_addr = f"@{_CLIENT_ADDR}"
            return client_addr
        except HTTPException as e:
            logger.error(f"client authentication failed: {e} token = {token}")
            return None

    await websocket.accept()

    # won't return until the connection is closed
    await serve(websocket, authenticate, param=param, timeout=env.CLIENT_WS_TIMEOUT)  # type: ignore
    logger.info(f"client connection closed {param}")

    try:
        await websocket.close()
    except Exception as e:
        logger.error(f"ws {id(websocket)} - close failed: {e}")
