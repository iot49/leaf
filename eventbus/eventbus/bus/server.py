import asyncio
import logging
import time
from abc import abstractmethod
from typing import Any, Awaitable, Callable

from eventbus import SRC_ADDR, event_type
from eventbus.event import get_auth

from .. import Event, EventBus, post, subscribe, unsubscribe
from ..event import bye_timeout, hello_already_connected, hello_connected, hello_invalid_token, state

logger = logging.getLogger(__name__)

BUS_TIMEOUT = 5  # disconnect if no message received [seconds]


class Transport:
    @abstractmethod
    async def send_json(self, data: Any) -> None:
        pass

    @abstractmethod
    async def receive_json(self) -> Any:
        pass

    @abstractmethod
    async def close(self) -> Any:
        pass


class Server(EventBus):
    CONNECTIONS = {}

    def __init__(
        self,
        *,
        transport: Transport,
        addr_filter: Callable[[str], bool],
        authenticate: Callable[[str], Awaitable[bool]],
        param: dict = {},
    ):
        """Create a Server instance.

        Args:
            transport (Transport): The transport object (e.g. websocket) used for communication.
            bridge (Bridge): The bridge object used for message routing.
            addr_filter ((str, ) -> bool): The address filter used to route messages to this client.
                Messages addressed to this client are always accepted.
            timeout (float, optional): The timeout in seconds. Longer silence results in disconnect.
                Typically clients will send a ping message to keep the connection alive. The
                server responds with pong.
        """

        self.transport = transport
        self.timeout = BUS_TIMEOUT
        self.closed = False
        self.addr_filter = addr_filter
        self.authenticate = authenticate
        self.param = param
        self.param["timeout_interval"] = self.timeout

    async def run(self):
        """Returns when the connection is closed."""

        # send authentication request
        try:
            await self.transport.send_json(get_auth)
            event = await asyncio.wait_for(self.transport.receive_json(), timeout=self.timeout + 1)
            if not await self.authenticate(event.get("token")):
                await self.transport.send_json(hello_invalid_token)
                return
        except (RuntimeError, asyncio.TimeoutError):
            print("Server.run: Timeout waiting for token")
            await self.transport.send_json(bye_timeout)
            return

        try:
            # update connections registry
            peer = self.param["peer"]
            if peer in Server.CONNECTIONS and Server.CONNECTIONS[peer]["connected"]:
                await self.transport.send_json(hello_already_connected)
                return
            Server.CONNECTIONS[peer] = {
                "param": self.param,
                "connected_at": time.time(),
            }
            # ready for events
            subscribe(self)
            # send greeting
            await self.transport.send_json(hello_connected(peer, self.param))
            # update gateway connection state
            if self.param["gateway"]:
                await post(state(eid=f"{self.param['peer']}:gateway:status:connected", value=True))
            # won't return until the connection is closed
            await self.receiver_task()
        finally:
            unsubscribe(self)
            self.param["disconnected_at"] = time.time()
            self.param["connected"] = False
            Server.CONNECTIONS[self.param["peer"]] = self.param
            if self.param["gateway"]:
                await post(state(eid=f"{self.param['peer']}:gateway:status:connected", value=False))

    async def post(self, event: Event) -> None:
        # TODO: batch send events as lists
        if self.closed:
            unsubscribe(self)
            return
        # address filter
        dst = event.get("dst", "")
        if self.addr_filter(dst):
            try:
                await self.transport.send_json(event)
            except RuntimeError as e:
                logger.error(f"Server.post: Transport error {e}")
                self.closed = True
        else:
            logger.debug(f"addr_filter skip peer={self.param['peer']} dst={dst})")

    async def process_event(self, event: Event) -> None:
        et = event.get("type")
        if et != "ping":
            logger.debug(f"eventbus.bus.server got {event}")
        if et is None:
            logger.error(f"Invalid event - no type (ignored) {event}")
            return
        if et == event_type.PING:
            await self.post({"type": event_type.PONG, "src": SRC_ADDR, "dst": f"{self.param['peer']}"})
        elif et == event_type.BYE:
            self.closed = True
        else:
            if "src" in event and "dst" in event:
                await post(event)
            else:
                logger.error(f"Invalid event - no src/dst (ignored) {event}")

    async def receiver_task(self):
        while not self.closed:
            try:
                event = await asyncio.wait_for(self.transport.receive_json(), timeout=self.timeout + 1)
                if isinstance(event, list):
                    for e in event:
                        await self.process_event(e)
                else:
                    await self.process_event(event)
            except asyncio.TimeoutError:
                logger.debug(f"Timeout {self.param}")
                await post(bye_timeout)
                self.closed = True
            except Exception as e:
                logger.error(f"unspecified error in receiver_task {e}")
                self.closed = True
        try:
            await self.transport.close()
        except RuntimeError as e:
            logger.exception("RuntimeError closing transport", e)
        except Exception as e:
            logger.exception("Server Error closing transport", e)
