import asyncio

from eventbus import event_type
from eventbus.bus import CurrentState, Printer
from eventbus.eid import eid2lid
from eventbus.event import get_state, state, state_action, state_update
from eventbus.eventbus import EventBus, post, subscribe


class Counter(EventBus):
    """Resettable counter"""

    def __init__(self, eid: str, interval: float = 0.1, N: int = 10):
        super().__init__()
        self.interval = interval
        self.N = N
        self.state = state(eid=eid, value=0)
        # Subscribe to the bus to receive StateAction events
        subscribe(self)

    async def _count_task(self):
        state = self.state
        for _ in range(self.N):
            state_update(state, value=state["value"] + 1)
            # post the event to the bus
            await post(state)
            await asyncio.sleep(self.interval)

    async def post(self, event):
        # Called by bus when an event is posted
        if event["type"] == event_type.STATE_ACTION:
            lid = eid2lid(self.state["eid"])
            if event["lid"] == lid and event["action"] == "reset":
                # reset counter and post its new value
                state_update(self.state, value=0)
                await self.post(self.state)


async def main():
    async def reset_task():
        for i in range(3):
            await asyncio.sleep(0.35)
            await post(state_action(counter1.state, "reset", param=i))

    async def current_state_task():
        for i in range(3):
            await asyncio.sleep(0.7)
            await post(get_state)

    CurrentState()
    Printer()
    counter1 = Counter("counter1:count", interval=0.10)
    counter2 = Counter("counter2:count", interval=0.17)
    await asyncio.gather(counter1._count_task(), counter2._count_task(), reset_task(), current_state_task())
