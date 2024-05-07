from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api import api_key
from app.dependencies.verify_jwt import verify_gateway_token
from app.tokens import new_gateway_token, verify_gateway_token_
from eventbus import serve

from ...db import get_session
from ...event_handlers import eventbus_config

router = APIRouter()


@router.get("/secrets")
async def secrets(request: Request, session: AsyncSession = Depends(get_session), tree=Depends(verify_gateway_token)):
    key = await api_key.get_key(db_session=session)
    gateway_token = await new_gateway_token(tree_uuid=tree.uuid, api_key=key)
    return {"tree": tree, "gateway-token": gateway_token}


# /gateway/ws  (serve gateway)
@router.websocket("/ws")
async def tree_ws(websocket: WebSocket):
    param = {
        "host": str(websocket.headers.get("host")),
        "versions": {"config": eventbus_config.get("version")},
        "gateway": True,
    }

    def addr_filter(dst: str) -> bool:
        # peer is the <tree_id>; allow <tree_id>:<branch_id>
        return dst == "#branches" or dst.startswith(param["peer"])

    async def authenticate(token: str) -> bool:
        try:
            tree = await verify_gateway_token_(token)
            param["peer"] = tree.tree_id
            return True
        except HTTPException:
            return False

    await websocket.accept()
    # won't return until the connection is closed
    await serve(websocket, addr_filter, authenticate, param)  # type: ignore
