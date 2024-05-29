from ..base import create_endpoints
from .crud import crud
from .schema import TreeCreate, TreeRead, TreeUpdate

# add the default endpoints
router = create_endpoints(crud, TreeCreate, TreeRead, TreeUpdate)
