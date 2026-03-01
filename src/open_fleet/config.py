# src/open_fleet/config.py
"""Configuration loading and startup validation.

Reads .env once at startup and returns a typed Config object.
All other modules receive config values as constructor arguments —
they never import or read .env directly (config injection pattern).

Only main.py imports this module.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from open_fleet.exceptions import ConfigError

# Required environment variables and their expected formats
_REQUIRED: dict[str, str] = {
    "SLACK_BOT_TOKEN": "xoxb-...",
    "SLACK_APP_TOKEN": "xapp-...",
    "GEMINI_API_KEY": "string (from Google AI Studio)",
}

# Optional variables with their defaults
_DEFAULTS: dict[str, str] = {
    "LM_STUDIO_BASE_URL": "http://localhost:1234/v1",
    "LM_STUDIO_TIMEOUT_SECS": "30",
    "GMAIL_TOKEN_PATH": "token.json",
    "LOG_DIR": "logs",
}


@dataclass(frozen=True)
class Config:
    # Required
    slack_bot_token: str
    slack_app_token: str
    gemini_api_key: str
    # Optional with defaults
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_timeout_secs: int = 30
    gmail_token_path: Path = field(default_factory=lambda: Path("token.json"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))


def load(env_file: str | Path | None = ".env") -> Config:
    """Load and validate configuration from environment / .env file.

    Args:
        env_file: Path to .env file. Pass None to skip loading (e.g. in tests
                  that set env vars directly).

    Returns:
        A validated, fully-typed Config instance.

    Raises:
        ConfigError: If any required variable is missing, or if token.json
                     does not exist at the configured path.
    """
    if env_file is not None:
        load_dotenv(env_file, override=False)

    # Validate required variables
    missing = {k: v for k, v in _REQUIRED.items() if not os.environ.get(k)}
    if missing:
        details = ", ".join(
            f"{k} (expected: {fmt})" for k, fmt in missing.items()
        )
        raise ConfigError(f"Missing required environment variable(s): {details}")

    # Resolve optional variables
    lm_studio_base_url = os.environ.get("LM_STUDIO_BASE_URL", _DEFAULTS["LM_STUDIO_BASE_URL"])

    timeout_raw = os.environ.get("LM_STUDIO_TIMEOUT_SECS", _DEFAULTS["LM_STUDIO_TIMEOUT_SECS"])
    try:
        lm_studio_timeout_secs = int(timeout_raw)
    except ValueError:
        raise ConfigError(
            f"LM_STUDIO_TIMEOUT_SECS must be an integer, got: {timeout_raw!r}"
        )

    gmail_token_path = Path(
        os.environ.get("GMAIL_TOKEN_PATH", _DEFAULTS["GMAIL_TOKEN_PATH"])
    )
    log_dir = Path(os.environ.get("LOG_DIR", _DEFAULTS["LOG_DIR"]))

    # Validate token.json exists
    if not gmail_token_path.exists():
        raise ConfigError(
            f"Gmail OAuth token not found at '{gmail_token_path}'. "
            "Run scripts/setup_gmail_auth.py to generate it."
        )

    return Config(
        slack_bot_token=os.environ["SLACK_BOT_TOKEN"],
        slack_app_token=os.environ["SLACK_APP_TOKEN"],
        gemini_api_key=os.environ["GEMINI_API_KEY"],
        lm_studio_base_url=lm_studio_base_url,
        lm_studio_timeout_secs=lm_studio_timeout_secs,
        gmail_token_path=gmail_token_path,
        log_dir=log_dir,
    )
