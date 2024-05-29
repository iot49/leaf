from fastapi.encoders import jsonable_encoder
from sqlmodel.ext.asyncio.session import AsyncSession

import eventbus
from eventbus import Event, EventBus, event_type, post, subscribe
from eventbus.event import put_secrets

from .. import api, db, env, tokens


async def _get_version(tree, session: AsyncSession) -> str:  # api.tree.schema.TreeReadWithBraches):
    """Most recent update to tree or any branch."""
    branches = await api.tree.crud.get_tree_branches(uuid=tree.uuid, db_session=session)
    dates = [branch.updated_at for branch in branches if branch.updated_at is not None]
    dates.append(tree.updated_at)  # type: ignore
    return max(dates).replace(microsecond=0).isoformat()


async def get_version(tree_id: str) -> str:
    async for session in db.get_session():
        tree = await api.tree.crud.get_by_tree_id(tree_id=tree_id, db_session=session)  # type: ignore
        return await _get_version(tree, session)
    return ""


async def _get_secrets(tree, session: AsyncSession) -> dict:
    api_key = await api.api_key.get_key(db_session=session)
    gateway_token = await tokens.new_gateway2earth(tree=tree, api_key=api_key)
    branches = await api.tree.crud.get_tree_branches(uuid=tree.uuid, db_session=session)

    tree_ = jsonable_encoder(tree)
    tree_["branches"] = [jsonable_encoder(branch) for branch in branches]

    return {
        "domain": f"{tree.tree_id}.ws.{env.get_env().DOMAIN}",
        "tree": tree_,
        "gateway-token": gateway_token,
        "version": await _get_version(tree, session),
    }


async def get_secrets_uuid(*, tree_uuid: str) -> dict:
    async for session in db.get_session():
        tree = await api.tree.crud.get_by_uuid(uuid=tree_uuid, db_session=session)
        return await _get_secrets(tree, session)
    return {}


async def get_secrets_tree_id(
    *,
    tree_id: str,
) -> dict:
    async for session in db.get_session():
        tree = await api.tree.crud.get_by_tree_id(tree_id=tree_id, db_session=session)
        return await _get_secrets(tree, session)
    return {}


class Secrets(EventBus):
    """Tree secrets."""

    def __init__(self):
        subscribe(self)

    async def post(self, event: Event) -> None:
        et = event["type"]
        if et == event_type.GET_SECRETS:
            tree_id = eventbus.tree_id(event["src"])
            secrets = await get_secrets_tree_id(tree_id=tree_id)
            if secrets is not None:
                await post(put_secrets(event, secrets=secrets))
