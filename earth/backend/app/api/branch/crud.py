from datetime import timedelta

from sqlmodel.ext.asyncio.session import AsyncSession

from app.api import api_key

from .. import tree
from ..base import CRUDBase
from .model import Branch
from .schema import BranchCreate, BranchRead, BranchUpdate


class CRUDIotBranch(CRUDBase[Branch, BranchCreate, BranchRead, BranchUpdate]):
    async def create(
        self,
        *,
        obj_in: BranchCreate | Branch,
        db_session: AsyncSession,
    ) -> BranchRead:
        from ...tokens import new_gateway_token

        # verify the tree exists (returns 404 if not found)
        await tree.crud.get_by_uuid(uuid=obj_in.tree_uuid, db_session=db_session)
        # now create the branch
        branch = await super().create(obj_in=obj_in, db_session=db_session)
        key = await api_key.get_key(db_session=db_session)
        # token for onboarding
        # since passed to the branch from the client, we give it a short duration in case it's leaked
        # TODO: reduce sign-up gateway_token validity
        token = await new_gateway_token(
            branch.tree_uuid,
            api_key=key,
            validity=timedelta(minutes=1000),
        )
        return BranchRead(**branch.model_dump(), gateway_token=str(token))


crud = CRUDIotBranch(Branch)
