"""Lightweight structured logging."""
from __future__ import annotations

import logging
import sys

from app.core.config import CONFIG

_FMT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_DATEFMT = "%H:%M:%S"


def setup_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_FMT, _DATEFMT))
    root.addHandler(handler)
    root.setLevel(getattr(logging, CONFIG.log_level, logging.INFO))
    # keep noisy libs quiet
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
