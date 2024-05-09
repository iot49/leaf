# https://github.com/tom-draper/api-analytics

from collections import deque

from eventbus import Event, EventBus, event_type, post, subscribe


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
