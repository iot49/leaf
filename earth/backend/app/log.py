import json
import logging
from logging import Formatter

from colored import Fore, Style
from starlette.middleware.base import BaseHTTPMiddleware

from eventbus import post_sync
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


class PrintFormatter(Formatter):
    def __init__(self):
        super(PrintFormatter, self).__init__()

    def format(self, record):
        colors = {
            logging.DEBUG: Fore.blue,
            logging.INFO: Fore.green,
            logging.WARNING: Fore.yellow,
            logging.ERROR: Fore.red,
            logging.CRITICAL: Fore.magenta,
        }
        return f"{colors[record.levelno]}{record.levelname+':':9}{Style.reset} {record.name:12} {record.funcName:12} {record.getMessage()}"


class EventLogHandler(logging.Handler):
    def emit(self, record):
        event = log_event(
            levelname=record.levelname,
            levelno=record.levelno,
            timestamp=record.created,
            name=record.name,
            message=record.getMessage(),
        )
        post_sync(event)


logger = logging.root
handler = logging.StreamHandler()
# handler.setFormatter(JsonFormatter())
handler.setFormatter(PrintFormatter())
logger.handlers = [handler, EventLogHandler()]
logger.setLevel(logging.ERROR)

logging.getLogger("uvicorn.access").disabled = True
