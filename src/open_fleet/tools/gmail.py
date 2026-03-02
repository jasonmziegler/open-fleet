# src/open_fleet/tools/gmail.py
"""Gmail client — authentication, fetch, pagination, and parsing.

Story 2.1: credential loading and GmailClient initialisation.
Story 2.2: fetch_emails() with timeframe parsing and nextPageToken pagination.
Story 2.3: parse_email() — subject, sender, timestamp, body extraction.
Story 2.4: rate-limit handling.
"""
from __future__ import annotations

import asyncio
import base64
import html
import logging
import re
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from open_fleet.exceptions import GmailAuthError, GmailFetchError, GmailRateLimitError

logger = logging.getLogger("open_fleet.tools.gmail")

# OAuth scopes required — read-only access to Gmail messages
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Gmail API page size (maximum allowed)
_PAGE_SIZE = 500

# Exponential backoff delays (seconds) for HTTP 429 retries: 1s, 2s, 4s
_RETRY_DELAYS = [1, 2, 4]

# Notify callback type: accepts a message string, returns an awaitable
_NotifyFn = Callable[[str], Awaitable[None]]


async def _execute_with_retry(
    sync_fn: Callable,
    notify: _NotifyFn | None,
    label: str,
) -> dict:
    """Run a synchronous Gmail API call with exponential backoff on HTTP 429.

    Args:
        sync_fn: Zero-argument callable wrapping the .execute() call.
        notify:  Optional async callback to send a Slack warning before each retry.
        label:   Short description used in error messages (e.g. "list", "get msg123").

    Returns:
        The dict returned by the Gmail API on success.

    Raises:
        GmailRateLimitError: All retry attempts exhausted on HTTP 429.
        GmailFetchError:     Any non-429 HTTP error or unexpected exception.
    """
    loop = asyncio.get_running_loop()
    attempts = 0

    for attempt_idx in range(len(_RETRY_DELAYS) + 1):
        if attempt_idx > 0:
            delay = _RETRY_DELAYS[attempt_idx - 1]
            warning = (
                f"⚠️ Gmail API rate limit hit — extraction will retry in {delay} seconds"
            )
            logger.warning(warning)
            if notify is not None:
                await notify(warning)
            await asyncio.sleep(delay)

        attempts += 1
        try:
            return await loop.run_in_executor(None, sync_fn)
        except HttpError as exc:
            if exc.resp.status == 429:
                continue  # retry with backoff
            raise GmailFetchError(
                f"Gmail API {label} failed (HTTP {exc.resp.status}): {exc.reason}"
            ) from exc
        except Exception as exc:
            raise GmailFetchError(
                f"Gmail API {label} failed: {exc}"
            ) from exc

    raise GmailRateLimitError(
        f"Gmail API rate limit — extraction could not complete after {attempts} attempts"
    )


# ---------------------------------------------------------------------------
# HTML stripping (for text/html fallback bodies)
# ---------------------------------------------------------------------------

class _HTMLStripper(HTMLParser):
    """Minimal HTML → plain-text converter."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def _strip_html(html_content: str) -> str:
    stripper = _HTMLStripper()
    stripper.feed(html.unescape(html_content))
    return re.sub(r"\s+", " ", stripper.get_text()).strip()


def _decode_body(data: str) -> str:
    """Decode a base64url-encoded Gmail message body part."""
    if not data:
        return ""
    # Gmail uses base64url without padding — add padding before decoding
    try:
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_body(payload: dict) -> str:
    """Recursively extract the best available plain-text body from a payload."""
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        return _decode_body(payload.get("body", {}).get("data", ""))

    if mime_type == "text/html":
        return _strip_html(_decode_body(payload.get("body", {}).get("data", "")))

    if mime_type.startswith("multipart/"):
        parts = payload.get("parts", [])

        # Prefer text/plain
        for part in parts:
            if part.get("mimeType") == "text/plain":
                return _decode_body(part.get("body", {}).get("data", ""))

        # Fall back to text/html
        for part in parts:
            if part.get("mimeType") == "text/html":
                return _strip_html(_decode_body(part.get("body", {}).get("data", "")))

        # Recurse into nested multipart parts (e.g. multipart/mixed wrapping multipart/alternative)
        for part in parts:
            if part.get("mimeType", "").startswith("multipart/"):
                result = _extract_body(part)
                if result:
                    return result

    return ""


def _parse_timeframe(timeframe: str) -> datetime:
    """Convert a timeframe string to a UTC datetime marking the start of the window.

    Supported patterns:
      - "last N hours"              e.g. "last 24 hours", "last 2 hours"
      - "last N days"               e.g. "last 3 days"
      - "today"                     since midnight today (UTC)
      - "since yesterday"           since midnight yesterday (UTC)
      - "since yesterday [H]pm/am"  e.g. "since yesterday 5pm", "since yesterday 9am"

    Raises:
        ValueError: If the timeframe string does not match any known pattern.
    """
    now = datetime.now(timezone.utc)
    tf = timeframe.lower().strip()

    # "last N hours"
    m = re.match(r"last\s+(\d+)\s+hours?", tf)
    if m:
        return now - timedelta(hours=int(m.group(1)))

    # "last N days"
    m = re.match(r"last\s+(\d+)\s+days?", tf)
    if m:
        return now - timedelta(days=int(m.group(1)))

    # "today"
    if tf == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)

    # "since yesterday" (midnight)
    if tf == "since yesterday":
        yesterday = now - timedelta(days=1)
        return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

    # "since yesterday H[:MM][am|pm]"
    m = re.match(r"since\s+yesterday\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)", tf)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2) or 0)
        ampm = m.group(3)
        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        yesterday = now - timedelta(days=1)
        return yesterday.replace(hour=hour, minute=minute, second=0, microsecond=0)

    raise ValueError(
        f"Cannot parse timeframe: {timeframe!r}. "
        "Expected formats: 'last 24 hours', 'last 3 days', 'today', "
        "'since yesterday', 'since yesterday 5pm'."
    )


class GmailClient:
    """Async-friendly Gmail API wrapper.

    Args:
        token_path: Path to the token.json file produced by setup_gmail_auth.py.

    Raises:
        GmailAuthError: If token.json is missing, corrupt, or the refresh fails.
    """

    def __init__(self, token_path: Path) -> None:
        self._token_path = Path(token_path)
        self._creds: Credentials = self._load_credentials()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch_emails(
        self,
        timeframe: str,
        notify: _NotifyFn | None = None,
    ) -> list[dict]:
        """Fetch all full message dicts for emails within the given timeframe.

        Paginates until all matching messages are retrieved (no artificial cap).
        Synchronous google-api-python-client calls are wrapped in
        run_in_executor so the asyncio event loop is never blocked.

        HTTP 429 (rate limit) errors trigger exponential backoff with delays of
        1s, 2s, 4s. Before each retry, `notify` is called (if provided) so the
        caller can surface a warning to the user (e.g. via Slack).

        Args:
            timeframe: Human-readable window string, e.g. "last 24 hours".
            notify:    Optional async callback for rate-limit warnings.
                       Signature: async def notify(message: str) -> None.

        Returns:
            List of full Gmail message resource dicts (format="full").

        Raises:
            GmailRateLimitError: All retry attempts exhausted on HTTP 429.
            GmailFetchError:     Any non-rate-limit API or network error.
            ValueError:          If the timeframe string cannot be parsed.
        """
        since_dt = _parse_timeframe(timeframe)
        query = f"after:{int(since_dt.timestamp())}"
        logger.info(
            "Fetching emails",
            extra={"timeframe": timeframe, "query": query},
        )

        loop = asyncio.get_running_loop()
        service = await loop.run_in_executor(None, self._build_service)

        # --- Collect all message IDs via paginated list ---
        message_stubs: list[dict] = []
        page_token: str | None = None

        while True:
            result = await _execute_with_retry(
                lambda pt=page_token: (
                    service.users()
                    .messages()
                    .list(
                        userId="me",
                        q=query,
                        pageToken=pt,
                        maxResults=_PAGE_SIZE,
                    )
                    .execute()
                ),
                notify,
                label="list",
            )
            message_stubs.extend(result.get("messages", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        logger.info("Gmail list complete", extra={"message_count": len(message_stubs)})

        # --- Fetch full content for each message ID ---
        full_messages: list[dict] = []
        for stub in message_stubs:
            msg = await _execute_with_retry(
                lambda mid=stub["id"]: (
                    service.users()
                    .messages()
                    .get(userId="me", id=mid, format="full")
                    .execute()
                ),
                notify,
                label=f"get {stub['id']}",
            )
            full_messages.append(msg)

        return full_messages

    @staticmethod
    def parse_email(message: dict) -> dict:
        """Parse a raw Gmail API message dict into a structured dict.

        Extracts subject, sender (display name + address from the From: header),
        timestamp (UTC ISO8601), and plain-text body.

        Body extraction priority:
          1. text/plain part (used as-is)
          2. text/html part (HTML tags stripped)
          3. Empty string if neither is present

        Raw body content is returned in memory only — it is never written to disk
        (NFR7, FR33). Callers must not persist the returned 'body' value.

        Args:
            message: Full Gmail API message resource dict (format="full").

        Returns:
            Dict with keys: subject, sender, timestamp, body.
        """
        payload = message.get("payload", {})
        headers = {
            h["name"].lower(): h["value"]
            for h in payload.get("headers", [])
        }

        subject = headers.get("subject", "(no subject)")
        sender = headers.get("from", "(unknown sender)")

        # internalDate is milliseconds since Unix epoch (UTC)
        internal_date_ms = int(message.get("internalDate", 0))
        timestamp = datetime.fromtimestamp(
            internal_date_ms / 1000, tz=timezone.utc
        ).isoformat()

        body = _extract_body(payload)

        return {
            "subject": subject,
            "sender": sender,
            "timestamp": timestamp,
            "body": body,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_service(self):
        """Build the Gmail API service object (synchronous)."""
        return build("gmail", "v1", credentials=self._creds, cache_discovery=False)

    def _load_credentials(self) -> Credentials:
        """Load and, if necessary, refresh OAuth credentials from token.json."""
        if not self._token_path.exists():
            raise GmailAuthError(
                f"Gmail token not found at '{self._token_path}'. "
                "Run scripts/setup_gmail_auth.py to generate it."
            )

        try:
            creds = Credentials.from_authorized_user_file(
                str(self._token_path), GMAIL_SCOPES
            )
        except (ValueError, KeyError) as exc:
            raise GmailAuthError(
                f"Gmail token at '{self._token_path}' is corrupt or invalid: {exc}"
            ) from exc

        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                self._persist_credentials(creds)
                logger.info("Gmail access token refreshed successfully.")
            except RefreshError as exc:
                raise GmailAuthError(
                    f"Gmail token refresh failed — re-run scripts/setup_gmail_auth.py: {exc}"
                ) from exc
            except TransportError as exc:
                raise GmailAuthError(
                    f"Network error while refreshing Gmail token: {exc}"
                ) from exc

        return creds

    def _persist_credentials(self, creds: Credentials) -> None:
        """Write updated credentials back to token.json."""
        self._token_path.write_text(creds.to_json(), encoding="utf-8")

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def credentials(self) -> Credentials:
        """The current (possibly refreshed) OAuth credentials."""
        return self._creds
