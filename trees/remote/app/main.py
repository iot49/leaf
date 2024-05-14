import asyncio
import json
import logging
import time

import ntptime  # type: ignore

from eventbus import EventBus, event_type, subscribe

from . import branch_id, config, secrets, tree_id
from .gateway import Gateway  # type: ignore
from .wifi import wifi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UpdateListener(EventBus):
    def __init__(self):
        subscribe(self)

    async def post(self, event):
        tp = event.get("type")
        data = event.get("data", {})
        new_version = data.get("version")
        if tp == event_type.PUT_CONFIG and "wifi" in data:
            with open("/config.json", "w") as f:
                logger.info(f"Updating config from {config.get('version')} --> {new_version}")
                f.write(json.dumps(data))
        elif tp == event_type.PUT_SECRETS and "gateway-token" in data:
            with open("/secrets.json", "w") as f:
                logger.info(f"Updating secrets from {secrets.get('version')} --> {new_version}")
                f.write(json.dumps(data))
        elif tp == event_type.PUT_CERT:
            logger.info(f"GOT certs: {event}")


async def main_task():
    async with wifi:
        ntptime.settime()
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        logger.info(f"Time set to {t}")

        # event listener
        _ = UpdateListener()

        # load plugins
        plugins = config.get(f"trees/{tree_id}/branches/{branch_id}/plugins", {})
        for mod, param in plugins.items():
            m = __import__(mod, None, None, (), 0)
            if "init" in m.__dict__:
                await m.init(**(param or {}))
            logger.info(f"Loaded plugin {mod} with {param}")

        # connect to earth
        gateway = Gateway()
        reconnect_delay = 10
        while True:
            msg = await gateway.connnect()
            logger.info(f"Disconnected: {msg}")
            if msg == "server unreachable":
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(600, reconnect_delay * 2)
            else:
                reconnect_delay = 10


async def main():
    logger.info("Starting main")
    while True:
        try:
            await main_task()
        except Exception as e:
            logger.exception(f"??? main: {e}", exc_info=e)
        finally:
            asyncio.new_event_loop()
