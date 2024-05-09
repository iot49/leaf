# ruff: noqa: E402, F401

import asyncio
import json
import logging
import sys
import time
from os.path import isfile

import aiohttp
import machine  # type: ignore

# bail if branch is not yet provisioned
if not isfile("/secrets.json") or not isfile("/config.json"):
    sys.exit(-1)


# logging must be configured before any actual logging
def configure_logging():
    class LogHandler(logging.Handler):
        def emit(self, record):
            from eventbus import post_sync
            from eventbus.event import log_event

            event = log_event(
                levelname=record.levelname,
                timestamp=record.ct + EPOCH_OFFSET,  # type: ignore
                name=record.name,
                message=record.message,
            )
            post_sync(event)
            print("LogHandler", event["levelname"], event["name"], event["message"])

    root_logger = logging.getLogger()
    # remove default handler
    root_logger.handlers = []
    root_logger.addHandler(LogHandler())


configure_logging()

# globals

logger = logging.getLogger(__name__)
EPOCH_OFFSET = 946684800 if time.gmtime(0)[0] == 2000 else 0
mac = ":".join("{:02x}".format(x) for x in machine.unique_id())

with open("/secrets.json") as f:
    secrets = json.load(f)

# configure eventbus SRC_ADDR before importing eventbus.event
from eventbus import SRC_ADDR

tree_id = secrets["tree"]["tree_id"]
for branch in secrets["tree"]["branches"]:
    if branch["mac"] == mac:
        branch_id = branch["branch_id"]
else:
    branch_id = "?"

SRC_ADDR = f"{tree_id}:{branch_id}"  # noqa: F811
DOMAIN = secrets["domain"]

# setup eventbus
from eventbus import event_type
from eventbus.bus import Config, Counter, CurrentState, Log
from eventbus.event import get_state, ping

# load config and current state
config = Config(config_file="/config.json")
state = CurrentState()
Log()

# after loading config
from .wifi import wifi
