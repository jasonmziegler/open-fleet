"""Tests for Story 1.4: Structured Logging Infrastructure."""
import json
import logging

import pytest

import open_fleet.logging_setup as logging_setup
from open_fleet.logging_setup import configure


@pytest.fixture(autouse=True)
def reset_logger():
    """Remove all handlers from the open_fleet logger between tests."""
    logger = logging.getLogger("open_fleet")
    yield
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


# --- JSON format ---

def test_log_record_is_valid_json(capsys):
    configure(log_dir=None)
    logging.getLogger("open_fleet.test").info("hello world")

    out = capsys.readouterr().out
    record = json.loads(out.strip())
    assert record["level"] == "INFO"
    assert record["message"] == "hello world"
    assert record["module"] == "open_fleet.test"
    assert "timestamp" in record


def test_required_fields_present(capsys):
    configure(log_dir=None)
    logging.getLogger("open_fleet.test").warning("check fields")

    record = json.loads(capsys.readouterr().out.strip())
    for field in ("timestamp", "level", "module"):
        assert field in record, f"Missing field: {field}"


# --- Test mode (no file output) ---

def test_no_file_handler_in_test_mode():
    configure(log_dir=None)
    logger = logging.getLogger("open_fleet")
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    assert file_handlers == [], "No file handler should be added in test mode"


def test_stdout_handler_present_in_test_mode():
    configure(log_dir=None)
    logger = logging.getLogger("open_fleet")
    stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)
                       and not isinstance(h, logging.FileHandler)]
    assert len(stream_handlers) == 1


# --- Production mode (with file output) ---

def test_file_handler_created_in_production_mode(tmp_path):
    configure(log_dir=tmp_path)
    logger = logging.getLogger("open_fleet")

    file_handlers = [h for h in logger.handlers
                     if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(file_handlers) == 1


def test_log_file_written_in_production_mode(tmp_path):
    configure(log_dir=tmp_path)
    logging.getLogger("open_fleet.test").info("written to file")

    log_file = tmp_path / "open_fleet.log"
    assert log_file.exists()
    record = json.loads(log_file.read_text().strip())
    assert record["message"] == "written to file"


def test_rotating_handler_configured_correctly(tmp_path):
    configure(log_dir=tmp_path)
    logger = logging.getLogger("open_fleet")

    handler = next(
        h for h in logger.handlers
        if isinstance(h, logging.handlers.RotatingFileHandler)
    )
    assert handler.maxBytes == logging_setup._MAX_BYTES
    assert handler.backupCount == logging_setup._BACKUP_COUNT


def test_log_dir_created_if_not_exists(tmp_path):
    new_dir = tmp_path / "nested" / "logs"
    configure(log_dir=new_dir)
    assert new_dir.exists()


# --- Idempotency ---

def test_configure_called_twice_does_not_duplicate_handlers():
    configure(log_dir=None)
    configure(log_dir=None)
    logger = logging.getLogger("open_fleet")
    assert len(logger.handlers) == 1


# --- Propagation ---

def test_does_not_propagate_to_root_logger():
    configure(log_dir=None)
    assert logging.getLogger("open_fleet").propagate is False


# --- Extra fields (architecture: Log Record Schema) ---

def test_extra_fields_included_in_json_output(capsys):
    configure(log_dir=None)
    logging.getLogger("open_fleet.test").info(
        "extraction_complete",
        extra={
            "provider": "lmstudio",
            "email_count": 187,
            "action_item_count": 14,
            "duration_ms": 23450,
            "error": None,
        },
    )

    record = json.loads(capsys.readouterr().out.strip())
    assert record["provider"] == "lmstudio"
    assert record["email_count"] == 187
    assert record["action_item_count"] == 14
    assert record["duration_ms"] == 23450
    assert record["error"] is None


# --- UTC ISO8601 timestamp ---

def test_timestamp_includes_utc_offset(capsys):
    configure(log_dir=None)
    logging.getLogger("open_fleet.test").info("tz check")

    record = json.loads(capsys.readouterr().out.strip())
    assert record["timestamp"].endswith("+00:00")
