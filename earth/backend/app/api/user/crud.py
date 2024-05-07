from ..base import CRUDBase
from .model import User
from .schema import UserCreate, UserRead, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserRead, UserUpdate]):
    pass


crud = CRUDUser(User)
