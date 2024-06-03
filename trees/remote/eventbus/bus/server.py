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

from .. import Event, eventbus
from ..event import (
    State,
    bye_timeout,
    get_log,
    get_state,
    hello_already_connected,
    hello_connected,
    hello_invalid_token,
    pong,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

WS_TIMEOUT = 5  # disconnect if no message received [seconds]


class Transport:
    @abstractmethod
    async def send_json(self, data: Any) -> None:
        pass

    @abstractmethod
    async def receive_json(self) -> Any:
        pass


class Server:
    CONNECTIONS = {}

    def __init__(
        self, *, transport: Transport, authenticate: Callable[[str], Awaitable[str | None]], param: dict, timeout
    ):
        """Create a Server instance.

        Args:
            transport (Transport): The transport object (e.g. websocket) used for communication.
            authenticate (Callable[[str], Awaitable[str | None]]): The authentication function.
                Returns client address or None if authentication fails.
            param (dict, optional): The parameters to pass to the client. Defaults to {}.
        """

        self.closed = False
        self.transport = transport
        self.timeout = timeout
        self.authenticate = authenticate
        self.param = param
        self.param["timeout_interval"] = self.timeout

    async def run(self):
        """Returns when the connection is closed."""
        # send authentication request
        try:
            await self.transport.send_json(get_auth())
            event = await asyncio.wait_for(self.transport.receive_json(), timeout=self.timeout + 1)
            if event is None or event.get("type") != event_type.PUT_AUTH:
                logger.error(f"??? get_auth received invalid response: {event}")
                return
            self.param["client_addr"] = client_addr = await self.authenticate(event.get("token"))
            if not client_addr:
                logger.error(f"{self.param.get('client')}: authentication failed with {event}")
                await self.transport.send_json(hello_invalid_token())
                return
            self.gateway = not client_addr.startswith("@")
        except (WebSocketDisconnect, RuntimeError, asyncio.TimeoutError) as e:
            logger.exception(f"handshake failed: {e} {self.param}", exc_info=e)
            self.closed = True
            await self.transport.send_json(bye_timeout())
            return

        connect_event = State(eid=f"{client_addr}.gateway:status.connected")
        try:
            # update connections registry
            connection = Server.CONNECTIONS.get(client_addr)
            if connection and connection.get("connected"):
                await self.transport.send_json(hello_already_connected())
                return
            Server.CONNECTIONS[client_addr] = {
                "param": self.param,
                "connected_at": time.time(),
                "connected": True,
            }
            # send greeting
            await self.transport.send_json(hello_connected(self.param))
            # ready for events
            logger.debug(f"listening for events from {client_addr}")
            self.sender()
            # update gateway connection state
            if self.gateway:
                await connect_event.update(True)
                await eventbus.emit(get_state(dst=client_addr))
                await eventbus.emit(get_log(dst=client_addr))
            # won't return until the connection is closed
            await self.receiver_task()
        except RuntimeError:
            # client disconnected without sending BYE
            self.closed = True
        finally:
            connection = Server.CONNECTIONS.get(client_addr) or {}
            connection["connected"] = False
            connection["disconnected_at"] = time.time()
            if self.gateway:
                await connect_event.update(False)
            else:
                del Server.CONNECTIONS[self.param.get("client_addr")]
                pass

    def addr_filter(self, dst: str) -> bool:
        client_addr = self.param["client_addr"]
        if self.gateway:
            return dst == "#branches" or dst.startswith(client_addr)
        else:
            return dst in ("#clients", client_addr)

    def sender(self):
        @eventbus.on("*")
        async def all_events(**event):
            nonlocal self
            # forward event to client
            if self.closed:
                # no more events, please ...
                print(f"Server.sender: off {self.param}")
                eventbus.off(all_events)
                return
            # address filter
            dst = event.get("dst", "")
            if self.addr_filter(dst):
                try:
                    # TODO: batch send events as lists
                    print(f"Server.sender: -> {self.param.get('client_addr')}: {event}")
                    await self.transport.send_json(event)
                except (RuntimeError, Exception) as e:
                    logger.error(f"Server.sender: Transport error {type(e)} {e}")
                    self.closed = True
            else:
                pass
                # logger.debug(f"addr_filter not posted: type={event.get('type')} dst={dst} (client_addr={self.param.get("client_addr")})")

    async def process_event(self, event: Event) -> None:
        et = event.get("type")
        if et is None:
            logger.error(f"Invalid event - no type (ignored) {event}")
            return
        if et == event_type.PING:
            await self.transport.send_json(pong)
        elif et == event_type.BYE:
            logger.debug("got bye, closing connection")
            self.closed = True
        else:
            logger.debug(f"From {self.param.get('client_addr')}: {event}")
            if "dst" in event:
                if not self.gateway:
                    event["src"] = self.param["client_addr"]
                await eventbus.emit(event)
            else:
                logger.error(f"Invalid event - no dst (ignored) {event}")

    async def receiver_task(self):
        while not self.closed:
            try:
                event = await asyncio.wait_for(self.transport.receive_json(), timeout=self.timeout + 100)
                if isinstance(event, list):
                    for e in event:
                        await self.process_event(e)
                else:
                    await self.process_event(event)
            except asyncio.TimeoutError:
                logger.debug(f"Timeout {self.param}")
                await eventbus.emit(bye_timeout())
                self.closed = True
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON {e}")
            except WebSocketDisconnect as e:
                logger.debug(f"WebSocketDisconnect {e}")
                self.closed = True
            except Exception as e:
                logger.exception(e, exc_info=e)
                self.closed = True
