from ..base import create_endpoints
from .crud import crud
from .schema import BranchCreate, BranchRead, BranchUpdate

router = create_endpoints(crud, BranchCreate, BranchRead, BranchUpdate)


@router.post("", response_model={})
async def create_with_secrets():
    pass
