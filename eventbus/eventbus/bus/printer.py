import time

from eventbus import event_type

from .. import Event, EventBus


class Printer(EventBus):
    """Print events to the console."""

    def __init__(self, report_pong=False):
        from .. import subscribe

        super().__init__()
        self.start_time = None
        self.report_pong = report_pong
        subscribe(self)

    async def post(self, event: Event) -> None:
        self.start_time = self.start_time or time.time_ns()
        if self.report_pong or event.get("type") != event_type.PONG:
            print(f"PRINT {event.get('type', '?'):12} {(time.time_ns()-self.start_time)/1e9:10.4f}", event)
