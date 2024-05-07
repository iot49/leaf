from eventbus.bus import Server

from . import router


# /api/connections
@router.get("/connections")
def get_connections():
    return Server.CONNECTIONS
