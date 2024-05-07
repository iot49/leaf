from fastapi import APIRouter, Request

from ...env import env

router = APIRouter()


@router.get("/settings")
async def settings():
    return env.model_dump()


@router.get("/cookies")
async def read_cookies(request: Request):
    return {"cookies": request.cookies}


@router.get("/headers")
async def read_headers(request: Request):
    return {"headers": request.headers}


@router.get("/request")
async def read_text(request: Request):
    return {
        "base_url": request.base_url,
        "client": request.client,
        "method": request.method,
        "path_params": request.path_params,
        "query_params": request.query_params,
        "url": request.url,
        "url_for": request.url_for,
    }
