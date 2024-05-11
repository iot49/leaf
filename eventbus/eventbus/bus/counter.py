import asyncio

from .. import EventBus, event_type, post, subscribe
from ..eid import eid2lid
from ..event import state, state_update


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
        self.interval = interval
        self.N = N
        self.state = state(eid=eid, value=0)
        # Subscribe to the bus to receive StateAction events
        subscribe(self)

    async def counter_task(self):
        N = self.N
        state = self.state
        n = 0
        while n < N or N == -1:
            state_update(state, value=state["value"] + 1)
            # post the event to the bus
            await post(state)
            await asyncio.sleep(self.interval)
            n += 1

    async def post(self, event):
        # Called by bus when an event is posted
        if event["type"] == event_type.STATE_ACTION:
            if event["lid"] == eid2lid(self.state["eid"]) and event["action"] == "reset":
                state_update(self.state, value=0)
                await post(self.state)
