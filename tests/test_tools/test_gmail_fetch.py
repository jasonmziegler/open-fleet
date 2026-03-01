"""Tests for Story 2.2: Gmail email fetch and pagination."""
import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from open_fleet.exceptions import GmailFetchError
from open_fleet.tools.gmail import GmailClient, _parse_timeframe


# ---------------------------------------------------------------------------
# Timeframe parser
# ---------------------------------------------------------------------------

class TestParseTimeframe:
    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def test_last_24_hours(self):
        result = _parse_timeframe("last 24 hours")
        expected = self._now() - timedelta(hours=24)
        assert abs((result - expected).total_seconds()) < 2

    def test_last_1_hour(self):
        result = _parse_timeframe("last 1 hour")
        expected = self._now() - timedelta(hours=1)
        assert abs((result - expected).total_seconds()) < 2

    def test_last_3_days(self):
        result = _parse_timeframe("last 3 days")
        expected = self._now() - timedelta(days=3)
        assert abs((result - expected).total_seconds()) < 2

    def test_today_returns_midnight(self):
        result = _parse_timeframe("today")
        now = self._now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        assert result == midnight

    def test_since_yesterday_midnight(self):
        result = _parse_timeframe("since yesterday")
        now = self._now()
        expected = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result == expected

    def test_since_yesterday_5pm(self):
        result = _parse_timeframe("since yesterday 5pm")
        now = self._now()
        expected = (now - timedelta(days=1)).replace(hour=17, minute=0, second=0, microsecond=0)
        assert result == expected

    def test_since_yesterday_9am(self):
        result = _parse_timeframe("since yesterday 9am")
        now = self._now()
        expected = (now - timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        assert result == expected

    def test_since_yesterday_12pm(self):
        result = _parse_timeframe("since yesterday 12pm")
        now = self._now()
        expected = (now - timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
        assert result == expected

    def test_since_yesterday_12am(self):
        result = _parse_timeframe("since yesterday 12am")
        now = self._now()
        expected = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        assert result == expected

    def test_unknown_pattern_raises_value_error(self):
        with pytest.raises(ValueError, match="Cannot parse timeframe"):
            _parse_timeframe("next week sometime")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_client(tmp_path: Path) -> GmailClient:
    """Return a GmailClient with mocked credentials."""
    token = tmp_path / "token.json"
    token.write_text("{}", encoding="utf-8")

    mock_creds = MagicMock()
    mock_creds.expired = False
    mock_creds.valid = True

    with patch("open_fleet.tools.gmail.Credentials.from_authorized_user_file",
               return_value=mock_creds):
        return GmailClient(token_path=token)


def _make_service(message_pages: list[list[dict]], full_messages: dict[str, dict]):
    """Build a mock Gmail API service.

    Args:
        message_pages: Each inner list is one page of message stubs {"id": "..."}.
        full_messages: Maps message ID → full message dict.
    """
    service = MagicMock()
    messages_resource = service.users.return_value.messages.return_value

    # list() returns pages in sequence
    list_responses = []
    for i, page in enumerate(message_pages):
        resp = {"messages": page}
        if i < len(message_pages) - 1:
            resp["nextPageToken"] = f"token_{i}"
        list_responses.append(resp)

    list_execute = MagicMock(side_effect=list_responses)
    messages_resource.list.return_value.execute = list_execute

    # get() returns full message by ID
    def _get_execute(userId, id, format):  # noqa: A002
        mock = MagicMock()
        mock.execute.return_value = full_messages.get(id, {"id": id})
        return mock

    messages_resource.get.side_effect = _get_execute

    return service


# ---------------------------------------------------------------------------
# fetch_emails
# ---------------------------------------------------------------------------

class TestFetchEmails:
    def test_single_page_returns_all_messages(self, tmp_path):
        client = _make_client(tmp_path)
        stubs = [{"id": f"msg{i}"} for i in range(5)]
        full = {s["id"]: {"id": s["id"], "payload": {}} for s in stubs}
        service = _make_service([stubs], full)

        with patch.object(client, "_build_service", return_value=service):
            result = asyncio.run(client.fetch_emails("last 24 hours"))

        assert len(result) == 5
        assert [m["id"] for m in result] == [s["id"] for s in stubs]

    def test_paginates_through_multiple_pages(self, tmp_path):
        client = _make_client(tmp_path)
        page1 = [{"id": f"msg{i}"} for i in range(3)]
        page2 = [{"id": f"msg{i}"} for i in range(3, 6)]
        all_stubs = page1 + page2
        full = {s["id"]: {"id": s["id"]} for s in all_stubs}
        service = _make_service([page1, page2], full)

        with patch.object(client, "_build_service", return_value=service):
            result = asyncio.run(client.fetch_emails("last 24 hours"))

        assert len(result) == 6

    def test_empty_inbox_returns_empty_list(self, tmp_path):
        client = _make_client(tmp_path)
        service = _make_service([[]], {})
        # list returns no messages key
        service.users.return_value.messages.return_value.list.return_value.execute.return_value = {}

        with patch.object(client, "_build_service", return_value=service):
            result = asyncio.run(client.fetch_emails("last 24 hours"))

        assert result == []

    def test_query_uses_after_filter(self, tmp_path):
        client = _make_client(tmp_path)
        service = _make_service([[]], {})
        service.users.return_value.messages.return_value.list.return_value.execute.return_value = {}

        with patch.object(client, "_build_service", return_value=service):
            asyncio.run(client.fetch_emails("last 24 hours"))

        call_kwargs = service.users.return_value.messages.return_value.list.call_args
        query = call_kwargs.kwargs.get("q") or call_kwargs.args[0] if call_kwargs.args else \
                call_kwargs[1].get("q", call_kwargs[0][0] if call_kwargs[0] else "")
        # Extract q from however it was called
        all_kwargs = service.users.return_value.messages.return_value.list.call_args_list[0]
        q_value = all_kwargs.kwargs.get("q", "")
        assert q_value.startswith("after:")

    def test_list_api_error_raises_fetch_error(self, tmp_path):
        client = _make_client(tmp_path)
        service = MagicMock()
        service.users.return_value.messages.return_value.list.return_value.execute.side_effect = \
            Exception("API quota exceeded")

        with patch.object(client, "_build_service", return_value=service):
            with pytest.raises(GmailFetchError, match="list request failed"):
                asyncio.run(client.fetch_emails("last 24 hours"))

    def test_get_api_error_raises_fetch_error(self, tmp_path):
        client = _make_client(tmp_path)
        stubs = [{"id": "msg1"}]
        service = _make_service([stubs], {})
        # Override get to raise
        service.users.return_value.messages.return_value.get.side_effect = \
            Exception("Message not found")

        with patch.object(client, "_build_service", return_value=service):
            with pytest.raises(GmailFetchError, match="get request failed"):
                asyncio.run(client.fetch_emails("last 24 hours"))

    def test_200_messages_retrieved_across_pages(self, tmp_path):
        client = _make_client(tmp_path)
        # Simulate 200 messages across 2 pages of 100
        page1 = [{"id": f"msg{i}"} for i in range(100)]
        page2 = [{"id": f"msg{i}"} for i in range(100, 200)]
        full = {s["id"]: {"id": s["id"]} for s in page1 + page2}
        service = _make_service([page1, page2], full)

        with patch.object(client, "_build_service", return_value=service):
            result = asyncio.run(client.fetch_emails("last 24 hours"))

        assert len(result) == 200
