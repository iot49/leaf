import time

from eventbus import event_type

from .. import Event, EventBus


class Printer(EventBus):
    """Print events to the console."""

    def __init__(self, exclude=[event_type.PONG, event_type.LOG]):
        from .. import subscribe

        super().__init__()
        self.start_time = None
        self.excludes = exclude
        subscribe(self)

    async def post(self, event: Event) -> None:
        tp = event.get("type")
        if tp not in self.excludes:
            self.start_time = self.start_time or time.time_ns()
            print(f"PRINT {event.get('type', '?'):12} {(time.time_ns()-self.start_time)/1e9:10.4f}", event)
