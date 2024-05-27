import asyncio
import json
import logging
import time

import esp32  # type: ignore
import ntptime  # type: ignore

from eventbus import EventBus, event_type, subscribe

from . import (
    DOMAIN,
    branch_id,
    config,
    led,
    ota,  # noqa: F401
    secrets,
    tree_id,
)
from .gateway import Gateway  # type: ignore
from .wifi import wifi

logger = logging.getLogger(__name__)


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
            logger.info(f"Updating certs: {event}")


async def main_task(ws_url):
    async with wifi:
        led.pattern = led.GREEN_BLINK_FAST
        ntptime.settime()
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        logger.info(f"Time set to {t}")

        # event listener
        _ = UpdateListener()

        # load plugins
        plugins = config.get(f"trees/{tree_id}/branches/{branch_id}/plugins", {})
        for mod, param in plugins.items():
            try:
                m = __import__(mod, None, None, (), 0)
                if "init" in m.__dict__:
                    if isinstance(m.init, type(main_task)):
                        asyncio.create_task(m.init(**(param or {})))
                    else:
                        m.init(**(param or {}))
                logger.info(f"Loaded plugin {mod} with {param}")
            except ImportError as e:
                logger.error(f"import {mod}: {e}")

        # since we got here, we assume the app is working
        logger.debug("esp32.Partition.mark_app_valid_cancel_rollback()")
        esp32.Partition.mark_app_valid_cancel_rollback()

        # connect to earth
        gateway = Gateway()
        reconnect_delay = 1
        while True:
            await gateway.connnect(ws_url)
            logger.info("Disconnected")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(5, reconnect_delay * 2)


async def main(ws_url=f"wss://{DOMAIN}/gateway/ws", logging_level=logging.INFO):
    logger.setLevel(logging_level)
    logger.info("Starting main")
    asyncio.create_task(led.run())
    led.pattern = led.GREEN_BLINK_SLOW
    while True:
        try:
            await main_task(ws_url)
        except Exception as e:
            print("exception in main", e)
            logger.exception(f"??? main: {e}", exc_info=e)
        finally:
            asyncio.new_event_loop()
