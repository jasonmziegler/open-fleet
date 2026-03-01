"""Tests for Story 2.1: Gmail OAuth credential loading."""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from open_fleet.exceptions import GmailAuthError
from open_fleet.tools.gmail import GmailClient, GMAIL_SCOPES


def _write_token(path: Path, extra: dict | None = None) -> None:
    """Write a minimal valid-looking token.json."""
    data = {
        "token": "ya29.access-token",
        "refresh_token": "1//refresh-token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "client-id.apps.googleusercontent.com",
        "client_secret": "client-secret",
        "scopes": GMAIL_SCOPES,
    }
    if extra:
        data.update(extra)
    path.write_text(json.dumps(data), encoding="utf-8")


# --- Missing token.json ---

def test_raises_auth_error_when_token_missing(tmp_path):
    with pytest.raises(GmailAuthError) as exc_info:
        GmailClient(token_path=tmp_path / "token.json")

    assert "setup_gmail_auth.py" in str(exc_info.value)


# --- Corrupt token.json ---

def test_raises_auth_error_on_corrupt_token(tmp_path):
    token = tmp_path / "token.json"
    token.write_text("not valid json {{", encoding="utf-8")

    with pytest.raises(GmailAuthError) as exc_info:
        GmailClient(token_path=token)

    assert "corrupt" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()


# --- Valid, non-expired token ---

def test_loads_valid_token_without_refresh(tmp_path):
    token = tmp_path / "token.json"
    _write_token(token)

    mock_creds = MagicMock()
    mock_creds.expired = False
    mock_creds.valid = True

    with patch("open_fleet.tools.gmail.Credentials.from_authorized_user_file",
               return_value=mock_creds):
        client = GmailClient(token_path=token)

    assert client.credentials is mock_creds
    mock_creds.refresh.assert_not_called()


# --- Expired token, successful refresh ---

def test_refreshes_expired_token_and_persists(tmp_path):
    token = tmp_path / "token.json"
    _write_token(token)

    mock_creds = MagicMock()
    mock_creds.expired = True
    mock_creds.refresh_token = "1//refresh-token"
    mock_creds.to_json.return_value = '{"refreshed": true}'

    with patch("open_fleet.tools.gmail.Credentials.from_authorized_user_file",
               return_value=mock_creds), \
         patch("open_fleet.tools.gmail.Request"):
        client = GmailClient(token_path=token)

    mock_creds.refresh.assert_called_once()
    # Verify refreshed token is written back to disk
    assert json.loads(token.read_text())["refreshed"] is True


# --- Expired token, refresh fails ---

def test_raises_auth_error_on_refresh_failure(tmp_path):
    from google.auth.exceptions import RefreshError

    token = tmp_path / "token.json"
    _write_token(token)

    mock_creds = MagicMock()
    mock_creds.expired = True
    mock_creds.refresh_token = "1//refresh-token"
    mock_creds.refresh.side_effect = RefreshError("invalid_grant")

    with patch("open_fleet.tools.gmail.Credentials.from_authorized_user_file",
               return_value=mock_creds), \
         patch("open_fleet.tools.gmail.Request"), \
         pytest.raises(GmailAuthError) as exc_info:
        GmailClient(token_path=token)

    assert "refresh failed" in str(exc_info.value).lower()
    assert "setup_gmail_auth.py" in str(exc_info.value)


# --- Scopes ---

def test_gmail_scopes_are_read_only():
    assert GMAIL_SCOPES == ["https://www.googleapis.com/auth/gmail.readonly"]
