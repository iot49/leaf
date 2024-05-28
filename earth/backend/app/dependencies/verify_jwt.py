from fastapi import Depends, HTTPException
from fastapi.requests import HTTPConnection
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .. import api, db
from ..api.user.schema import UserRead
from ..env import Environment, env


class JWTAuth(HTTPBearer):
    # Gets around a FastAPI bug
    async def __call__(
        self,
        request: HTTPConnection,
    ) -> HTTPAuthorizationCredentials:
        if not request or not request.headers.get("Authorization"):
            if self.auto_error:
                raise HTTPException(status_code=403, detail="No authentication (Bearer Token) submitted")
        return await super().__call__(request)  # type: ignore


async def verify_gateway_token(
    request: HTTPConnection,
    credentials: HTTPAuthorizationCredentials = Depends(JWTAuth()),
):  # -> api.tree.schema.TreeReadWithBraches:
    from .. import tokens

    token = credentials.credentials
    tree_ = await tokens.verify_gateway_token_(token=token)
    request.state.tree = tree_
    return tree_


async def verify_client_token(
    request: HTTPConnection,
    credentials: HTTPAuthorizationCredentials = Depends(JWTAuth()),
):  # -> api.user.schema.UserRead:
    from .. import tokens

    # skip verification for dev environment and localhost
    host = request.url.hostname
    if env.ENVIRONMENT == Environment.development and host in ["localhost", "127.0.0.1"]:
        # Skip verification when running locally
        async for db_session in db.get_session():
            superuser = (await api.user.crud.get_list(db_session=db_session))[0]  # type: ignore
            request.state.user_email = superuser.email
            request.state.user = superuser
            return superuser  # type: ignore

    token = credentials.credentials
    user_: UserRead = await tokens.verify_client_token_(token=token)  # type: ignore
    request.state.user_email = user_.email
    request.state.user = user_
    return user_
