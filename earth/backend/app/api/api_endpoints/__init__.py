# ruff: noqa: F401, E402

from fastapi import APIRouter

router = APIRouter()

from . import connections, tokens, update_config, vm
