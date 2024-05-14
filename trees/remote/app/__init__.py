# ruff: noqa: E402, F401

import json
import logging
import sys
import time
from os.path import isfile

import machine  # type: ignore

from eventbus.bus import Config, CurrentState, Log
from eventbus.event import set_src_addr

EPOCH_OFFSET = 946684800 if time.gmtime(0)[0] == 2000 else 0

# use test server
TESTING = True
TEST_DOMAIN = "192.168.8.138:8001"
SSL = not TESTING

CERT_DIR = "/certs"

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
            # print(event["levelname"], event["name"], event["message"])

    root_logger = logging.getLogger()
    # remove default handler
    root_logger.handlers = []
    root_logger.addHandler(LogHandler())


configure_logging()
logger = logging.getLogger(__name__)
Log()

# globals

mac = ":".join("{:02x}".format(x) for x in machine.unique_id())

with open("/secrets.json") as f:
    try:
        secrets = json.load(f)
    except ValueError:
        logger.error("Invalid secrets.json")
        sys.exit(-1)


tree_id = secrets["tree"]["tree_id"]
branch_id = "?"
for branch in secrets["tree"]["branches"]:
    if branch["mac"] == mac:
        branch_id = branch["branch_id"]
        break

set_src_addr(f"{tree_id}:{branch_id}")  # noqa: F811

DOMAIN = TEST_DOMAIN if TESTING else secrets["domain"]

# load config and current state
config = Config(config_file="/config.json")
state = CurrentState()


# after loading config
from .main import main
from .wifi import wifi
