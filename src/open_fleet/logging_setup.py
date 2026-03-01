# src/open_fleet/logging_setup.py
"""Structured JSON logging infrastructure.

Call configure() once in main.py before any other module initializes.

Production mode (log_dir provided):
  - RotatingFileHandler → logs/open_fleet.log (JSON, 10MB × 7 backups)
  - StreamHandler       → stdout (JSON, same records)

Test mode (log_dir=None):
  - StreamHandler → stdout only; no file is created or written.

All loggers in the project use the "open_fleet" namespace:
    logging.getLogger("open_fleet.config")
    logging.getLogger("open_fleet.tools.gmail")
    ...
"""
from __future__ import annotations

import json
import logging
import logging.handlers
import sys
from pathlib import Path

_LOG_FORMAT_FIELDS = ("timestamp", "level", "module")
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 7
_LOG_FILENAME = "open_fleet.log"


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure(log_dir: Path | None = None) -> None:
    """Configure the root open_fleet logger.

    Args:
        log_dir: Directory for rotating log files. Pass None (default) in
                 tests to suppress file output and write to stdout only.
    """
    root_logger = logging.getLogger("open_fleet")

    # Avoid adding duplicate handlers if called more than once
    if root_logger.handlers:
        return

    root_logger.setLevel(logging.DEBUG)
    formatter = _JsonFormatter()

    # stdout handler — always present
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # rotating file handler — production only
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / _LOG_FILENAME,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Prevent log records from propagating to the root Python logger
    root_logger.propagate = False
