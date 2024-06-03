import time

from eventbus import event_type, eventbus


class Printer:
    """Print events to the console."""

    def __init__(self, exclude=[event_type.PONG, event_type.LOG]):
        self.start_time = None
        self.excludes = exclude

        @eventbus.on("*")
        def ev(type, **event):
            if type not in self.excludes:
                self.start_time = self.start_time or time.time_ns()
                print(f"PRINT {event.get('type', '?'):12} {(time.time_ns()-self.start_time)/1e9:10.4f}", event)
