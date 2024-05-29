from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from ...tokens import new_client2gateway
from .. import tree as _tree
from ..base import CRUDBase
from ..user.model import User
from ..user.schema import TreeReadWithToken, UserCreate, UserRead, UserUpdate, UserUpdateNoRoles


class CRUDMe(CRUDBase[User, UserCreate, UserRead, UserUpdate]):
    async def get_me(
        self,
        *,
        uuid: UUID | str,
        db_session: AsyncSession,
    ) -> UserRead:
        user = await super().get_by_uuid(uuid=uuid, db_session=db_session)
        user = UserRead(**user.model_dump())
        trees = await _tree.crud.get_list(db_session=db_session)

        # filter trees based on permissions
        for tree in trees:
            # tokens for local tree websocket access
            # only admin and user roles can connect to trees
            if set(["admin", "user"]).isdisjoint(user.roles):
                jwt_ = "no access"
            else:
                jwt_ = await new_client2gateway(tree=tree)  # type: ignore
            user.trees.append(TreeReadWithToken(**tree.model_dump(), client_token=jwt_))
        return UserRead(**user.model_dump())

    async def update_me(
        self,
        *,
        uuid: UUID,
        obj_new: UserUpdateNoRoles,
        db_session: AsyncSession,
    ) -> UserRead:
        update = UserUpdate(**obj_new.model_dump(exclude_none=True))
        return await super().update(uuid=uuid, obj_new=update, db_session=db_session)


crud = CRUDMe(User)
