from eventbus import event_type, eventbus
from eventbus.bus import Log
from eventbus.event import get_log, log_event


async def test_current_state():
    rec = []
    proto = []

    @eventbus.on(event_type.LOG)
    def lh(**event):
        rec.append(event)

    Log()
    for i in range(3):
        lg = log_event(message=f"test {i}", levelno=10, levelname="INFO", src="test", name="name", funcName="func")
        await eventbus.emit(lg)
        proto.append(lg)

    await eventbus.emit(get_log())
    assert rec == proto
