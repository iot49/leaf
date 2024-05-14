import asyncio
import json
import logging
import os

import aiohttp

from eventbus import Event, EventBus, event_type, post, subscribe, unsubscribe
from eventbus.event import get_cert, get_config, get_log, get_secrets, get_state, ping

from . import CERT_DIR, DOMAIN, SSL, config, secrets
from .wifi import wifi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Gateway(EventBus):
    def __init__(self):
        self.connected = False

    async def connnect(self) -> str:
        """Connect to earth. Returns when the connection is closed.

        Returns:
            str: disconnect reason.
        """
        async with wifi:
            try:
                async with aiohttp.ClientSession() as session:
                    # connect to websocket
                    scheme = "wss" if SSL else "ws"
                    url = f"{scheme}://{DOMAIN}/gateway/ws"
                    gateway_token = secrets["gateway-token"]
                    async with session.ws_connect(url) as ws:
                        self.connected = True
                        msg = await self._connection(ws, gateway_token)
                    unsubscribe(self)
                    return msg
            except Exception as e:
                logger.error(f"connect error: {e}")
                return "server unreachable"
            finally:
                self.connected = False

    async def _connection(self, ws, gateway_token) -> str:
        """Handle connection to earth.
        Returns when the connection is closed.
            str: disconnect reason.
        """
        auth_msg = await ws.receive_json()
        logger.debug(f"Authenticated - {auth_msg}")
        if auth_msg["type"] == event_type.GET_AUTH:
            await ws.send_json({"type": event_type.PUT_AUTH, "token": gateway_token})
        hello_msg = await ws.receive_json()
        if hello_msg["type"] == event_type.HELLO_CONNECTED:
            # send pings and receive messages
            self._ws = ws
            tasks = [
                self._ping_task(hello_msg["param"]["timeout_interval"]),
                self._receiver_task(),
                self._update_task(hello_msg["param"]["versions"]),
            ]
            subscribe(self)
            logger.info(f"Connected - {hello_msg}")
            await asyncio.gather(*tasks, return_exceptions=True)
            return "connection closed"
        else:
            return f"connection failed: {hello_msg}"

    async def _ping_task(self, interval):
        ws = self._ws
        while self.connected:
            # errors handled in connect_task by gather
            await ws.send_json(ping)
            await asyncio.sleep(interval)

    async def _receiver_task(self):
        ws = self._ws
        # update config & get current state, log
        await ws.send_json(get_state())
        await ws.send_json(get_log())

        # wait for messages
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                logger.debug(f"received msg-type={msg.type}: {str(msg.data)}")
                await post(json.loads(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"receiver_task: ws returned error {msg}")
                self.connected = False
                return

    async def _update_task(self, versions):
        # config and secrets
        if versions.get("config") != config.get("version"):
            await self.post(get_config())
        if versions.get("secrets") != secrets.get("version"):
            await self.post(get_secrets())

        # certificates
        version = ""
        version_file = f"{CERT_DIR}/version"
        if os.path.isfile(version_file):
            with open(version_file) as f:
                version = f.read().strip()
        if versions.get("certificates", "") != version:
            # update certificates
            await self.post(get_cert())

    async def post(self, event: Event) -> None:
        dst = event.get("dst")
        if dst in ("#clients", "#earth"):
            logger.debug(f"sending {event}")
            await self._ws.send_json(event)
