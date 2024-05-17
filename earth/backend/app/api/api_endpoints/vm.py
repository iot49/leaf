import logging

from . import router

logger = logging.getLogger(__name__)


@router.get("/vm")
async def get_releases():
    return {"message": "Hello World"}


@router.get("/vm/{tag}/{arch}")
async def get_vm(tag: str, arch: str):
    return {"message": "Hello World"}
