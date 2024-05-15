from fastapi.encoders import jsonable_encoder

import eventbus
from eventbus import Event, EventBus, event_type, post, subscribe
from eventbus.event import put_secrets

from .. import api, db, env, tokens


def _get_version(tree) -> str:  # api.tree.schema.TreeReadWithBraches):
    """Most recent update to tree or any branch."""
    dates = [branch.updated_at for branch in tree.branches if branch.updated_at is not None]
    dates.append(tree.updated_at)  # type: ignore
    return max(dates).replace(microsecond=0).isoformat()


async def get_version(tree_id: str) -> str:
    async for session in db.get_session():
        tree = await api.tree.crud.get_by_tree_id(tree_id=tree_id, db_session=session)  # type: ignore
        return _get_version(tree)
    return ""


async def get_secrets(*, tree_uuid: str | None = None, tree_id: str | None = None) -> dict:
    async for session in db.get_session():
        if tree_uuid is not None:
            tree = await api.tree.crud.get_by_uuid(uuid=tree_uuid, db_session=session)  # type: ignore
        else:
            tree = await api.tree.crud.get_by_tree_id(tree_id=tree_id, db_session=session)  # type: ignore
        key = await api.api_key.get_key(db_session=session)
        gateway_token = await tokens.new_gateway_token(tree_uuid=tree.uuid, api_key=key)
        return {
            "domain": f"{tree.tree_id}.ws.{env.get_env().DOMAIN}",
            "tree": jsonable_encoder(tree),
            "gateway-token": gateway_token,
            "version": _get_version(tree),
        }
    return {}


class Secrets(EventBus):
    """Tree secrets."""

    def __init__(self):
        subscribe(self)

    async def post(self, event: Event) -> None:
        et = event["type"]
        if et == event_type.GET_SECRETS:
            tree_id = eventbus.tree_id(event["src"])
            await post(put_secrets(event, secrets=await get_secrets(tree_id=tree_id)))
