from fastapi import HTTPException, WebSocket

from app.tokens import verify_client_token_
from eventbus import serve

from ...event_handlers import eventbus_config
from . import router

_CLIENT_ADDR = 1


# /ws  (serve client)
@router.websocket("/ws")
async def client_ws(websocket: WebSocket):
    global _CLIENT_ADDR
    _CLIENT_ADDR += 1
    peer = f"@{_CLIENT_ADDR}"

    param = {
        "peer": peer,
        "host": str(websocket.headers.get("host")),
        "versions": {"config": eventbus_config.get("version")},
        "gateway": False,
    }

    def addr_filter(dst: str) -> bool:
        return dst in ("#clients", peer)

    async def authenticate(token: str) -> bool:
        try:
            user = await verify_client_token_(token)
            param["user"] = user.email
            return True
        except HTTPException:
            return False

    await websocket.accept()
    # won't return until the connection is closed
    await serve(websocket, addr_filter, authenticate, param)  # type: ignore
