from sqlmodel.ext.asyncio.session import AsyncSession

from .. import tree
from ..base import CRUDBase
from .model import Branch
from .schema import BranchCreate, BranchRead, BranchUpdate


class CRUDIotBranch(CRUDBase[Branch, BranchCreate, BranchRead, BranchUpdate]):
    async def create_with_secrets(
        self,
        *,
        obj_in: BranchCreate | Branch,
        db_session: AsyncSession,
    ) -> BranchRead:
        # verify the tree exists (raises 404 if not found)
        await tree.crud.get_by_uuid(uuid=obj_in.tree_uuid, db_session=db_session)

        # now create the branch
        branch = await super().create(obj_in=obj_in, db_session=db_session)

        return branch


crud = CRUDIotBranch(Branch)
