import logging
from datetime import datetime

import aiohttp
from asyncache import cached
from cachetools import TTLCache
from fastapi import HTTPException, Response
from pydantic import BaseModel
from pydantic_core import Url

from ...env import env
from . import router

logger = logging.getLogger(__name__)


class GitReleaseAsset(BaseModel):
    name: str
    size: int
    browser_download_url: Url


class GitRelease(BaseModel):
    tag_name: str
    name: str
    published_at: datetime
    # assets: list[GitReleaseAsset]


class GitReleases(BaseModel):
    releases: list[GitRelease]


class OctetStreamResponse(Response):
    media_type = "application/octet-stream"


@cached(cache=TTLCache(maxsize=32, ttl=600))
async def get_resource(resource: str = "releases"):
    url = f"https://api.github.com/repos/{env.GITHUB_OWNER}/{env.GITHUB_REPO}/{resource}"
    headers = {
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=f"Failed fetching {url}")
            return await response.json()


@cached(cache=TTLCache(maxsize=32, ttl=24 * 3600))
async def get_binary(tag: str = "v0.0.8", board: str = "ESP32_S3_N16R8", file="micropython.bin"):
    url = f"https://github.com/{env.GITHUB_OWNER}/{env.GITHUB_REPO}/releases/download/{tag}/{board}-{file}"
    headers = {
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "binary/octet-stream",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail=f"Failed fetching {url}")
            return await response.read()


@router.get("/vm", response_model=GitReleases)
async def get_releases() -> GitReleases:
    resource = await get_resource("releases")
    model = GitReleases.model_validate({"releases": resource})
    return model


@router.get("/vm/{tag}/{board}/{file}", response_class=OctetStreamResponse)
async def get_vm(response: Response, tag: str, board: str, file: str):
    data = await get_binary(tag=tag, board=board, file=file)
    response.media_type = "binary/octet-stream"
    return Response(content=data, media_type="binary/octet-stream")
