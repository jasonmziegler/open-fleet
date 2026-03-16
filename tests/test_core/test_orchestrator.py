"""Tests for Story 4.2: Extraction Orchestrator."""
import ast
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from open_fleet.core.orchestrator import Orchestrator
from open_fleet.exceptions import GmailAuthError, GmailRateLimitError, LLMTimeoutError
from open_fleet.llm.router import LLMRouter
from open_fleet.llm.schemas import ActionItem, ExtractionResult
from open_fleet.tools.gmail import GmailClient


# ---------------------------------------------------------------------------
# Helpers & shared fixtures
# ---------------------------------------------------------------------------

_RAW_MSG_1 = {"id": "msg1", "payload": {}}
_RAW_MSG_2 = {"id": "msg2", "payload": {}}

_PARSED_EMAIL = {
    "subject": "Contract follow-up",
    "sender": "Alice <alice@example.com>",
    "timestamp": "2026-03-01T10:00:00+00:00",
    "body": "Please review the contract.",
}

_VALID_RESULT = ExtractionResult(
    action_items=[
        ActionItem(
            description="Review contract",
            client="Example Corp",
            sender="Alice <alice@example.com>",
            email_timestamp="2026-03-01T10:00:00+00:00",
            deadline=None,
            priority="this_week",
            sentiment="neutral",
            context="Please review the contract.",
        )
    ],
    emails_scanned=1,
    timeframe="last 24 hours",
)


def _gmail(fetch_return=None, fetch_side_effect=None) -> MagicMock:
    """Return a mock GmailClient with fetch_emails as AsyncMock."""
    client = MagicMock(spec=GmailClient)
    if fetch_side_effect is not None:
        client.fetch_emails = AsyncMock(side_effect=fetch_side_effect)
    else:
        client.fetch_emails = AsyncMock(
            return_value=fetch_return if fetch_return is not None else [_RAW_MSG_1]
        )
    return client


def _router(run_return=None, run_side_effect=None) -> MagicMock:
    """Return a mock LLMRouter with run_extraction as AsyncMock."""
    router = MagicMock(spec=LLMRouter)
    if run_side_effect is not None:
        router.run_extraction = AsyncMock(side_effect=run_side_effect)
    else:
        router.run_extraction = AsyncMock(return_value=run_return or _VALID_RESULT)
    return router


def _orch(gmail=None, router=None) -> Orchestrator:
    return Orchestrator(
        gmail_client=gmail or _gmail(),
        llm_router=router or _router(),
    )


# ---------------------------------------------------------------------------
# TestHappyPath
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_run_returns_list_of_strings(self):
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            result = asyncio.run(_orch().run("last 24 hours"))
        assert isinstance(result, list)
        assert all(isinstance(s, str) for s in result)
        assert len(result) >= 1

    def test_run_calls_fetch_emails_with_timeframe(self):
        gmail = _gmail()
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(Orchestrator(gmail_client=gmail, llm_router=_router()).run("last 48 hours"))
        gmail.fetch_emails.assert_called_once_with("last 48 hours", notify=None)

    def test_run_parses_each_raw_message(self):
        gmail = _gmail(fetch_return=[_RAW_MSG_1, _RAW_MSG_2])
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL) as mock_parse:
            asyncio.run(Orchestrator(gmail_client=gmail, llm_router=_router()).run("last 24 hours"))
        assert mock_parse.call_count == 2
        mock_parse.assert_any_call(_RAW_MSG_1)
        mock_parse.assert_any_call(_RAW_MSG_2)

    def test_run_passes_parsed_emails_to_router(self):
        router = _router()
        gmail = _gmail(fetch_return=[_RAW_MSG_1])
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(Orchestrator(gmail_client=gmail, llm_router=router).run("last 24 hours"))
        router.run_extraction.assert_called_once()
        call_args = router.run_extraction.call_args
        assert call_args[0][0] == [_PARSED_EMAIL]

    def test_run_passes_timeframe_to_router(self):
        router = _router()
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(
                Orchestrator(gmail_client=_gmail(), llm_router=router).run("since yesterday 5pm")
            )
        call_args = router.run_extraction.call_args
        assert call_args[0][1] == "since yesterday 5pm"

    def test_run_returns_formatted_output_from_extraction_result(self):
        """format() output is returned directly — no transformation by orchestrator."""
        expected = ["message chunk 1", "message chunk 2"]
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL), \
             patch("open_fleet.core.orchestrator.ResponseFormatter.format", return_value=expected):
            result = asyncio.run(_orch().run("last 24 hours"))
        assert result == expected

    def test_pipeline_order_fetch_parse_extract_format(self):
        """Verify the pipeline executes in exact order: fetch → parse → extract → format."""
        call_order: list[str] = []

        async def _fetch(*a, **kw):
            call_order.append("fetch")
            return [_RAW_MSG_1]

        async def _extract(*a, **kw):
            call_order.append("extract")
            return _VALID_RESULT

        gmail = _gmail()
        gmail.fetch_emails = AsyncMock(side_effect=_fetch)
        router = _router()
        router.run_extraction = AsyncMock(side_effect=_extract)
        with patch.object(
            GmailClient, "parse_email",
            side_effect=lambda msg: (call_order.append("parse"), _PARSED_EMAIL)[1],
        ), patch(
            "open_fleet.core.orchestrator.ResponseFormatter.format",
            side_effect=lambda res: (call_order.append("format"), ["ok"])[1],
        ):
            asyncio.run(Orchestrator(gmail_client=gmail, llm_router=router).run("last 24 hours"))
        assert call_order == ["fetch", "parse", "extract", "format"]

    def test_run_empty_inbox_returns_formatted_empty_result(self):
        """Zero emails is a valid run — orchestrator passes empty list to router."""
        router = _router()
        gmail = _gmail(fetch_return=[])
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(Orchestrator(gmail_client=gmail, llm_router=router).run("last 24 hours"))
        router.run_extraction.assert_called_once()
        assert router.run_extraction.call_args[0][0] == []


# ---------------------------------------------------------------------------
# TestNotifyCallback
# ---------------------------------------------------------------------------


class TestNotifyCallback:
    def test_notify_threaded_to_fetch_emails(self):
        gmail = _gmail()
        notify_fn = AsyncMock()
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(
                Orchestrator(gmail_client=gmail, llm_router=_router()).run(
                    "last 24 hours", notify=notify_fn
                )
            )
        gmail.fetch_emails.assert_called_once_with("last 24 hours", notify=notify_fn)

    def test_notify_threaded_to_run_extraction(self):
        router = _router()
        notify_fn = AsyncMock()
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(
                Orchestrator(gmail_client=_gmail(), llm_router=router).run(
                    "last 24 hours", notify=notify_fn
                )
            )
        call_kwargs = router.run_extraction.call_args[1]
        assert call_kwargs.get("notify") is notify_fn

    def test_notify_defaults_to_none(self):
        gmail = _gmail()
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            asyncio.run(Orchestrator(gmail_client=gmail, llm_router=_router()).run("last 24 hours"))
        gmail.fetch_emails.assert_called_once_with("last 24 hours", notify=None)


# ---------------------------------------------------------------------------
# TestGmailErrorHandling
# ---------------------------------------------------------------------------


class TestGmailErrorHandling:
    def test_gmail_auth_error_returns_auth_expired_message(self):
        gmail = _gmail(fetch_side_effect=GmailAuthError("token expired"))
        result = asyncio.run(Orchestrator(gmail_client=gmail, llm_router=_router()).run("last 24 hours"))
        assert result == [
            "❌ Gmail authentication expired — run scripts/setup_gmail_auth.py to reconnect"
        ]

    def test_gmail_rate_limit_error_returns_rate_limit_message(self):
        gmail = _gmail(fetch_side_effect=GmailRateLimitError("rate limit hit"))
        result = asyncio.run(Orchestrator(gmail_client=gmail, llm_router=_router()).run("last 24 hours"))
        assert result == [
            "❌ Gmail API rate limit — extraction could not complete after retries"
        ]

    def test_gmail_auth_error_does_not_call_router(self):
        router = _router()
        gmail = _gmail(fetch_side_effect=GmailAuthError("expired"))
        asyncio.run(Orchestrator(gmail_client=gmail, llm_router=router).run("last 24 hours"))
        router.run_extraction.assert_not_called()

    def test_gmail_rate_limit_error_does_not_call_router(self):
        router = _router()
        gmail = _gmail(fetch_side_effect=GmailRateLimitError("exhausted"))
        asyncio.run(Orchestrator(gmail_client=gmail, llm_router=router).run("last 24 hours"))
        router.run_extraction.assert_not_called()


# ---------------------------------------------------------------------------
# TestLLMErrorHandling
# ---------------------------------------------------------------------------


class TestLLMErrorHandling:
    def test_llm_timeout_error_returns_llm_unavailable_message(self):
        router = _router(run_side_effect=LLMTimeoutError("both providers exhausted"))
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            result = asyncio.run(
                Orchestrator(gmail_client=_gmail(), llm_router=router).run("last 24 hours")
            )
        assert result == [
            "❌ LLM extraction failed — both LM Studio and Gemini unavailable"
        ]


# ---------------------------------------------------------------------------
# TestUnexpectedErrorHandling
# ---------------------------------------------------------------------------


class TestUnexpectedErrorHandling:
    def test_unexpected_exception_returns_generic_error_message(self):
        gmail = _gmail(fetch_side_effect=ValueError("unexpected internal error"))
        result = asyncio.run(Orchestrator(gmail_client=gmail, llm_router=_router()).run("last 24 hours"))
        assert result == ["❌ Unexpected error — check logs for details"]

    def test_unexpected_exception_logs_at_error_level_with_exc_info(self):
        gmail = _gmail(fetch_side_effect=RuntimeError("boom"))
        orch = Orchestrator(gmail_client=gmail, llm_router=_router())
        with patch("open_fleet.core.orchestrator.logger") as mock_logger:
            asyncio.run(orch.run("last 24 hours"))
        mock_logger.error.assert_called_once()
        _, kwargs = mock_logger.error.call_args
        assert kwargs.get("exc_info") is True

    def test_format_exception_falls_to_generic_handler(self):
        """If ResponseFormatter.format() raises, the catch-all returns the generic error."""
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL), \
             patch(
                 "open_fleet.core.orchestrator.ResponseFormatter.format",
                 side_effect=TypeError("unexpected format error"),
             ):
            result = asyncio.run(_orch().run("last 24 hours"))
        assert result == ["❌ Unexpected error — check logs for details"]

    def test_unhandled_open_fleet_error_falls_to_generic_handler(self):
        """LLMProviderError / LLMValidationError / GmailFetchError are not specifically
        handled — they fall through to the catch-all and return the generic message."""
        from open_fleet.exceptions import LLMProviderError
        router = _router(run_side_effect=LLMProviderError("provider down"))
        with patch.object(GmailClient, "parse_email", return_value=_PARSED_EMAIL):
            result = asyncio.run(
                Orchestrator(gmail_client=_gmail(), llm_router=router).run("last 24 hours")
            )
        assert result == ["❌ Unexpected error — check logs for details"]


# ---------------------------------------------------------------------------
# TestNoSlackImports
# ---------------------------------------------------------------------------


class TestNoSlackImports:
    def test_orchestrator_has_no_slack_imports(self):
        src_path = Path("src/open_fleet/core/orchestrator.py")
        tree = ast.parse(src_path.read_text(encoding="utf-8"))
        forbidden = {"slack_bolt", "slack_sdk", "adapters"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden_name in forbidden:
                        assert forbidden_name not in alias.name, (
                            f"Forbidden import found: {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for forbidden_name in forbidden:
                    assert forbidden_name not in module, (
                        f"Forbidden import found: from {module}"
                    )
