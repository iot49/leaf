# https://github.com/tom-draper/api-analytics

import logging
import time
from collections import deque

from eventbus import Event, EventBus, event_type, post, subscribe

BLUE = "\x1b[38;5;4m"
GREEN = "\x1b[38;5;2m"
YELLOW = "\x1b[38;5;3m"
RED = "\x1b[38;5;1m"
MAGENTA = "\x1b[38;5;5m"

RESET = "\x1b[0m"


class Log(EventBus):
    """Keep event history"""

    def __init__(self, size=100):
        self.history = deque((), size)
        subscribe(self)

    async def post(self, event: Event) -> None:
        tp = event.get("type")
        if tp == event_type.LOG:
            levelno = event.get("levelno", 0)
            if levelno >= logging.ERROR:
                self.history.appendleft(event)  # type: ignore
            colors = {
                logging.DEBUG: BLUE,
                logging.INFO: GREEN,
                logging.WARNING: YELLOW,
                logging.ERROR: RED,
                logging.CRITICAL: MAGENTA,
            }
            color = colors.get(levelno, "")
            funcName = event.get("funcName") or ""
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(event.get("ct", 0)))  # type: ignore
            print(
                f"{t} {color}{event.get('levelname'):9}{RESET} {event.get('src'):12} {event.get('name'):20} {funcName:16} {event.get('message')}"
            )
            tb = event.get("traceback")
            if tb is not None:
                print(tb)
        elif tp == event_type.GET_LOG:
            history = self.history
            dst = event["src"]
            for i in range(len(history)):
                ev = history.popleft()
                history.append(ev)
                # retarget even to requester
                ev["dst"] = dst
                await post(ev)
