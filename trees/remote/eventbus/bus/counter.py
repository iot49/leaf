import asyncio

from .. import event_type, eventbus
from ..event import State


class Counter:
    """Resettable counter"""

    def __init__(self, eid: str, interval: float = 5, max_count: int = -1):
        """
        Initialize a Counter object.

        Args:
            eid (str): The identifier for the counter.
            interval (float, optional): The interval between counter updates.
            max_count (int, optional): The maximum number of counter updates. Defaults to -1 (unlimited).

        Example:
            counter = Counter("counter1", interval=1, N=10)
        """
        super().__init__()
        self.interval = interval
        self.max_count = max_count
        self.state = State(eid)
        self.count = 0

        @eventbus.on(event_type.STATE_ACTION)
        async def reset_action(eid, action, **event):
            if eid == self.state.eid and action == "reset":
                self.count = 0
                await self.state.update(0)

    async def counter_task(self):
        N = self.max_count
        state = self.state
        n = 0
        while n < N or N == -1:
            await state.update(self.count)
            self.count += 1
            n += 1
            await asyncio.sleep(self.interval)
