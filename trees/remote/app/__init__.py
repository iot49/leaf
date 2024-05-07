import logging
import time

import ads1x15
import ina3221
import ntptime

from eventbus.bus import Config, Counter, CurrentState, Log, configure_logging

config = Config(config_file="/config.json")
state = CurrentState()

# needs config
from .wifi import wifi  # noqa: E402, F401


async def main():
    Log()
    configure_logging()
    logger = logging.getLogger(__name__)

    async with wifi:
        logger.info(f"Connected to wifi @ {wifi.ip}")
        logger.critical(f"Connected to wifi @ {wifi.ip}")
        ntptime.settime()
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        logger.info(f"Time set to {t}")

        # plugins
        Counter("counter.count")
