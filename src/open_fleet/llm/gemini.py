# src/open_fleet/llm/gemini.py
"""Gemini fallback provider — cloud inference via google-genai SDK.

Config injection: api_key is passed as a constructor argument.
This module never reads environment variables directly.

Provider name string is always "gemini" (lowercase, no variations).
Email content is transmitted only over HTTPS to Google's API (NFR8).
"""
from __future__ import annotations

import logging
import time

from google import genai
from google.genai import types
from pydantic import ValidationError

from open_fleet.exceptions import LLMProviderError, LLMValidationError
from open_fleet.llm.lmstudio import _SYSTEM_PROMPT, _build_user_message, _extract_json
from open_fleet.llm.schemas import ExtractionResult

logger = logging.getLogger("open_fleet.llm.gemini")

PROVIDER_NAME = "gemini"
_MODEL = "gemini-2.0-flash"


class GeminiProvider:
    """Sends batched emails to the Gemini API for extraction.

    Args:
        api_key: Gemini API key (from Google AI Studio).
    """

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    async def extract(self, email_batch: list[dict], timeframe: str = "last 24 hours") -> ExtractionResult:
        """Extract action items from a batch of parsed email dicts.

        Uses the same two-message prompt structure as LMStudioProvider:
        system instruction defines the extraction schema; user content
        contains the serialised email batch.

        Email content is sent over HTTPS to Google's API only (NFR8).

        Args:
            email_batch: List of dicts with keys: subject, sender, timestamp, body.
            timeframe:   Human-readable timeframe string included in the prompt.

        Returns:
            Validated ExtractionResult.

        Raises:
            LLMProviderError:   Gemini API call failed (network, auth, quota).
            LLMValidationError: Response JSON failed ExtractionResult schema validation.
        """
        user_content = _build_user_message(email_batch, timeframe)
        config = types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.1,
            response_mime_type="application/json",
        )

        start = time.monotonic()
        logger.info(
            "Gemini extraction started",
            extra={"provider": PROVIDER_NAME, "email_count": len(email_batch)},
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=_MODEL,
                contents=user_content,
                config=config,
            )
        except Exception as exc:
            raise LLMProviderError(
                f"Gemini API call failed: {exc}"
            ) from exc

        # Parse and validate
        try:
            if response.text is None:
                raise TypeError("Gemini response text was None")
            json_dict = _extract_json(response.text)
            result = ExtractionResult.model_validate(json_dict)
        except (ValueError, TypeError) as exc:
            raise LLMValidationError(
                f"Gemini response could not be parsed: {exc}"
            ) from exc
        except ValidationError as exc:
            raise LLMValidationError(
                f"Gemini response failed schema validation: {exc}"
            ) from exc

        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "Gemini extraction complete",
            extra={
                "provider": PROVIDER_NAME,
                "email_count": len(email_batch),
                "action_item_count": len(result.action_items),
                "duration_ms": duration_ms,
                "error": None,
            },
        )
        return result
