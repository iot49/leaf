import json
import logging
import traceback
from io import StringIO
from logging import Formatter, Handler

from starlette.middleware.base import BaseHTTPMiddleware

from eventbus import post_sync
from eventbus.bus.log import Log
from eventbus.event import log_event


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        logger.info(
            "Incoming request",
            extra={
                "req": {"method": request.method, "url": str(request.url)},
                "res": {
                    "status_code": response.status_code,
                },
            },
        )
        return response


class JsonFormatter(Formatter):
    def __init__(self):
        super(JsonFormatter, self).__init__()

    def format(self, record):
        json_record = {}
        json_record["message"] = record.getMessage()
        if "req" in record.__dict__:
            json_record["req"] = record.__dict__["req"]
        if "res" in record.__dict__:
            json_record["res"] = record.__dict__["res"]
        if record.levelno == logging.ERROR and record.exc_info:
            json_record["err"] = self.formatException(record.exc_info)
        return json.dumps(json_record)


class EventLogHandler(Handler):
    def __init__(self):
        super(EventLogHandler, self).__init__()

    def emit(self, record):
        event = log_event(
            levelname=record.levelname,
            levelno=record.levelno,
            timestamp=record.created,
            name=record.name,
            funcName=record.funcName,
            message=record.getMessage(),
        )
        if record.exc_info:
            buf = StringIO()
            print(traceback.print_tb(record.exc_info[2], file=buf))
            event["traceback"] = buf.getvalue()
        post_sync(event)


logger = logging.root
logger.handlers = [EventLogHandler()]
logger.setLevel(logging.ERROR)

logging.getLogger("uvicorn.access").disabled = True

log_history = Log(size=500)


# handler.setFormatter(JsonFormatter())
