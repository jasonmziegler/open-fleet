#!/usr/bin/env python3
# scripts/setup_gmail_auth.py
"""One-time Gmail OAuth 2.0 setup script.

Run this once before the first agent launch to generate token.json.
Re-run at any time to refresh an expired token.

Usage:
    python scripts/setup_gmail_auth.py

Requirements:
    - GMAIL_TOKEN_PATH set in .env (default: token.json)
    - credentials.json downloaded from Google Cloud Console and placed
      in the project root (excluded from version control via .gitignore)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ is on the path when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
import os

load_dotenv()

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from open_fleet.tools.gmail import GMAIL_SCOPES

_CREDENTIALS_FILE = Path("credentials.json")
_DEFAULT_TOKEN_PATH = Path("token.json")


def main() -> None:
    token_path = Path(os.environ.get("GMAIL_TOKEN_PATH", str(_DEFAULT_TOKEN_PATH)))

    print(f"Gmail OAuth Setup")
    print(f"Token path: {token_path}")
    print()

    creds: Credentials | None = None

    # Load existing token if present
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), GMAIL_SCOPES)
            print("Existing token.json found.")
        except (ValueError, KeyError):
            print("Existing token.json is corrupt — will re-authenticate.")
            creds = None

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        print("Token is expired — refreshing...")
        try:
            creds.refresh(Request())
            print("Token refreshed successfully.")
        except RefreshError:
            print("Refresh failed — will re-authenticate via browser.")
            creds = None

    # Full OAuth flow if no valid token
    if not creds or not creds.valid:
        if not _CREDENTIALS_FILE.exists():
            print(
                f"\nError: '{_CREDENTIALS_FILE}' not found.\n"
                "Download it from Google Cloud Console:\n"
                "  APIs & Services > Credentials > OAuth 2.0 Client IDs > Download JSON\n"
                f"Save it as '{_CREDENTIALS_FILE}' in the project root."
            )
            sys.exit(1)

        print("Opening browser for Google OAuth consent...")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(_CREDENTIALS_FILE), GMAIL_SCOPES
        )
        creds = flow.run_local_server(port=0)

    # Persist token
    token_path.write_text(creds.to_json(), encoding="utf-8")
    print(f"\ntoken.json written to: {token_path}")
    print("Gmail authentication is ready. You can now start the agent.")


if __name__ == "__main__":
    main()
