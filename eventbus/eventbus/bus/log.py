# https://github.com/tom-draper/api-analytics

import logging
from collections import deque

from eventbus import Event, EventBus, event_type, post, subscribe


class Log(EventBus):
    """Keep event history"""

    def __init__(self, size=100):
        self.history = deque((), size)
        subscribe(self)

    async def post(self, event: Event) -> None:
        tp = event.get("type")
        if tp == event_type.LOG:
            if event.get("levelno", 0) >= logging.ERROR:
                self.history.appendleft(event)  # type: ignore
            print(event.get("levelname"), event.get("name"), event.get("message"))
        elif tp == event_type.GET_LOG:
            history = self.history
            dst = event["src"]
            for i in range(len(history)):
                ev = history.popleft()
                history.append(ev)
                ev["dst"] = dst
                await post(ev)
