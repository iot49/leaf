import time

from . import SRC_ADDR, event_type
from .eid import eid2addr, eid2eid, eid2lid

"""
Events are dicts communicated by EventBus.

The following fields are mandatory:

- et: event type (and int defined in event_type.py)
- src: source address (str)
- dst: destination address (str)

All other fields are specific to the event type. To keep
things organized, events should not be created ad-hoc.
This file defines a set of functions to create events for
an application. For other purposes, it should be modified
or extended.
"""

# MicroPython time starts from 2000-01-01 on some ports
EPOCH_OFFSET = 946684800 if time.gmtime(0)[0] == 2000 else 0


def make_event(type, dst, **args):
    args["type"] = type
    args["dst"] = dst
    args["src"] = SRC_ADDR
    return args


# connection keep-alive
ping = {"type": event_type.PING}
pong = {"type": event_type.PONG}

# authentication
get_auth = {"type": event_type.GET_AUTH, "src": SRC_ADDR}
put_auth = {"type": event_type.PUT_AUTH}

# states
get_state = {"type": event_type.GET_STATE, "dst": "#server", "src": SRC_ADDR}
get_config = {"type": event_type.GET_CONFIG, "dst": "#server", "src": SRC_ADDR}
get_log = {"type": event_type.GET_LOG, "dst": "#server", "src": SRC_ADDR}


def put_config(data: dict, dst: str = "#server"):
    return make_event(event_type.PUT_CONFIG, dst, data=data)


def update_config(data: dict, dst: str = "#branches"):
    return make_event(event_type.UPDATE_CONFIG, dst, data=data)


# connection management
def hello_connected(peer: str, param: dict):
    return make_event(event_type.HELLO_CONNECTED, peer, param=param)


hello_no_token = {"type": event_type.HELLO_NO_TOKEN, "src": SRC_ADDR}
hello_invalid_token = {"type": event_type.HELLO_INVALID_TOKEN, "src": SRC_ADDR}
hello_already_connected = {"type": event_type.HELLO_ALREADY_CONNECTED, "src": SRC_ADDR}

bye = {"type": event_type.BYE, "src": SRC_ADDR}
bye_timeout = {"type": event_type.BYE_TIMEOUT, "src": SRC_ADDR}


# state & actions
def state(eid: str, value, dst="#clients", timestamp: float = time.time() + EPOCH_OFFSET):
    return make_event(event_type.STATE, dst, eid=eid2eid(eid), value=value, timestamp=timestamp)


def state_update(state: dict, value):
    state["value"] = value
    state["timestamp"] = time.time() + EPOCH_OFFSET
    return state


def state_action(state: dict, action: str, param=None):
    eid = state["eid"]
    return make_event(event_type.STATE_ACTION, dst=eid2addr(eid), lid=eid2lid(eid), action=action, param=param)


# logging
def log_event(**event):
    return make_event(event_type.LOG, "#clients", **event)
