import asyncio

from .. import EventBus, event_type, subscribe
from ..eid import eid2lid
from ..event import State


class Counter(EventBus):
    """Resettable counter"""

    def __init__(self, eid: str, interval: float = 0.1, N: int = -1):
        """
        Initialize a Counter object.

        Args:
            eid (str): The identifier for the counter.
            interval (float, optional): The interval between counter updates. Defaults to 0.1 seconds.
            N (int, optional): The maximum number of counter updates. Defaults to -1 (unlimited).

        Example:
            counter = Counter("counter1", interval=1, N=10)
            asyncio.create_task(counter.counter_task())
        """
        super().__init__()
        # TODO: delete 10x
        self.interval = 10 * interval
        self.N = N
        self.state = State(eid)
        self.count = 0
        # Subscribe to the bus to receive StateAction events
        subscribe(self)

    async def counter_task(self):
        N = self.N
        state = self.state
        n = 0
        while n < N or N == -1:
            await state.update(self.count)
            self.count += 1
            n += 1
            await asyncio.sleep(self.interval)

    async def post(self, event):
        # Called by bus when an event is posted
        if event["type"] == event_type.STATE_ACTION:
            if event.get("eid") == eid2lid(self.state.eid) and event["action"] == "reset":
                self.count = 0
                await self.state.update(0)
