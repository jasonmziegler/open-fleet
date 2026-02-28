# src/open_fleet/exceptions.py
"""Typed exception hierarchy for open-fleet.

All project exceptions inherit from OpenFleetError. No other module
in the project defines custom exception classes.
"""


class OpenFleetError(Exception):
    """Base class for all open-fleet exceptions."""


# --- Gmail exceptions ---

class GmailError(OpenFleetError):
    """Base class for all Gmail-related failures."""


class GmailAuthError(GmailError):
    """Gmail OAuth token is missing, corrupt, or the refresh failed."""


class GmailRateLimitError(GmailError):
    """Gmail API rate limit exceeded after all retry attempts."""


class GmailFetchError(GmailError):
    """Non-rate-limit Gmail API error (network timeout, 5xx, etc.)."""


# --- LLM exceptions ---

class LLMError(OpenFleetError):
    """Base class for all LLM-related failures."""


class LLMTimeoutError(LLMError):
    """LLM provider did not respond within the configured timeout."""


class LLMValidationError(LLMError):
    """LLM response failed Pydantic schema validation."""


class LLMProviderError(LLMError):
    """LLM provider is unreachable or returned an unexpected error."""


# --- Config exceptions ---

class ConfigError(OpenFleetError):
    """A required configuration value is missing or invalid."""
