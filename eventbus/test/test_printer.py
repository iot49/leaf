from eventbus import eventbus
from eventbus.bus.printer import Printer
from eventbus.event import get_state


async def _test_printer():
    Printer()
    await eventbus.emit(get_state())

    # check stdout ...
