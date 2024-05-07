from ..base import create_endpoints
from .crud import crud
from .schema import BranchCreate, BranchRead, BranchUpdate

router = create_endpoints(crud, BranchCreate, BranchRead, BranchUpdate)
