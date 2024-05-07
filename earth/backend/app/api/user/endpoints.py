from ..base import create_endpoints
from ..me.crud import crud
from .schema import UserCreate, UserRead, UserUpdate

# create the default endpoints
router = create_endpoints(crud, UserCreate, UserRead, UserUpdate)
