from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..base import CRUDBase
from ..branch.model import Branch
from .model import Tree
from .schema import TreeCreate, TreeRead, TreeUpdate


class CRUDTree(CRUDBase[Tree, TreeCreate, TreeRead, TreeUpdate]):
    # customize get_by_uuid to include branches
    async def get_by_uuid_with_branches(self, *, uuid: UUID | str, db_session: AsyncSession) -> Tree:
        tree = await super().get_by_uuid(uuid=uuid, db_session=db_session)
        branches = await db_session.execute(select(Branch).where(Branch.tree_uuid == tree.uuid))  # type: ignore
        branches = branches.scalars().all()
        return Tree(**tree.model_dump(), branches=branches)  # type: ignore

    async def get_by_tree_id(self, *, tree_id: str, db_session: AsyncSession) -> TreeRead:
        tree = await db_session.execute(select(Tree).where(Tree.tree_id == tree_id))  # type: ignore
        tree = tree.scalars().first()  # Get the first result from the query
        if tree is None:
            raise HTTPException(status_code=404, detail="Tree not found")
        return tree

    async def get_tree_branches(self, *, uuid: UUID | str, db_session: AsyncSession) -> list[Branch]:
        branches = await db_session.execute(select(Branch).where(Branch.tree_uuid == uuid))  # type: ignore
        branches = branches.scalars().all()
        return branches  # type: ignore

    # customize to also delete linked branches
    async def remove(self, *, uuid: UUID | str, db_session: AsyncSession) -> TreeRead:
        # verify the object exists
        obj = await db_session.get(self.model, uuid)
        if obj is None:
            raise HTTPException(status_code=404, detail="Object not found")
        # first remove the branches
        await db_session.execute(delete(Branch).where(Branch.tree_uuid == uuid))  # type: ignore
        # then remove the tree
        await db_session.delete(obj)
        await db_session.commit()
        return obj  # type: ignore


crud = CRUDTree(Tree)
