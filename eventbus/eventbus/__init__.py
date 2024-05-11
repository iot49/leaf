import asyncio
from abc import abstractmethod
from typing import Awaitable, Callable

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


class EventBus:
    """EventBus interface."""

    @abstractmethod
    async def post(self, event: Event) -> None:
        """Post an event to this eventbus."""
        pass


async def post(event: Event) -> None:
    """Post event on all subscribers."""
    global _subscribers
    for subscriber in _subscribers:
        await subscriber.post(event)


def post_sync(event: Event) -> None:
    """Post event 'eventually'"""

    async def poster():
        await post(event)

    asyncio.create_task(poster())


# list of subscribers - call subscribe/unsubscribe to add/remove
_subscribers = []


def subscribe(bus: EventBus) -> None:
    """Subscribe to this eventbus."""
    global _subscribers
    _subscribers.append(bus)


def unsubscribe(bus: EventBus) -> None:
    """Unsubscribe from this eventbus."""
    if bus in _subscribers:
        _subscribers.remove(bus)


# circular import
from .bus import Server, Transport  # noqa: E402


async def serve(
    transport: Transport, addr_filter: Callable[[str], bool], authenticate: Callable[[str], Awaitable[bool]], param
) -> None:
    # won't return until the connection is closed
    server = Server(transport=transport, addr_filter=addr_filter, authenticate=authenticate, param=param)
    await server.run()
