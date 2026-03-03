"""Tests for Story 3.2: LM Studio provider integration."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from open_fleet.exceptions import LLMProviderError, LLMTimeoutError, LLMValidationError
from open_fleet.llm.lmstudio import (
    LMStudioProvider,
    PROVIDER_NAME,
    _build_user_message,
    _extract_json,
)
from open_fleet.llm.schemas import ExtractionResult


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

BASE_URL = "http://localhost:1234/v1"

_VALID_RESULT = {
    "action_items": [
        {
            "description": "Review proposal",
            "client": "Acme",
            "sender": "alice@acme.com",
            "email_timestamp": "2026-03-01T09:00:00+00:00",
            "deadline": None,
            "priority": "urgent",
            "sentiment": "neutral",
            "context": "Please review the attached proposal.",
        }
    ],
    "emails_scanned": 3,
    "timeframe": "last 24 hours",
}

_VALID_EMAIL = {
    "subject": "Proposal review needed",
    "sender": "alice@acme.com",
    "timestamp": "2026-03-01T09:00:00+00:00",
    "body": "Please review the attached proposal by EOD Friday.",
}


def _lm_response(content: str) -> dict:
    """Build a minimal OpenAI-compatible chat completion response."""
    return {
        "choices": [{"message": {"role": "assistant", "content": content}}]
    }


def _provider() -> LMStudioProvider:
    return LMStudioProvider(base_url=BASE_URL, timeout_secs=30)


# ---------------------------------------------------------------------------
# _extract_json
# ---------------------------------------------------------------------------

class TestExtractJson:
    def test_parses_plain_json(self):
        result = _extract_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_strips_json_code_fence(self):
        result = _extract_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_strips_plain_code_fence(self):
        result = _extract_json('```\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_handles_whitespace(self):
        result = _extract_json('  \n{"key": "value"}\n  ')
        assert result == {"key": "value"}


# ---------------------------------------------------------------------------
# _build_user_message
# ---------------------------------------------------------------------------

class TestBuildUserMessage:
    def test_includes_timeframe(self):
        msg = _build_user_message([_VALID_EMAIL], "last 24 hours")
        assert "last 24 hours" in msg

    def test_includes_email_count(self):
        msg = _build_user_message([_VALID_EMAIL, _VALID_EMAIL], "today")
        assert "2" in msg

    def test_includes_sender_and_subject(self):
        msg = _build_user_message([_VALID_EMAIL], "today")
        assert "alice@acme.com" in msg
        assert "Proposal review needed" in msg

    def test_includes_body(self):
        msg = _build_user_message([_VALID_EMAIL], "today")
        assert "review the attached proposal" in msg


# ---------------------------------------------------------------------------
# Successful extraction
# ---------------------------------------------------------------------------

class TestExtractSuccess:
    def test_returns_extraction_result(self):
        provider = _provider()
        response_content = json.dumps(_VALID_RESULT)

        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(response_content)):
            result = asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        assert isinstance(result, ExtractionResult)
        assert result.emails_scanned == 3
        assert len(result.action_items) == 1

    def test_accepts_json_in_code_fence(self):
        provider = _provider()
        fenced = f"```json\n{json.dumps(_VALID_RESULT)}\n```"

        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(fenced)):
            result = asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        assert isinstance(result, ExtractionResult)

    def test_sends_two_message_prompt(self):
        provider = _provider()
        captured = []

        async def mock_post(url, payload):
            captured.append(payload)
            return _lm_response(json.dumps(_VALID_RESULT))

        with patch.object(provider, "_post", side_effect=mock_post):
            asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        messages = captured[0]["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_posts_to_chat_completions_endpoint(self):
        provider = _provider()
        captured_urls = []

        async def mock_post(url, payload):
            captured_urls.append(url)
            return _lm_response(json.dumps(_VALID_RESULT))

        with patch.object(provider, "_post", side_effect=mock_post):
            asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        assert captured_urls[0] == f"{BASE_URL}/chat/completions"

    def test_provider_name_is_lmstudio_lowercase(self):
        assert PROVIDER_NAME == "lmstudio"


# ---------------------------------------------------------------------------
# Timeout handling
# ---------------------------------------------------------------------------

class TestTimeout:
    def test_timeout_raises_llm_timeout_error(self):
        provider = LMStudioProvider(base_url=BASE_URL, timeout_secs=30)

        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError()):
            with pytest.raises(LLMTimeoutError):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_timeout_error_mentions_timeout_value(self):
        provider = LMStudioProvider(base_url=BASE_URL, timeout_secs=45)

        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError()):
            with pytest.raises(LLMTimeoutError) as exc_info:
                asyncio.run(provider.extract([_VALID_EMAIL]))

        assert "45" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Connection error
# ---------------------------------------------------------------------------

class TestConnectionError:
    def test_connection_refused_raises_provider_error(self):
        import aiohttp
        provider = _provider()

        async def failing_post(url, payload):
            raise LLMProviderError("LM Studio is unreachable")

        with patch.object(provider, "_post", side_effect=failing_post):
            with pytest.raises(LLMProviderError, match="unreachable"):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_http_error_status_raises_provider_error(self):
        provider = _provider()

        async def bad_status_post(url, payload):
            raise LLMProviderError("LM Studio returned HTTP 500")

        with patch.object(provider, "_post", side_effect=bad_status_post):
            with pytest.raises(LLMProviderError):
                asyncio.run(provider.extract([_VALID_EMAIL]))


# ---------------------------------------------------------------------------
# Validation error
# ---------------------------------------------------------------------------

class TestValidationError:
    def test_invalid_schema_raises_llm_validation_error(self):
        provider = _provider()
        bad_result = {"action_items": [{"bad": "schema"}], "emails_scanned": 1}

        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(bad_result))):
            with pytest.raises(LLMValidationError):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_malformed_json_raises_llm_validation_error(self):
        provider = _provider()

        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response("this is not json")):
            with pytest.raises(LLMValidationError, match="parsed"):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_missing_choices_raises_llm_validation_error(self):
        provider = _provider()

        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value={"no_choices": True}):
            with pytest.raises(LLMValidationError, match="parsed"):
                asyncio.run(provider.extract([_VALID_EMAIL]))


# ---------------------------------------------------------------------------
# Config injection
# ---------------------------------------------------------------------------

class TestConfigInjection:
    def test_base_url_trailing_slash_normalised(self):
        provider = LMStudioProvider(base_url="http://localhost:1234/v1/", timeout_secs=30)
        captured = []

        async def mock_post(url, payload):
            captured.append(url)
            return _lm_response(json.dumps(_VALID_RESULT))

        with patch.object(provider, "_post", side_effect=mock_post):
            asyncio.run(provider.extract([_VALID_EMAIL]))

        assert not captured[0].startswith("http://localhost:1234/v1//")

    def test_does_not_read_env_vars_directly(self):
        """Provider must not import or use os.environ / dotenv."""
        import ast, pathlib
        source = pathlib.Path("src/open_fleet/llm/lmstudio.py").read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("dotenv", "os.environ"), \
                        f"lmstudio.py imports {alias.name}"
