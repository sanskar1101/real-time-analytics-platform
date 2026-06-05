from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class _CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get("")  # type: ignore[attr-defined]
        return True


def configure_logging(*, json_logs: bool = False) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_CorrelationIdFilter())

    if json_logs:
        try:
            from pythonjsonlogger import jsonlogger  # type: ignore[import]

            handler.setFormatter(
                jsonlogger.JsonFormatter(
                    fmt="%(asctime)s %(name)s %(levelname)s %(correlation_id)s %(message)s",
                    rename_fields={
                        "asctime": "timestamp",
                        "levelname": "level",
                        "name": "logger",
                        "correlation_id": "correlation_id",
                    },
                )
            )
        except ImportError:
            handler.setFormatter(_text_formatter())
    else:
        handler.setFormatter(_text_formatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


def _text_formatter() -> logging.Formatter:
    return logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] [%(correlation_id)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
