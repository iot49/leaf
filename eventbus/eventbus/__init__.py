import logging
from typing import Awaitable, Callable

from eventbus.event_emitter import EventEmitter

try:
    from asyncio import Queue, QueueFull
except AttributeError:
    # MicroPython asyncio misses Queue
    from asyncio_extra import Queue, QueueFull  # type: ignore # noqa: F401

from . import event_type  # noqa: F401

WS_TIMEOUT = 5  # disconnect if no message received [seconds]

"""
EventBus - a simple interface for routing events (dicts).

Methods:

- post(event: Event) -> None: Post an event to this eventbus.
- subscribe(bus: EventBus) -> None: Subscribe to this eventbus.
- unsubscribe(bus: EventBus) -> None: Unsubscribe from this eventbus.
"""

Addr = str
"""Address

- branch address: <tree_id>.<branch_id> or just <tree_id> (goes to all branches)
- client address: @<client_id>
- special addresses: 
    * #earth, 
    * #branches, (all branches)
    * #clients, (clients, e.g. web ui)
    * #server (gateway or #earth, handle get_config, etc.)
- Note: to broadcast to all nodes, separately post to 
        #branches and #clients to avoid recursion
"""

Event = dict
"""Event

Mandatory fields:
- type: str
- src: Addr
- dst: Addr
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# singleton
eventbus = EventEmitter(sync_queue_size=20, pause=0.05)


# circular import
from .bus import Server, Transport  # noqa: E402


async def serve(
    transport: Transport, authenticate: Callable[[str], Awaitable[str | None]], param, timeout=WS_TIMEOUT
) -> None:
    # won't return until the connection is closed
    server = Server(transport=transport, authenticate=authenticate, param=param, timeout=timeout)
    logger.info(f"+++++ client connection {param.get('client')}")
    await server.run()
    logger.info(f"----- client connection {param.get('client_addr') or param.get('client')}")


def tree_id(addr: Addr) -> str:
    """Return tree_id from address."""
    try:
        return addr.split(".")[0]
    except IndexError:
        return addr


def branch_id(addr: Addr) -> str:
    """Return tree_id from address."""
    try:
        return addr.split(".")[1]
    except IndexError:
        return addr
