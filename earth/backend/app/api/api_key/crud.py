from ..base import CRUDBase
from .model import ApiKey
from .schema import ApiKeyCreate, ApiKeyRead, ApiKeyUpdate


class CRUDApiKey(CRUDBase[ApiKey, ApiKeyCreate, ApiKeyRead, ApiKeyUpdate]):
    pass


crud = CRUDApiKey(ApiKey)
