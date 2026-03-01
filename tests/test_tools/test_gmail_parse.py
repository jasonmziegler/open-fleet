"""Tests for Story 2.3: Email content parsing."""
import base64
from datetime import datetime, timezone

from open_fleet.tools.gmail import GmailClient, _strip_html


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _b64(text: str) -> str:
    """Return base64url-encoded text (as Gmail API delivers it)."""
    return base64.urlsafe_b64encode(text.encode()).decode().rstrip("=")


def _make_message(
    subject: str = "Test Subject",
    sender: str = "Alice <alice@example.com>",
    internal_date_ms: int = 1_700_000_000_000,
    mime_type: str = "text/plain",
    body_text: str = "Hello world",
    parts: list | None = None,
) -> dict:
    """Build a minimal Gmail API message resource."""
    payload: dict = {
        "mimeType": mime_type,
        "headers": [
            {"name": "Subject", "value": subject},
            {"name": "From", "value": sender},
        ],
    }
    if parts is not None:
        payload["parts"] = parts
    else:
        payload["body"] = {"data": _b64(body_text)}

    return {
        "internalDate": str(internal_date_ms),
        "payload": payload,
    }


# ---------------------------------------------------------------------------
# Plain-text email
# ---------------------------------------------------------------------------

class TestPlainTextEmail:
    def test_subject_extracted(self):
        msg = _make_message(subject="Weekly Report")
        result = GmailClient.parse_email(msg)
        assert result["subject"] == "Weekly Report"

    def test_sender_extracted(self):
        msg = _make_message(sender="Bob <bob@corp.com>")
        result = GmailClient.parse_email(msg)
        assert result["sender"] == "Bob <bob@corp.com>"

    def test_timestamp_is_utc_iso8601(self):
        # 1_700_000_000_000 ms = 2023-11-14T22:13:20+00:00
        msg = _make_message(internal_date_ms=1_700_000_000_000)
        result = GmailClient.parse_email(msg)
        dt = datetime.fromisoformat(result["timestamp"])
        assert dt.tzinfo is not None
        assert dt == datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)

    def test_body_returned_as_plain_text(self):
        msg = _make_message(body_text="Please review by Friday.")
        result = GmailClient.parse_email(msg)
        assert result["body"] == "Please review by Friday."

    def test_missing_subject_defaults(self):
        msg = _make_message()
        msg["payload"]["headers"] = [h for h in msg["payload"]["headers"]
                                      if h["name"] != "Subject"]
        result = GmailClient.parse_email(msg)
        assert result["subject"] == "(no subject)"

    def test_missing_sender_defaults(self):
        msg = _make_message()
        msg["payload"]["headers"] = [h for h in msg["payload"]["headers"]
                                      if h["name"] != "From"]
        result = GmailClient.parse_email(msg)
        assert result["sender"] == "(unknown sender)"


# ---------------------------------------------------------------------------
# Multipart email — text/plain preferred over text/html
# ---------------------------------------------------------------------------

class TestMultipartEmail:
    def test_plain_part_preferred_over_html(self):
        parts = [
            {"mimeType": "text/plain", "body": {"data": _b64("Plain body")}},
            {"mimeType": "text/html",  "body": {"data": _b64("<p>HTML body</p>")}},
        ]
        msg = _make_message(mime_type="multipart/alternative", parts=parts)
        result = GmailClient.parse_email(msg)
        assert result["body"] == "Plain body"

    def test_html_stripped_when_no_plain_part(self):
        parts = [
            {"mimeType": "text/html", "body": {"data": _b64("<p>Hello <b>world</b></p>")}},
        ]
        msg = _make_message(mime_type="multipart/alternative", parts=parts)
        result = GmailClient.parse_email(msg)
        assert "Hello" in result["body"]
        assert "<p>" not in result["body"]
        assert "<b>" not in result["body"]

    def test_nested_multipart_resolved(self):
        """multipart/mixed wrapping multipart/alternative."""
        inner_parts = [
            {"mimeType": "text/plain", "body": {"data": _b64("Nested plain text")}},
        ]
        outer_parts = [
            {"mimeType": "multipart/alternative", "parts": inner_parts},
        ]
        msg = _make_message(mime_type="multipart/mixed", parts=outer_parts)
        result = GmailClient.parse_email(msg)
        assert result["body"] == "Nested plain text"

    def test_empty_parts_returns_empty_body(self):
        msg = _make_message(mime_type="multipart/alternative", parts=[])
        result = GmailClient.parse_email(msg)
        assert result["body"] == ""


# ---------------------------------------------------------------------------
# HTML stripping
# ---------------------------------------------------------------------------

class TestStripHtml:
    def test_removes_tags(self):
        assert _strip_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_decodes_html_entities(self):
        assert ">" in _strip_html("&gt;")

    def test_collapses_whitespace(self):
        result = _strip_html("<p>Line one</p>\n<p>Line two</p>")
        assert "  " not in result

    def test_empty_string(self):
        assert _strip_html("") == ""


# ---------------------------------------------------------------------------
# Return value structure
# ---------------------------------------------------------------------------

def test_parse_email_returns_all_required_keys():
    msg = _make_message()
    result = GmailClient.parse_email(msg)
    assert set(result.keys()) == {"subject", "sender", "timestamp", "body"}


def test_parse_email_is_static_method():
    """parse_email should be callable without a GmailClient instance."""
    msg = _make_message()
    result = GmailClient.parse_email(msg)
    assert isinstance(result, dict)
