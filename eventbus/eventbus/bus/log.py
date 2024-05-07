# https://github.com/tom-draper/api-analytics

import logging
from collections import deque

from eventbus import Event, EventBus, event_type, post, post_sync, subscribe
from eventbus.event import EPOCH_OFFSET, log_event


class Log(EventBus):
    """Keep event history"""

    def __init__(self, size=100):
        self.history = deque((), size)
        subscribe(self)

    async def post(self, event: Event) -> None:
        tp = event["type"]
        if tp == event_type.LOG:
            self.history.appendleft(event)  # type: ignore
            print(event["levelname"], event["name"], event["message"])
        elif tp == event_type.GET_LOG:
            history = self.history
            dst = event["src"]
            for i in range(len(history)):
                ev = history.popleft()
                history.append(ev)
                ev["dst"] = dst
                await post(ev)


def configure_logging():
    class LogHandler(logging.Handler):
        def emit(self, record):
            event = log_event(
                levelname=record.levelname,
                timestamp=record.ct + EPOCH_OFFSET,  # type: ignore
                name=record.name,
                message=record.message,
            )
            post_sync(event)
            print("LogHandler", event["levelname"], event["name"], event["message"])

    root_logger = logging.getLogger()
    # remove default handler
    root_logger.handlers = []
    root_logger.addHandler(LogHandler())


# configure()
