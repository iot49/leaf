from fastapi import APIRouter

router = APIRouter()

from . import ws  # noqa: F401, E402
