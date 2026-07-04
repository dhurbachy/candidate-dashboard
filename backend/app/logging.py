import logging
import logging.config
import sys
import json
import os
from datetime import datetime, timezone

class CentralizedJsonFormatter(logging.Formatter):
    """
    Production Formatter
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line_number": record.lineno,
        }

        if record.exc_info:
            log_payload["exception_trace"] = self.formatException(record.exc_info)

        return json.dumps(log_payload)


class LocalConsoleFormatter(logging.Formatter):
    """
    Local Development Formatter
    """
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        log_line = f"[{timestamp}] [{record.levelname:<7}] ({record.name}:{record.module}:{record.lineno}) -> {record.getMessage()}"
        
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"
            
        return log_line


APP_ENV = os.getenv("APP_ENV", "development").lower()
FORMATTER_CHOICE = "json" if APP_ENV == "production" else "console"

UVICORN_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": CentralizedJsonFormatter,
        },
        "console": {
            "()": LocalConsoleFormatter,
        }
    },
    "handlers": {
        "stdout": {
            "formatter": FORMATTER_CHOICE,  
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "hrmodule": {"handlers": ["stdout"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(UVICORN_LOGGING_CONFIG)
logger = logging.getLogger("hrmodule")
