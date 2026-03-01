# src/open_fleet/tools/gmail.py
"""Gmail client — authentication credential loading.

Story 2.1 implements credential loading and GmailClient initialisation.
Stories 2.2-2.4 add fetch, parse, and rate-limit handling.
"""
from __future__ import annotations

import logging
from pathlib import Path

from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from open_fleet.exceptions import GmailAuthError

logger = logging.getLogger("open_fleet.tools.gmail")

# OAuth scopes required — read-only access to Gmail messages
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailClient:
    """Thin wrapper around the Gmail API with async-friendly design.

    Credential loading happens at construction time. All network I/O
    (fetch, parse) is added in Stories 2.2–2.4.

    Args:
        token_path: Path to the token.json file produced by setup_gmail_auth.py.

    Raises:
        GmailAuthError: If token.json is missing, corrupt, or the refresh fails.
    """

    def __init__(self, token_path: Path) -> None:
        self._token_path = Path(token_path)
        self._creds: Credentials = self._load_credentials()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

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
