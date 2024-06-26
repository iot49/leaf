import time

from . import Addr, event_type, eventbus
from .eid import eid2addr, eid2eid

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
_SRC_ADDR: Addr = "#earth"


# MicroPython time starts from 2000-01-01 on some ports
EPOCH_OFFSET = 946684800 if time.gmtime(0)[0] == 2000 else 0


def set_src_addr(addr: Addr):
    global _SRC_ADDR
    _SRC_ADDR = addr


def get_src_addr():
    return _SRC_ADDR


def make_event(type, dst, **args):
    args["type"] = type
    args["dst"] = dst
    args["src"] = _SRC_ADDR
    return args


# connection keep-alive
ping = {"type": event_type.PING}
pong = {"type": event_type.PONG}


# authentication
def get_auth():
    return {"type": event_type.GET_AUTH, "src": "#server"}


def put_auth(get_auth, token: str):
    return make_event(event_type.PUT_AUTH, get_auth["src"], token=token)


# secrets
def get_secrets(dst="#earth"):
    return make_event(event_type.GET_SECRETS, dst)


def put_secrets(get_secrets, secrets: dict):
    # secrets are for trees only
    assert not get_secrets["src"].startswith("@")
    return make_event(event_type.PUT_SECRETS, get_secrets["src"], data=secrets)


# certificates
def get_cert():
    return make_event(event_type.GET_CERT, "#earth")


def put_cert(get_cert, cert: dict):
    # certificates are sensitive and for trees only
    assert not get_cert["src"].startswith("@")
    return make_event(event_type.PUT_CERT, get_cert["src"], data=cert)


# current values
def get_state(dst="#server"):
    return make_event(event_type.GET_STATE, dst)


def get_config(dst="#server"):
    return make_event(event_type.GET_CONFIG, dst)


def get_log(dst="#server"):
    return make_event(event_type.GET_LOG, dst)


def put_config(data: dict, dst: str = "#server"):
    return make_event(event_type.PUT_CONFIG, dst, data=data)


# connection management
def hello_connected(param: dict):
    return {"type": event_type.HELLO_CONNECTED, "param": param}


def hello_no_token():
    return {"type": event_type.HELLO_NO_TOKEN}


def hello_invalid_token():
    return {"type": event_type.HELLO_INVALID_TOKEN}


def hello_already_connected():
    return {"type": event_type.HELLO_ALREADY_CONNECTED}


def bye():
    return {"type": event_type.BYE}


def bye_timeout():
    return {"type": event_type.BYE_TIMEOUT}


# logging
def log_event(**event):
    return make_event(event_type.LOG, dst="#clients", **event)


# state & actions


class State:
    def __init__(self, eid: str, dst="#clients"):
        self._eid = eid2eid(eid)
        self._event = make_event(event_type.STATE, dst=dst, eid=self._eid, value=None, timestamp=None)

    @property
    def eid(self):
        return self._eid

    @property
    def event(self):
        return self._event

    async def update(self, value, timestamp: float = time.time() + EPOCH_OFFSET):
        ev = self._event
        ev["value"] = value
        ev["timestamp"] = timestamp
        await eventbus.emit(ev)
        return ev

    async def act(self, action: str, param=None):
        ev = make_event(event_type.STATE_ACTION, dst=eid2addr(self._eid), eid=self._eid, action=action, param=param)
        await eventbus.emit(ev)
        return ev

    def __repr__(self) -> str:
        return f"State({self._eid})"
