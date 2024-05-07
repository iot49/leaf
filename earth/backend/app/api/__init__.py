from fastapi import APIRouter

# api routes
from . import (  # noqa: F401
    api_endpoints,
    api_key,
    dev,
    gateway,
    me,
    root,
    tree,
    user,
)

api_router = APIRouter()
api_router.include_router(tree.router, prefix="/tree", tags=["tree", "api"])
api_router.include_router(api_key.router, prefix="/api_key", tags=["api_key"])
api_router.include_router(user.router, prefix="/user", tags=["user", "api"])
api_router.include_router(dev.router, prefix="/dev", tags=["dev", "api"])
api_router.include_router(me.router, tags=["me", "api"])
api_router.include_router(api_endpoints.router, tags=["api", "api"])

from . import branch  # noqa: E402

api_router.include_router(branch.router, prefix="/branch", tags=["branch", "api"])
