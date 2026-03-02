"""Tests for Story 2.4: Gmail rate limit handling with exponential backoff."""
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest
from googleapiclient.errors import HttpError

from open_fleet.exceptions import GmailFetchError, GmailRateLimitError
from open_fleet.tools.gmail import GmailClient, _execute_with_retry, _RETRY_DELAYS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _http_error(status: int, reason: str = "error") -> HttpError:
    """Build a googleapiclient HttpError with the given HTTP status."""
    resp = MagicMock()
    resp.status = status
    resp.reason = reason
    return HttpError(resp=resp, content=reason.encode())


def _make_client(tmp_path: Path) -> GmailClient:
    token = tmp_path / "token.json"
    token.write_text("{}", encoding="utf-8")
    mock_creds = MagicMock()
    mock_creds.expired = False
    with patch("open_fleet.tools.gmail.Credentials.from_authorized_user_file",
               return_value=mock_creds):
        return GmailClient(token_path=token)


# ---------------------------------------------------------------------------
# _execute_with_retry unit tests
# ---------------------------------------------------------------------------

class TestExecuteWithRetry:
    """Test the retry helper directly."""

    def test_success_on_first_attempt(self):
        sync_fn = MagicMock(return_value={"ok": True})
        result = asyncio.run(
            _execute_with_retry(sync_fn, notify=None, label="test")
        )
        assert result == {"ok": True}
        sync_fn.assert_called_once()

    def test_retries_three_times_on_429_then_raises(self):
        sync_fn = MagicMock(side_effect=_http_error(429))

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with pytest.raises(GmailRateLimitError):
                asyncio.run(
                    _execute_with_retry(sync_fn, notify=None, label="test")
                )

        # Initial attempt + 3 retries = 4 total calls
        assert sync_fn.call_count == len(_RETRY_DELAYS) + 1
        # Sleep called once per retry with correct backoff delays
        assert mock_sleep.call_count == len(_RETRY_DELAYS)
        sleep_args = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_args == _RETRY_DELAYS

    def test_succeeds_on_second_attempt_after_429(self):
        sync_fn = MagicMock(side_effect=[_http_error(429), {"ok": True}])

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            result = asyncio.run(
                _execute_with_retry(sync_fn, notify=None, label="test")
            )

        assert result == {"ok": True}
        assert sync_fn.call_count == 2

    def test_non_429_raises_fetch_error_immediately(self):
        sync_fn = MagicMock(side_effect=_http_error(500, "Internal Server Error"))

        with pytest.raises(GmailFetchError, match="HTTP 500"):
            asyncio.run(
                _execute_with_retry(sync_fn, notify=None, label="test")
            )

        sync_fn.assert_called_once()  # No retry for non-429

    def test_unexpected_exception_raises_fetch_error(self):
        sync_fn = MagicMock(side_effect=ConnectionError("network down"))

        with pytest.raises(GmailFetchError, match="network down"):
            asyncio.run(
                _execute_with_retry(sync_fn, notify=None, label="test")
            )

    def test_notify_called_before_each_retry(self):
        sync_fn = MagicMock(side_effect=_http_error(429))
        notify = AsyncMock()

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(GmailRateLimitError):
                asyncio.run(
                    _execute_with_retry(sync_fn, notify=notify, label="test")
                )

        # notify called once before each of the 3 retry delays
        assert notify.call_count == len(_RETRY_DELAYS)

    def test_notify_message_contains_retry_delay(self):
        sync_fn = MagicMock(side_effect=_http_error(429))
        notify = AsyncMock()

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(GmailRateLimitError):
                asyncio.run(
                    _execute_with_retry(sync_fn, notify=notify, label="test")
                )

        messages = [c.args[0] for c in notify.call_args_list]
        assert "1 seconds" in messages[0]
        assert "2 seconds" in messages[1]
        assert "4 seconds" in messages[2]

    def test_notify_message_format(self):
        sync_fn = MagicMock(side_effect=[_http_error(429), {"ok": True}])
        notify = AsyncMock()

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            asyncio.run(
                _execute_with_retry(sync_fn, notify=notify, label="test")
            )

        msg = notify.call_args.args[0]
        assert msg.startswith("⚠️")
        assert "rate limit" in msg.lower()

    def test_rate_limit_error_mentions_attempt_count(self):
        sync_fn = MagicMock(side_effect=_http_error(429))

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(GmailRateLimitError) as exc_info:
                asyncio.run(
                    _execute_with_retry(sync_fn, notify=None, label="test")
                )

        assert str(len(_RETRY_DELAYS) + 1) in str(exc_info.value)

    def test_notify_none_does_not_raise(self):
        """Passing notify=None should work silently."""
        sync_fn = MagicMock(side_effect=[_http_error(429), {"ok": True}])

        with patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            result = asyncio.run(
                _execute_with_retry(sync_fn, notify=None, label="test")
            )

        assert result == {"ok": True}


# ---------------------------------------------------------------------------
# fetch_emails integration — rate limit propagation
# ---------------------------------------------------------------------------

class TestFetchEmailsRateLimit:
    def _make_service_with_429(self):
        service = MagicMock()
        service.users.return_value.messages.return_value.list.return_value \
            .execute.side_effect = _http_error(429)
        return service

    def test_fetch_emails_propagates_rate_limit_error(self, tmp_path):
        client = _make_client(tmp_path)
        service = self._make_service_with_429()

        with patch.object(client, "_build_service", return_value=service), \
             patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(GmailRateLimitError):
                asyncio.run(client.fetch_emails("last 24 hours"))

    def test_fetch_emails_passes_notify_to_retry(self, tmp_path):
        client = _make_client(tmp_path)
        service = self._make_service_with_429()
        notify = AsyncMock()

        with patch.object(client, "_build_service", return_value=service), \
             patch("open_fleet.tools.gmail.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(GmailRateLimitError):
                asyncio.run(client.fetch_emails("last 24 hours", notify=notify))

        assert notify.call_count == len(_RETRY_DELAYS)

    def test_fetch_emails_non_429_raises_fetch_error(self, tmp_path):
        client = _make_client(tmp_path)
        service = MagicMock()
        service.users.return_value.messages.return_value.list.return_value \
            .execute.side_effect = _http_error(500, "Internal Server Error")

        with patch.object(client, "_build_service", return_value=service):
            with pytest.raises(GmailFetchError, match="HTTP 500"):
                asyncio.run(client.fetch_emails("last 24 hours"))
