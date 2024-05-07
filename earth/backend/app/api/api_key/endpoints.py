from ..base import create_endpoints
from .crud import crud
from .schema import ApiKeyCreate, ApiKeyRead, ApiKeyUpdate

# create the default endpoints
router = create_endpoints(crud, ApiKeyCreate, ApiKeyRead, ApiKeyUpdate)
