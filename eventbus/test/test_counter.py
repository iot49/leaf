import asyncio

from eventbus import event_type, eventbus
from eventbus.bus import Counter
from eventbus.event import State


async def test_counter():
    c = 0

    @eventbus.on(event_type.STATE)
    def count(type, eid, value, timestamp, src, dst):
        if eid != "#earth:counter.count":
            return
        nonlocal c
        assert type == event_type.STATE
        assert value == c % 4
        assert src == "#earth"
        assert dst == "#clients"
        c += 1

    counter = Counter("counter.count", interval=0, max_count=4)
    asyncio.create_task(counter.counter_task())
    await asyncio.sleep(0.01)

    s = State("counter.count")
    await s.act("reset")
    assert c == 5
