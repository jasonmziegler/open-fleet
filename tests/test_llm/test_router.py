"""Tests for Story 3.4: LLM Router with automatic fallback and retry."""
import asyncio
import logging
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from open_fleet.exceptions import LLMProviderError, LLMTimeoutError, LLMValidationError
from open_fleet.llm.router import LLMRouter
from open_fleet.llm.schemas import ActionItem, ExtractionResult


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------


class _CapturingHandler(logging.Handler):
    """Collects LogRecord objects emitted to a specific logger."""
    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@contextmanager
def _capture_router_logs(level: int = logging.DEBUG):
    """Context manager that captures records from open_fleet.llm.router directly."""
    handler = _CapturingHandler()
    log = logging.getLogger("open_fleet.llm.router")
    orig_level = log.level
    log.setLevel(level)
    log.addHandler(handler)
    try:
        yield handler.records
    finally:
        log.removeHandler(handler)
        log.setLevel(orig_level)

_VALID_RESULT = ExtractionResult(
    action_items=[
        ActionItem(
            description="Follow up on contract",
            client="Globex",
            sender="bob@globex.com",
            email_timestamp="2026-03-01T10:00:00+00:00",
            deadline=None,
            priority="this_week",
            sentiment="neutral",
            context="Can you confirm the contract status?",
        )
    ],
    emails_scanned=5,
    timeframe="last 24 hours",
)

_VALID_EMAIL = {
    "subject": "Contract status",
    "sender": "bob@globex.com",
    "timestamp": "2026-03-01T10:00:00+00:00",
    "body": "Can you confirm the contract status?",
}


def _router(lmstudio=None, gemini=None) -> LLMRouter:
    """Build a router with mock providers."""
    lm = lmstudio or MagicMock()
    gm = gemini or MagicMock()
    return LLMRouter(lmstudio=lm, gemini=gm)


def _provider_returning(result) -> MagicMock:
    p = MagicMock()
    p.extract = AsyncMock(return_value=result)
    return p


def _provider_raising(exc) -> MagicMock:
    p = MagicMock()
    p.extract = AsyncMock(side_effect=exc)
    return p


# ---------------------------------------------------------------------------
# Primary path: LM Studio success
# ---------------------------------------------------------------------------

class TestLMStudioPrimaryPath:
    def test_lmstudio_success_returns_result(self):
        router = _router(lmstudio=_provider_returning(_VALID_RESULT))
        result = asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert isinstance(result, ExtractionResult)
        assert result.emails_scanned == 5

    def test_lmstudio_success_does_not_call_gemini(self):
        gemini = _provider_returning(_VALID_RESULT)
        router = _router(
            lmstudio=_provider_returning(_VALID_RESULT),
            gemini=gemini,
        )
        asyncio.run(router.run_extraction([_VALID_EMAIL]))
        gemini.extract.assert_not_called()

    def test_lmstudio_success_logs_lmstudio_provider(self):
        router = _router(lmstudio=_provider_returning(_VALID_RESULT))
        with _capture_router_logs(logging.INFO) as records:
            asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert any(getattr(r, "provider", None) == "lmstudio" for r in records)

    def test_lmstudio_success_log_has_all_required_fields(self):
        router = _router(lmstudio=_provider_returning(_VALID_RESULT))
        with _capture_router_logs(logging.INFO) as records:
            asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert records, "Router should emit at least one log record"
        record = records[-1]
        assert hasattr(record, "provider")
        assert hasattr(record, "email_count")
        assert hasattr(record, "action_item_count")
        assert hasattr(record, "duration_ms")
        assert hasattr(record, "error")


# ---------------------------------------------------------------------------
# Gemini fallback
# ---------------------------------------------------------------------------

class TestGeminiFailover:
    def test_lmstudio_timeout_triggers_gemini_fallback(self):
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_returning(_VALID_RESULT),
        )
        result = asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert isinstance(result, ExtractionResult)

    def test_lmstudio_provider_error_triggers_gemini_fallback(self):
        router = _router(
            lmstudio=_provider_raising(LLMProviderError("connection refused")),
            gemini=_provider_returning(_VALID_RESULT),
        )
        result = asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert isinstance(result, ExtractionResult)

    def test_gemini_fallback_logs_gemini_provider(self):
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_returning(_VALID_RESULT),
        )
        with _capture_router_logs(logging.INFO) as records:
            asyncio.run(router.run_extraction([_VALID_EMAIL]))
        success_records = [r for r in records if getattr(r, "provider", None) == "gemini"]
        assert success_records, "Router should log provider='gemini' after fallback"

    def test_notify_callback_called_on_fallback(self):
        notified = []

        async def notify(msg: str):
            notified.append(msg)

        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_returning(_VALID_RESULT),
        )
        asyncio.run(router.run_extraction([_VALID_EMAIL], notify=notify))
        assert len(notified) == 1
        assert "Gemini" in notified[0] or "gemini" in notified[0].lower()

    def test_notify_callback_not_called_on_lmstudio_success(self):
        notified = []

        async def notify(msg: str):
            notified.append(msg)

        router = _router(lmstudio=_provider_returning(_VALID_RESULT))
        asyncio.run(router.run_extraction([_VALID_EMAIL], notify=notify))
        assert notified == []


# ---------------------------------------------------------------------------
# Validation retry
# ---------------------------------------------------------------------------

class TestValidationRetry:
    def test_lmstudio_validation_error_retries_same_provider(self):
        """First call raises LLMValidationError; second call succeeds."""
        provider = MagicMock()
        provider.extract = AsyncMock(side_effect=[
            LLMValidationError("bad json"),
            _VALID_RESULT,
        ])
        router = _router(lmstudio=provider)
        result = asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert isinstance(result, ExtractionResult)
        assert provider.extract.call_count == 2

    def test_validation_retry_does_not_call_gemini(self):
        """Validation error → retry → success should never touch Gemini."""
        provider = MagicMock()
        provider.extract = AsyncMock(side_effect=[
            LLMValidationError("bad json"),
            _VALID_RESULT,
        ])
        gemini = _provider_returning(_VALID_RESULT)
        router = _router(lmstudio=provider, gemini=gemini)
        asyncio.run(router.run_extraction([_VALID_EMAIL]))
        gemini.extract.assert_not_called()

    def test_validation_retry_failure_raises_validation_error(self):
        """Both attempts raise LLMValidationError → router raises LLMValidationError."""
        provider = _provider_raising(LLMValidationError("bad schema"))
        router = _router(lmstudio=provider)
        with pytest.raises(LLMValidationError):
            asyncio.run(router.run_extraction([_VALID_EMAIL]))

    def test_validation_retry_failure_does_not_fall_back_to_gemini(self):
        """Validation error + retry failure must NOT trigger Gemini fallback."""
        lmstudio = _provider_raising(LLMValidationError("bad schema"))
        gemini = _provider_returning(_VALID_RESULT)
        router = _router(lmstudio=lmstudio, gemini=gemini)
        with pytest.raises(LLMValidationError):
            asyncio.run(router.run_extraction([_VALID_EMAIL]))
        gemini.extract.assert_not_called()

    def test_gemini_validation_error_retries_gemini(self):
        """After LM Studio timeout, Gemini validation error → retry Gemini → success."""
        gemini = MagicMock()
        gemini.extract = AsyncMock(side_effect=[
            LLMValidationError("gemini bad json"),
            _VALID_RESULT,
        ])
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=gemini,
        )
        result = asyncio.run(router.run_extraction([_VALID_EMAIL]))
        assert isinstance(result, ExtractionResult)
        assert gemini.extract.call_count == 2

    def test_gemini_validation_retry_failure_raises_validation_error(self):
        """Both Gemini attempts fail validation → LLMValidationError raised."""
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_raising(LLMValidationError("bad schema")),
        )
        with pytest.raises(LLMValidationError):
            asyncio.run(router.run_extraction([_VALID_EMAIL]))


# ---------------------------------------------------------------------------
# Total failure
# ---------------------------------------------------------------------------

class TestTotalFailure:
    def test_both_providers_fail_raises_llm_error(self):
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_raising(LLMProviderError("gemini down")),
        )
        from open_fleet.exceptions import LLMError
        with pytest.raises(LLMError):
            asyncio.run(router.run_extraction([_VALID_EMAIL]))

    def test_failure_log_has_all_required_fields(self):
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_raising(LLMProviderError("gemini down")),
        )
        with _capture_router_logs(logging.ERROR) as records:
            with pytest.raises(Exception):
                asyncio.run(router.run_extraction([_VALID_EMAIL]))
        error_records = [r for r in records if r.levelno == logging.ERROR]
        assert error_records, "Router should emit an ERROR log on total failure"
        record = error_records[0]
        assert hasattr(record, "provider")
        assert hasattr(record, "email_count")
        assert hasattr(record, "action_item_count")
        assert hasattr(record, "duration_ms")
        assert hasattr(record, "error")
        assert record.error is not None

    def test_failure_log_action_item_count_is_zero(self):
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_raising(LLMProviderError("gemini down")),
        )
        with _capture_router_logs(logging.ERROR) as records:
            with pytest.raises(Exception):
                asyncio.run(router.run_extraction([_VALID_EMAIL]))
        error_records = [r for r in records if r.levelno == logging.ERROR]
        assert error_records[0].action_item_count == 0

    def test_no_partial_data_returned_on_failure(self):
        """run_extraction must raise — never return partial data — on any failure."""
        router = _router(
            lmstudio=_provider_raising(LLMTimeoutError("timed out")),
            gemini=_provider_raising(LLMProviderError("gemini down")),
        )
        with pytest.raises(Exception):
            asyncio.run(router.run_extraction([_VALID_EMAIL]))
        # The above implicitly verifies no return value on failure
