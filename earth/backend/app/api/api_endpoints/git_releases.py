import json

import aiohttp
from pydantic import BaseModel
from pydantic_core import Url

from app.env import env


class GitReleaseAsset(BaseModel):
    name: str
    size: int
    updated_at: str
    browser_download_url: Url


class GitRelease(BaseModel):
    tag_name: str
    name: str
    assets: list[GitReleaseAsset]


class GitReleases(BaseModel):
    releases: list[GitRelease]


async def get_resource(resource: str = "releases"):
    url = f"https://api.github.com/repos/{env.GITHUB_OWNER}/{env.GITHUB_REPO}/{resource}"
    headers = {
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json",
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            print(response.status)
            print(json.dumps(await response.json(), indent=2))


RESOURCE = [
    {
        "url": "https://api.github.com/repos/iot49/leaf/releases/156307093",
        "assets_url": "https://api.github.com/repos/iot49/leaf/releases/156307093/assets",
        "upload_url": "https://uploads.github.com/repos/iot49/leaf/releases/156307093/assets{?name,label}",
        "html_url": "https://github.com/iot49/leaf/releases/tag/v0.0.2",
        "id": 156307093,
        "author": {
            "login": "github-actions[bot]",
            "id": 41898282,
            "node_id": "MDM6Qm90NDE4OTgyODI=",
            "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/github-actions%5Bbot%5D",
            "html_url": "https://github.com/apps/github-actions",
            "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
            "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
            "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
            "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
            "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
            "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
            "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
            "type": "Bot",
            "site_admin": False,
        },
        "node_id": "RE_kwDOL4ZmU84JUQ6V",
        "tag_name": "v0.0.2",
        "target_commitish": "main",
        "name": "ESP32_S3_N16R8 V0.0.2",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-05-17T16:56:26Z",
        "published_at": "2024-05-17T17:02:32Z",
        "assets": [
            {
                "url": "https://api.github.com/repos/iot49/leaf/releases/assets/168546849",
                "id": 168546849,
                "node_id": "RA_kwDOL4ZmU84KC9Ih",
                "name": "firmware.bin",
                "label": "",
                "uploader": {
                    "login": "github-actions[bot]",
                    "id": 41898282,
                    "node_id": "MDM6Qm90NDE4OTgyODI=",
                    "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                    "html_url": "https://github.com/apps/github-actions",
                    "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                    "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                    "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                    "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                    "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                    "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                    "type": "Bot",
                    "site_admin": False,
                },
                "content_type": "application/octet-stream",
                "state": "uploaded",
                "size": 1787424,
                "download_count": 0,
                "created_at": "2024-05-17T17:02:27Z",
                "updated_at": "2024-05-17T17:02:31Z",
                "browser_download_url": "https://github.com/iot49/leaf/releases/download/v0.0.2/firmware.bin",
            },
            {
                "url": "https://api.github.com/repos/iot49/leaf/releases/assets/168546850",
                "id": 168546850,
                "node_id": "RA_kwDOL4ZmU84KC9Ii",
                "name": "micropython.bin",
                "label": "",
                "uploader": {
                    "login": "github-actions[bot]",
                    "id": 41898282,
                    "node_id": "MDM6Qm90NDE4OTgyODI=",
                    "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                    "html_url": "https://github.com/apps/github-actions",
                    "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                    "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                    "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                    "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                    "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                    "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                    "type": "Bot",
                    "site_admin": False,
                },
                "content_type": "application/octet-stream",
                "state": "uploaded",
                "size": 1721888,
                "download_count": 0,
                "created_at": "2024-05-17T17:02:27Z",
                "updated_at": "2024-05-17T17:02:31Z",
                "browser_download_url": "https://github.com/iot49/leaf/releases/download/v0.0.2/micropython.bin",
            },
        ],
        "tarball_url": "https://api.github.com/repos/iot49/leaf/tarball/v0.0.2",
        "zipball_url": "https://api.github.com/repos/iot49/leaf/zipball/v0.0.2",
        "body": None,
    },
    {
        "url": "https://api.github.com/repos/iot49/leaf/releases/156151879",
        "assets_url": "https://api.github.com/repos/iot49/leaf/releases/156151879/assets",
        "upload_url": "https://uploads.github.com/repos/iot49/leaf/releases/156151879/assets{?name,label}",
        "html_url": "https://github.com/iot49/leaf/releases/tag/v0.0.1",
        "id": 156151879,
        "author": {
            "login": "github-actions[bot]",
            "id": 41898282,
            "node_id": "MDM6Qm90NDE4OTgyODI=",
            "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
            "gravatar_id": "",
            "url": "https://api.github.com/users/github-actions%5Bbot%5D",
            "html_url": "https://github.com/apps/github-actions",
            "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
            "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
            "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
            "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
            "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
            "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
            "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
            "type": "Bot",
            "site_admin": False,
        },
        "node_id": "RE_kwDOL4ZmU84JTrBH",
        "tag_name": "v0.0.1",
        "target_commitish": "main",
        "name": "leaf MicroPython VM for ESP32_S3_N16R8 0.0.1",
        "draft": False,
        "prerelease": False,
        "created_at": "2024-05-16T19:26:19Z",
        "published_at": "2024-05-16T19:30:27Z",
        "assets": [
            {
                "url": "https://api.github.com/repos/iot49/leaf/releases/assets/168357554",
                "id": 168357554,
                "node_id": "RA_kwDOL4ZmU84KCO6y",
                "name": "firmware.bin",
                "label": "",
                "uploader": {
                    "login": "github-actions[bot]",
                    "id": 41898282,
                    "node_id": "MDM6Qm90NDE4OTgyODI=",
                    "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                    "html_url": "https://github.com/apps/github-actions",
                    "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                    "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                    "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                    "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                    "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                    "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                    "type": "Bot",
                    "site_admin": False,
                },
                "content_type": "application/octet-stream",
                "state": "uploaded",
                "size": 1787344,
                "download_count": 3,
                "created_at": "2024-05-16T19:30:26Z",
                "updated_at": "2024-05-16T19:30:26Z",
                "browser_download_url": "https://github.com/iot49/leaf/releases/download/v0.0.1/firmware.bin",
            },
            {
                "url": "https://api.github.com/repos/iot49/leaf/releases/assets/168357553",
                "id": 168357553,
                "node_id": "RA_kwDOL4ZmU84KCO6x",
                "name": "micropython.bin",
                "label": "",
                "uploader": {
                    "login": "github-actions[bot]",
                    "id": 41898282,
                    "node_id": "MDM6Qm90NDE4OTgyODI=",
                    "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                    "gravatar_id": "",
                    "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                    "html_url": "https://github.com/apps/github-actions",
                    "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                    "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                    "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                    "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                    "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                    "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                    "type": "Bot",
                    "site_admin": False,
                },
                "content_type": "application/octet-stream",
                "state": "uploaded",
                "size": 1721808,
                "download_count": 0,
                "created_at": "2024-05-16T19:30:26Z",
                "updated_at": "2024-05-16T19:30:26Z",
                "browser_download_url": "https://github.com/iot49/leaf/releases/download/v0.0.1/micropython.bin",
            },
        ],
        "tarball_url": "https://api.github.com/repos/iot49/leaf/tarball/v0.0.1",
        "zipball_url": "https://api.github.com/repos/iot49/leaf/zipball/v0.0.1",
        "body": "**Full Changelog**: https://github.com/iot49/leaf/commits/v0.0.1",
    },
]


releases = GitReleases.model_validate({"releases": RESOURCE})

print(releases.model_dump_json(indent=2))
