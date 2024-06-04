import asyncio
import time

from eventbus.event import State, get_src_addr
from eventbus.singleton import singleton

from .. import eventbus


@singleton
class Reflect:
    """Resettable counter"""

    def __init__(self, interval: float = 0):
        super().__init__()
        self.interval = interval

        @eventbus.on("reflect?")
        async def reflect_echo(
            type,
            src,
            dst,
            timestamp,
            id,
        ):
            if src == get_src_addr():
                return
            await eventbus.emit(
                {"type": "reflect!", "timestamp": timestamp, "src": get_src_addr(), "dst": src, "id": id}
            )

        @eventbus.on("reflect!")
        async def reflect_get(
            type,
            src,
            dst,
            timestamp,
            id,
        ):
            if not id.startswith(get_src_addr()):
                return
            dt = time.time_ns() - timestamp
            dt = dt / 1e6
            s = State(f"reflect.{src}")
            await s.update(dt)

    async def emitter_task(self):
        if self.interval < 1e-3:
            return
        seq = 1
        while True:
            event = {
                "type": "reflect?",
                "timestamp": time.time_ns(),
                "src": get_src_addr(),
                "dst": "#clients",
                "id": f"{get_src_addr()}:{seq}",
            }
            seq += 1
            await eventbus.emit(event)
            event["dst"] = "#branches"
            await eventbus.emit(event)
            await asyncio.sleep(self.interval)
