"""Tests for Story 1.3: Configuration Loading & Startup Validation."""
import os
from pathlib import Path

import pytest

from open_fleet.config import Config, load
from open_fleet.exceptions import ConfigError

# Minimal set of required env vars for a valid config
_REQUIRED_VARS = {
    "SLACK_BOT_TOKEN": "xoxb-test",
    "SLACK_APP_TOKEN": "xapp-test",
    "GEMINI_API_KEY": "gemini-test-key",
}


@pytest.fixture()
def token_file(tmp_path: Path) -> Path:
    """Create a temporary token.json file."""
    token = tmp_path / "token.json"
    token.write_text('{"token": "fake"}')
    return token


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Remove any real env vars that could bleed into tests."""
    for key in {*_REQUIRED_VARS, "LM_STUDIO_BASE_URL", "LM_STUDIO_TIMEOUT_SECS",
                "GMAIL_TOKEN_PATH", "LOG_DIR"}:
        monkeypatch.delenv(key, raising=False)


def _set_required(monkeypatch, token_path: Path):
    for k, v in _REQUIRED_VARS.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("GMAIL_TOKEN_PATH", str(token_path))


# --- Required variable validation ---

def test_missing_single_required_var_raises(monkeypatch, token_file):
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-test")
    monkeypatch.setenv("GEMINI_API_KEY", "key")
    monkeypatch.setenv("GMAIL_TOKEN_PATH", str(token_file))

    with pytest.raises(ConfigError) as exc_info:
        load(env_file=None)

    assert "SLACK_BOT_TOKEN" in str(exc_info.value)
    assert "xoxb-" in str(exc_info.value)


def test_missing_multiple_required_vars_raises(monkeypatch, token_file):
    monkeypatch.setenv("GMAIL_TOKEN_PATH", str(token_file))

    with pytest.raises(ConfigError) as exc_info:
        load(env_file=None)

    msg = str(exc_info.value)
    assert "SLACK_BOT_TOKEN" in msg
    assert "SLACK_APP_TOKEN" in msg
    assert "GEMINI_API_KEY" in msg


# --- token.json validation ---

def test_missing_token_json_raises(monkeypatch, tmp_path):
    _set_required(monkeypatch, tmp_path / "token.json")  # does not exist

    with pytest.raises(ConfigError) as exc_info:
        load(env_file=None)

    assert "setup_gmail_auth.py" in str(exc_info.value)


# --- Successful load ---

def test_returns_config_with_typed_attributes(monkeypatch, token_file):
    _set_required(monkeypatch, token_file)

    cfg = load(env_file=None)

    assert isinstance(cfg, Config)
    assert cfg.slack_bot_token == "xoxb-test"
    assert cfg.slack_app_token == "xapp-test"
    assert cfg.gemini_api_key == "gemini-test-key"
    assert cfg.gmail_token_path == token_file


def test_optional_vars_use_defaults(monkeypatch, token_file):
    _set_required(monkeypatch, token_file)

    cfg = load(env_file=None)

    assert cfg.lm_studio_base_url == "http://localhost:1234/v1"
    assert cfg.lm_studio_timeout_secs == 30
    assert cfg.log_dir == Path("logs")


def test_optional_vars_overridden(monkeypatch, token_file):
    _set_required(monkeypatch, token_file)
    monkeypatch.setenv("LM_STUDIO_BASE_URL", "http://192.168.1.5:1234/v1")
    monkeypatch.setenv("LM_STUDIO_TIMEOUT_SECS", "45")
    monkeypatch.setenv("LOG_DIR", "/var/log/open_fleet")

    cfg = load(env_file=None)

    assert cfg.lm_studio_base_url == "http://192.168.1.5:1234/v1"
    assert cfg.lm_studio_timeout_secs == 45
    assert cfg.log_dir == Path("/var/log/open_fleet")


def test_invalid_timeout_raises(monkeypatch, token_file):
    _set_required(monkeypatch, token_file)
    monkeypatch.setenv("LM_STUDIO_TIMEOUT_SECS", "not-a-number")

    with pytest.raises(ConfigError) as exc_info:
        load(env_file=None)

    assert "LM_STUDIO_TIMEOUT_SECS" in str(exc_info.value)


# --- Config injection pattern ---

def test_config_is_frozen(monkeypatch, token_file):
    """Config must be immutable so modules can't mutate shared state."""
    _set_required(monkeypatch, token_file)
    cfg = load(env_file=None)

    with pytest.raises((AttributeError, TypeError)):
        cfg.slack_bot_token = "modified"  # type: ignore[misc]
