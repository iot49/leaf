import logging

from fastapi.requests import HTTPConnection

logger = logging.getLogger(__name__)


async def connection_report(request: HTTPConnection):
    logger.info(f"connection_report {request.url.path} {request.headers}")
    yield
