# src/open_fleet/tools/gmail.py
"""Gmail client — authentication, fetch, and pagination.

Story 2.1: credential loading and GmailClient initialisation.
Story 2.2: fetch_emails() with timeframe parsing and nextPageToken pagination.
Stories 2.3-2.4: parse_email() and rate-limit handling.
"""
from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from open_fleet.exceptions import GmailAuthError, GmailFetchError

logger = logging.getLogger("open_fleet.tools.gmail")

# OAuth scopes required — read-only access to Gmail messages
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Gmail API page size (maximum allowed)
_PAGE_SIZE = 500


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

    async def fetch_emails(self, timeframe: str) -> list[dict]:
        """Fetch all full message dicts for emails within the given timeframe.

        Paginates until all matching messages are retrieved (no artificial cap).
        Synchronous google-api-python-client calls are wrapped in
        run_in_executor so the asyncio event loop is never blocked.

        Args:
            timeframe: Human-readable window string, e.g. "last 24 hours".

        Returns:
            List of full Gmail message resource dicts (format="full").

        Raises:
            GmailFetchError: On any non-rate-limit API or network error.
            ValueError: If the timeframe string cannot be parsed.
        """
        since_dt = _parse_timeframe(timeframe)
        query = f"after:{int(since_dt.timestamp())}"
        logger.info(
            "Fetching emails",
            extra={"timeframe": timeframe, "query": query},
        )

        loop = asyncio.get_event_loop()
        service = await loop.run_in_executor(None, self._build_service)

        # --- Collect all message IDs via paginated list ---
        message_stubs: list[dict] = []
        page_token: str | None = None

        while True:
            try:
                result = await loop.run_in_executor(
                    None,
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
                )
            except Exception as exc:
                raise GmailFetchError(
                    f"Gmail API list request failed: {exc}"
                ) from exc

            message_stubs.extend(result.get("messages", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        logger.info("Gmail list complete", extra={"message_count": len(message_stubs)})

        # --- Fetch full content for each message ID ---
        full_messages: list[dict] = []
        for stub in message_stubs:
            try:
                msg = await loop.run_in_executor(
                    None,
                    lambda mid=stub["id"]: (
                        service.users()
                        .messages()
                        .get(userId="me", id=mid, format="full")
                        .execute()
                    ),
                )
            except Exception as exc:
                raise GmailFetchError(
                    f"Gmail API get request failed for message {stub['id']}: {exc}"
                ) from exc

            full_messages.append(msg)

        return full_messages

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
