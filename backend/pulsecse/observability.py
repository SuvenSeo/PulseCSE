from __future__ import annotations

import json
import logging
import sys
from time import perf_counter
from typing import Any

from pulsecse.config import settings


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)


def log_event(name: str, **fields: Any) -> None:
    payload = {"event": name, **fields}
    if settings.log_json:
        logging.getLogger("pulsecse").info(json.dumps(payload, default=str, sort_keys=True))
    else:
        logging.getLogger("pulsecse").info("%s %s", name, fields)


class timer:
    def __init__(self, name: str, **fields: Any) -> None:
        self.name = name
        self.fields = fields
        self.started = 0.0

    def __enter__(self) -> "timer":
        self.started = perf_counter()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        elapsed_ms = round((perf_counter() - self.started) * 1000, 2)
        log_event(self.name, elapsed_ms=elapsed_ms, ok=exc is None, **self.fields)
