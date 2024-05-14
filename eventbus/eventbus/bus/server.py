import asyncio
import json
import logging
import time
from abc import abstractmethod
from typing import Any, Awaitable, Callable

try:
    from fastapi import WebSocketDisconnect
except ImportError:
    WebSocketDisconnect = Exception

from eventbus import event_type
from eventbus.event import get_auth

from .. import Event, EventBus, post, subscribe, unsubscribe
from ..event import bye_timeout, hello_already_connected, hello_connected, hello_invalid_token, pong, state

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
        self, *, transport: Transport, authenticate: Callable[[str], Awaitable[tuple[bool, str]]], param: dict
    ):
        """Create a Server instance.

        Args:
            transport (Transport): The transport object (e.g. websocket) used for communication.
            authenticate (Callable[[str], Awaitable[bool]]): The authentication function.
            param (dict, optional): The parameters to pass to the client. Defaults to {}.
        """

        self.closed = False
        self.transport = transport
        self.timeout = BUS_TIMEOUT
        self.authenticate = authenticate
        self.param = param
        self.param["timeout_interval"] = self.timeout

    async def run(self):
        """Returns when the connection is closed."""
        # send authentication request
        try:
            await self.transport.send_json(get_auth())
            event = await asyncio.wait_for(self.transport.receive_json(), timeout=self.timeout + 1)
            authenticated, client_addr = await self.authenticate(event.get("token"))
            if not authenticated:
                await self.transport.send_json(hello_invalid_token())
                return
            self.client_addr = client_addr
            self.gateway = not client_addr.startswith("@")
        except (RuntimeError, asyncio.TimeoutError):
            await self.transport.send_json(bye_timeout())
            return

        try:
            # update connections registry
            connection = Server.CONNECTIONS.get(self.client_addr)
            if connection and connection.get("connected"):
                await self.transport.send_json(hello_already_connected())
                return
            Server.CONNECTIONS[self.client_addr] = {
                "param": self.param,
                "connected_at": time.time(),
                "connected": True,
            }
            # ready for events
            subscribe(self)
            # send greeting
            await self.transport.send_json(hello_connected(self.param))
            # update gateway connection state
            if self.gateway:
                await post(state(eid=f"{self.client_addr}.gateway:status.connected", value=True))
            # won't return until the connection is closed
            await self.receiver_task()
        except RuntimeError:
            # client disconnected without sending BYE
            self.closed = True
        finally:
            unsubscribe(self)
            connection = Server.CONNECTIONS.get(self.client_addr) or {}
            connection["connected"] = False
            connection["disconnected_at"] = time.time()
            if self.gateway:
                await post(state(eid=f"{self.client_addr}.gateway:status.connected", value=False))
            else:
                # del Server.CONNECTIONS[self.client_addr]
                pass

    def addr_filter(self, dst: str) -> bool:
        if self.gateway:
            return dst == "#branches" or dst.startswith(self.client_addr)
        else:
            return dst in ("#clients", self.client_addr)

    async def post(self, event: Event) -> None:
        # forward event to client
        if self.closed:
            unsubscribe(self)
            return
        # address filter
        dst = event.get("dst", "")
        if self.addr_filter(dst):
            try:
                # TODO: batch send events as lists
                await self.transport.send_json(event)
            except RuntimeError as e:
                logger.error(f"Server.post: Transport error {e}")
                self.closed = True
        else:
            logger.debug(f"addr_filter skip type={event.get('type')} dst={dst} (client_addr={self.client_addr})")

    async def process_event(self, event: Event) -> None:
        et = event.get("type")
        if et is None:
            logger.error(f"Invalid event - no type (ignored) {event}")
            return
        if et == event_type.PING:
            await self.transport.send_json(pong)
        elif et == event_type.BYE:
            self.closed = True
        else:
            logger.debug(f"eventbus.bus.server got {event}")
            if "dst" in event:
                # TODO: firewall
                if not self.gateway:
                    event["src"] = self.client_addr
                await post(event)
            else:
                logger.error(f"Invalid event - no dst (ignored) {event}")

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
                await post(bye_timeout())
                self.closed = True
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON {e}")
                self.closed = True
            except WebSocketDisconnect as e:
                logger.error(f"WebSocketDisconnect {e}")
                self.closed = True
            except Exception as e:
                logger.exception(f"{type(e)} receiver_task {e}", exc_info=e)
                self.closed = True
        try:
            await self.transport.close()
        except RuntimeError:
            # logger.error("RuntimeError closing transport")
            pass
        except Exception as e:
            logger.exception("Server Error closing transport", e)
