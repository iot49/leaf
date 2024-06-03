# https://github.com/tom-draper/api-analytics

import logging
import time
from collections import deque

from eventbus import event_type, eventbus

BLUE = "\x1b[38;5;4m"
GREEN = "\x1b[38;5;2m"
YELLOW = "\x1b[38;5;3m"
RED = "\x1b[38;5;1m"
MAGENTA = "\x1b[38;5;5m"

RESET = "\x1b[0m"


class Log:
    """Keep event history"""

    def __init__(self, size=100):
        self.history = deque((), size)
        self.last_event = None

        print()

        @eventbus.on(event_type.LOG)
        async def log(**event):
            # receive log message
            # append to history and print to console
            if self.last_event is not None:
                last = self.last_event
                if last.get("levelno") == event.get("levelno") and last.get("message") == event.get("message"):
                    last["count"] = last.get("count", 1) + 1
                    return
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
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(event.get("timestamp", 0)))  # type: ignore
            count = event.get("count")
            # BUG: count is never reported (see return above ...)
            repeat = f"[{count}] " if count is not None else ""
            print(
                f"{repeat}{t} {color}{event.get('levelname'):9}{RESET} {event.get('src'):12} {event.get('name'):20} {funcName:16} {event.get('message')}"
            )
            tb = event.get("traceback")
            if tb is not None:
                print(tb)

        @eventbus.on(event_type.GET_LOG)
        async def get(src, **event):
            # send logging history
            history = self.history
            dst = src
            for i in range(len(history)):
                ev = history.popleft()
                history.append(ev)
                # retarget event to requester
                ev["dst"] = dst
                await eventbus.emit(ev)
