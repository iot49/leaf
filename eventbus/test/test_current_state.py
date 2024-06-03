import asyncio

from eventbus import event_type, eventbus
from eventbus.bus import CurrentState
from eventbus.event import State, get_state


async def test_current_state():
    asyncio.new_event_loop()
    states = []

    @eventbus.on(event_type.STATE)
    def s(value, **event):
        nonlocal states
        states.append(value)

    CurrentState()
    for i in range(3):
        x = State(f"a.b{i}")
        await x.update(i)

    assert states == list(range(3))
    states = []

    await eventbus.emit(get_state())
    await asyncio.sleep(0.1)
    assert states == list(range(3))
