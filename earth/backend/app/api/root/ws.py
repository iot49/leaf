from fastapi import HTTPException, WebSocket

from app.tokens import verify_client_token_
from eventbus import serve

from ...bus import config
from . import router

_CLIENT_ADDR = 1


# /ws  (serve client)
@router.websocket("/ws")
async def client_ws(websocket: WebSocket):
    param = {
        "host": str(websocket.headers.get("host")),
        "url": str(websocket.url),
        "versions": {"config": config.get("version")},
    }

    async def authenticate(token: str) -> tuple[bool, str]:
        global _CLIENT_ADDR
        try:
            user = await verify_client_token_(token)
            param["user"] = user.email
            _CLIENT_ADDR += 1
            client_addr = f"@{_CLIENT_ADDR}"
            return (True, client_addr)
        except HTTPException:
            return (False, "")

    await websocket.accept()
    # won't return until the connection is closed
    await serve(websocket, authenticate, param)  # type: ignore
