import asyncio

from httpx_ws import aconnect_ws

import eventbus
from eventbus.event import bye
from eventbus.event_type import GET_AUTH, HELLO_CONNECTED, PUT_AUTH

DEBUG = False


def dprint(*args):
    if DEBUG:
        print(*args)


def set_src(event, src):
    event["src"] = src
    return event


class EventQueue(eventbus.EventBus):
    def __init__(self):
        self.queue = asyncio.Queue()
        eventbus.subscribe(self)

    async def post(self, event):
        dprint("EARTH GOT", event)
        await self.queue.put(event)


async def yield_ws(async_websocket_client, token, url="ws"):
    """Yield a client/gatway ws."""
    dprint()
    async with aconnect_ws(url, async_websocket_client) as ws:
        # authenticate
        auth = await ws.receive_json()
        assert auth["type"] == GET_AUTH
        await ws.send_json({"type": PUT_AUTH, "token": token})
        # get the hello message
        hello = await ws.receive_json()
        dprint(">>>>>", hello)
        assert hello["type"] == HELLO_CONNECTED
        yield ws
        await ws.send_json(bye())
        dprint(f"<<<<< bye {hello['param']['client']}\n")
