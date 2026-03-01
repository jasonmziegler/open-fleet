"""Tests for Story 1.2: Typed Exception Hierarchy."""
import pytest
from open_fleet.exceptions import (
    OpenFleetError,
    GmailError, GmailAuthError, GmailRateLimitError, GmailFetchError,
    LLMError, LLMTimeoutError, LLMValidationError, LLMProviderError,
    ConfigError,
)


def test_open_fleet_error_is_exception():
    assert issubclass(OpenFleetError, Exception)


def test_gmail_hierarchy():
    assert issubclass(GmailError, OpenFleetError)
    assert issubclass(GmailAuthError, GmailError)
    assert issubclass(GmailRateLimitError, GmailError)
    assert issubclass(GmailFetchError, GmailError)


def test_llm_hierarchy():
    assert issubclass(LLMError, OpenFleetError)
    assert issubclass(LLMTimeoutError, LLMError)
    assert issubclass(LLMValidationError, LLMError)
    assert issubclass(LLMProviderError, LLMError)


def test_config_error_hierarchy():
    assert issubclass(ConfigError, OpenFleetError)


def test_catching_base_catches_all_subclasses():
    subclasses = [
        GmailAuthError, GmailRateLimitError, GmailFetchError,
        LLMTimeoutError, LLMValidationError, LLMProviderError,
        ConfigError,
    ]
    for exc_class in subclasses:
        with pytest.raises(OpenFleetError):
            raise exc_class("test")


def test_exceptions_carry_message():
    err = GmailAuthError("token.json not found")
    assert str(err) == "token.json not found"

    err = LLMTimeoutError("elapsed=31s, timeout=30s")
    assert str(err) == "elapsed=31s, timeout=30s"

    err = ConfigError("SLACK_BOT_TOKEN is missing")
    assert str(err) == "SLACK_BOT_TOKEN is missing"
