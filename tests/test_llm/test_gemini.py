"""Tests for Story 3.3: Gemini fallback provider integration."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from open_fleet.exceptions import LLMProviderError, LLMValidationError
from open_fleet.llm.gemini import GeminiProvider, PROVIDER_NAME
from open_fleet.llm.lmstudio import _SYSTEM_PROMPT
from open_fleet.llm.schemas import ExtractionResult


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

_VALID_RESULT = {
    "action_items": [
        {
            "description": "Follow up on contract",
            "client": "Globex",
            "sender": "bob@globex.com",
            "email_timestamp": "2026-03-01T10:00:00+00:00",
            "deadline": None,
            "priority": "this_week",
            "sentiment": "neutral",
            "context": "Can you confirm the contract status?",
        }
    ],
    "emails_scanned": 5,
    "timeframe": "last 24 hours",
}

_VALID_EMAIL = {
    "subject": "Contract status",
    "sender": "bob@globex.com",
    "timestamp": "2026-03-01T10:00:00+00:00",
    "body": "Can you confirm the contract status?",
}


def _mock_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.text = text
    return resp


def _provider() -> GeminiProvider:
    return GeminiProvider(api_key="test-key")


# ---------------------------------------------------------------------------
# Successful extraction
# ---------------------------------------------------------------------------

class TestExtractSuccess:
    def test_returns_extraction_result(self):
        provider = _provider()
        mock_resp = _mock_response(json.dumps(_VALID_RESULT))

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock, return_value=mock_resp
        ):
            result = asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        assert isinstance(result, ExtractionResult)
        assert result.emails_scanned == 5
        assert len(result.action_items) == 1

    def test_accepts_json_in_code_fence(self):
        provider = _provider()
        fenced = f"```json\n{json.dumps(_VALID_RESULT)}\n```"
        mock_resp = _mock_response(fenced)

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock, return_value=mock_resp
        ):
            result = asyncio.run(provider.extract([_VALID_EMAIL]))

        assert isinstance(result, ExtractionResult)

    def test_uses_system_prompt_as_instruction(self):
        provider = _provider()
        captured_configs = []

        async def mock_generate(model, contents, config):
            captured_configs.append(config)
            return _mock_response(json.dumps(_VALID_RESULT))

        with patch.object(provider._client.aio.models, "generate_content",
                          side_effect=mock_generate):
            asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        assert captured_configs[0].system_instruction == _SYSTEM_PROMPT

    def test_user_content_contains_email_data(self):
        provider = _provider()
        captured_contents = []

        async def mock_generate(model, contents, config):
            captured_contents.append(contents)
            return _mock_response(json.dumps(_VALID_RESULT))

        with patch.object(provider._client.aio.models, "generate_content",
                          side_effect=mock_generate):
            asyncio.run(provider.extract([_VALID_EMAIL], "last 24 hours"))

        assert "bob@globex.com" in captured_contents[0]
        assert "Contract status" in captured_contents[0]

    def test_provider_name_is_gemini_lowercase(self):
        assert PROVIDER_NAME == "gemini"

    def test_uses_correct_model(self):
        from open_fleet.llm.gemini import _MODEL
        provider = _provider()
        captured_models = []

        async def mock_generate(model, contents, config):
            captured_models.append(model)
            return _mock_response(json.dumps(_VALID_RESULT))

        with patch.object(provider._client.aio.models, "generate_content",
                          side_effect=mock_generate):
            asyncio.run(provider.extract([_VALID_EMAIL]))

        assert captured_models[0] == _MODEL


# ---------------------------------------------------------------------------
# API failure → LLMProviderError
# ---------------------------------------------------------------------------

class TestProviderError:
    def test_api_exception_raises_provider_error(self):
        provider = _provider()

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock, side_effect=Exception("connection refused")
        ):
            with pytest.raises(LLMProviderError, match="Gemini API call failed"):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_auth_error_raises_provider_error(self):
        provider = _provider()

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock,
            side_effect=Exception("API_KEY_INVALID")
        ):
            with pytest.raises(LLMProviderError):
                asyncio.run(provider.extract([_VALID_EMAIL]))


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------

class TestValidationError:
    def test_invalid_schema_raises_validation_error(self):
        provider = _provider()
        bad = {"action_items": [{"bad": "data"}], "emails_scanned": 1}
        mock_resp = _mock_response(json.dumps(bad))

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock, return_value=mock_resp
        ):
            with pytest.raises(LLMValidationError):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_malformed_json_raises_validation_error(self):
        provider = _provider()
        mock_resp = _mock_response("not json at all")

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock, return_value=mock_resp
        ):
            with pytest.raises(LLMValidationError, match="parsed"):
                asyncio.run(provider.extract([_VALID_EMAIL]))

    def test_none_response_text_raises_validation_error(self):
        provider = _provider()
        mock_resp = _mock_response(None)

        with patch.object(
            provider._client.aio.models, "generate_content",
            new_callable=AsyncMock, return_value=mock_resp
        ):
            with pytest.raises(LLMValidationError):
                asyncio.run(provider.extract([_VALID_EMAIL]))


# ---------------------------------------------------------------------------
# Config injection
# ---------------------------------------------------------------------------

class TestConfigInjection:
    def test_does_not_read_env_vars_directly(self):
        import ast
        import pathlib
        source = pathlib.Path("src/open_fleet/llm/gemini.py").read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name not in ("dotenv", "os"), \
                        f"gemini.py imports {alias.name}"
            if isinstance(node, ast.ImportFrom):
                assert node.module not in ("dotenv", "os"), \
                    f"gemini.py imports from {node.module}"

    def test_api_key_passed_as_constructor_arg(self):
        """Client must be initialised with the provided key, not env vars."""
        with patch("open_fleet.llm.gemini.genai.Client") as mock_client_cls:
            mock_client_cls.return_value = MagicMock()
            GeminiProvider(api_key="my-test-key")

        mock_client_cls.assert_called_once_with(api_key="my-test-key")

    def test_reuses_shared_prompt_from_lmstudio(self):
        """GeminiProvider must use the same system prompt as LMStudioProvider."""
        from open_fleet.llm.gemini import _SYSTEM_PROMPT as gemini_prompt
        from open_fleet.llm.lmstudio import _SYSTEM_PROMPT as lmstudio_prompt
        assert gemini_prompt is lmstudio_prompt
