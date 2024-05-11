import asyncio
import logging
import time

import ntptime  # type: ignore

from . import branch_id, config, tree_id
from .gateway import Gateway  # type: ignore
from .wifi import wifi

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def main_task():
    async with wifi:
        ntptime.settime()
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        logger.info(f"Time set to {t}")

        # load plugins

        plugins = config.get(f"trees/{tree_id}/branches/{branch_id}/plugins", {})
        for mod, param in plugins.items():
            m = __import__(mod, None, None, (), 0)
            if "init" in m.__dict__:
                await m.init(**(param or {}))
            logger.info(f"Loaded plugin {mod} with {param}")

        # connect to earth
        gateway = Gateway()
        for i in range(3):
            try:
                await gateway.connnect()
            except OSError as e:
                logger.exception(f"OSError: {e}, reconnecting...", exc_info=e)
            except Exception as e:
                logger.exception(f"??? gateway connection: {e}, reconnecting...", exc_info=e)


async def main():
    logger.info("Starting main")
    while True:
        try:
            await main_task()
        except Exception as e:
            logger.exception(f"??? main: {e}", exc_info=e)
        finally:
            asyncio.new_event_loop()
