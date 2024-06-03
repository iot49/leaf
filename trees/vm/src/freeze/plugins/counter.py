import asyncio

from eventbus.bus import Counter


async def init(eid: str, interval: float = 1, N: int = 1000):
    asyncio.create_task(Counter(eid, interval=interval)._counter_task())
