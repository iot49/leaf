from fastapi.responses import RedirectResponse

from . import router


@router.get("/")
async def root():
    """
    Redirects to the UI.
    """
    return RedirectResponse(url="/ui")


@router.get("/ping")
async def ping():
    """
    An example "ping" FastAPI route. Useful to check server status.
    """
    return {"ping": "pong"}
