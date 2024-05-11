import asyncio
import json
import logging

import aiohttp

import app
from eventbus import Event, EventBus, event_type, post, subscribe, unsubscribe
from eventbus.event import get_config, get_log, get_state, ping

from . import DOMAIN, SSL, secrets
from .wifi import wifi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Gateway(EventBus):
    def __init__(self):
        pass

    async def connnect(self):
        """Connect to earth. Returns when the connection is closed."""
        async with wifi:
            async with aiohttp.ClientSession() as session:
                scheme = "wss" if SSL else "ws"
                url = f"{scheme}://{DOMAIN}/gateway/ws"
                gateway_token = secrets["gateway-token"]
                # update secrets
                async with session.get(
                    f"http://{DOMAIN}/gateway/secrets",
                    headers={"Authorization": f"Bearer {gateway_token}"},
                ) as response:
                    if response.status == 200:
                        _secrets = await response.json()
                        if "gateway-token" in _secrets:
                            gateway_token = _secrets["gateway-token"]
                            with open("/secrets.json", "w") as f:
                                json.dump(_secrets, f)
                            app.secrets = _secrets  # type: ignore
                    else:
                        logger.error(f"Error updating secrets: {response.status}")
                async with session.ws_connect(url) as ws:
                    # get auth
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
                        ]
                        subscribe(self)
                        logger.info(f"Connected - {hello_msg}")
                        try:
                            await asyncio.gather(*tasks, return_exceptions=True)
                        except Exception as e:
                            logger.error(f"connect_task error: {e}")
                    else:
                        logger.error(f"Connection to earth failed: {hello_msg}")
                unsubscribe(self)

    async def _ping_task(self, interval):
        ws = self._ws
        while True:
            # errors handled in connect_task by gather
            await ws.send_json(ping)
            await asyncio.sleep(interval)

    async def _receiver_task(self):
        ws = self._ws
        # update config & get current state, log
        await ws.send_json(get_config())
        await ws.send_json(get_state())
        await ws.send_json(get_log())

        # wait for messages
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                logger.debug(f"received msg-type={msg.type}: {str(msg.data)}")
                await post(json.loads(msg.data))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.error(f"receiver_task: ws returned error {msg}")
                return

    async def post(self, event: Event) -> None:
        dst = event.get("dst")
        if dst in ("#clients", "#earth"):
            logger.debug(f"sending {event}")
            await self._ws.send_json(event)
