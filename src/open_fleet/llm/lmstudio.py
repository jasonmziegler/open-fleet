# src/open_fleet/llm/lmstudio.py
"""LM Studio provider — local inference via OpenAI-compatible chat/completions API.

Config injection: all settings are passed as constructor arguments.
This module never reads environment variables directly.

Provider name string is always "lmstudio" (lowercase, no variations).
Email content is never written to disk during or after a call (FR32).
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time

import aiohttp
from pydantic import ValidationError

from open_fleet.exceptions import LLMProviderError, LLMTimeoutError, LLMValidationError
from open_fleet.llm.schemas import ExtractionResult

logger = logging.getLogger("open_fleet.llm.lmstudio")

PROVIDER_NAME = "lmstudio"

_SYSTEM_PROMPT = """\
You are an expert email triage assistant. Analyze the provided emails and extract \
every action item that requires a response or follow-up.

For each email that requires action, produce one ActionItem in the JSON output.
Emails with no required action must NOT appear in action_items.

Field rules:
- description: concise description of the action needed
- client: company or person the action relates to (infer from context if not explicit)
- sender: full From: header value (name + address)
- email_timestamp: ISO8601 UTC timestamp from the email
- deadline: ISO8601 UTC datetime if inferable from context ("EOD Friday", "ASAP", etc.), \
otherwise null
- priority: "urgent" if deadline within 24h or explicitly urgent/critical; \
"this_week" if deadline within 7 days or implied soon; "no_deadline" otherwise
- sentiment: "escalated" if sender threatens escalation or CC's management; \
"frustrated" if sender expresses impatience or dissatisfaction; "neutral" otherwise
- context: verbatim excerpt ≤100 characters showing WHY action is needed

Output ONLY valid JSON — no markdown fences, no explanation, nothing else:
{
  "action_items": [...],
  "emails_scanned": <integer — total emails analyzed including those with no action>,
  "timeframe": "<the timeframe string provided in the user message>"
}"""


def _build_user_message(email_batch: list[dict], timeframe: str) -> str:
    """Serialise the email batch into the user prompt."""
    lines = [f"Timeframe: {timeframe}", f"Emails to analyse: {len(email_batch)}", ""]
    for i, email in enumerate(email_batch, start=1):
        lines.append(f"--- Email {i} ---")
        lines.append(f"From: {email.get('sender', '(unknown)')}")
        lines.append(f"Subject: {email.get('subject', '(no subject)')}")
        lines.append(f"Timestamp: {email.get('timestamp', '')}")
        lines.append(f"Body:\n{email.get('body', '')}")
        lines.append("")
    return "\n".join(lines)


def _extract_json(content: str) -> dict:
    """Parse JSON from an LLM response, stripping markdown fences if present."""
    content = content.strip()
    # Strip ```json ... ``` or ``` ... ``` wrappers that LLMs often add
    content = re.sub(r"^```(?:json)?\s*\n?", "", content)
    content = re.sub(r"\n?```\s*$", "", content)
    return json.loads(content.strip())


class LMStudioProvider:
    """Sends batched emails to a local LM Studio instance for extraction.

    Args:
        base_url:     LM Studio base URL, e.g. "http://localhost:1234/v1".
        timeout_secs: Request timeout in seconds (default 30).
    """

    def __init__(self, base_url: str, timeout_secs: int = 30) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_secs = timeout_secs

    async def extract(self, email_batch: list[dict], timeframe: str = "last 24 hours") -> ExtractionResult:
        """Extract action items from a batch of parsed email dicts.

        Args:
            email_batch: List of dicts with keys: subject, sender, timestamp, body.
            timeframe:   Human-readable timeframe string included in the prompt.

        Returns:
            Validated ExtractionResult.

        Raises:
            LLMTimeoutError:    Request exceeded timeout_secs.
            LLMProviderError:   LM Studio is unreachable or returned a non-2xx response.
            LLMValidationError: Response JSON failed ExtractionResult schema validation.
        """
        payload = {
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_message(email_batch, timeframe)},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        url = f"{self._base_url}/chat/completions"
        start = time.monotonic()

        logger.info(
            "LM Studio extraction started",
            extra={"provider": PROVIDER_NAME, "email_count": len(email_batch)},
        )

        try:
            raw = await asyncio.wait_for(
                self._post(url, payload),
                timeout=self._timeout_secs,
            )
        except asyncio.TimeoutError:
            elapsed = round(time.monotonic() - start, 1)
            raise LLMTimeoutError(
                f"LM Studio did not respond within {self._timeout_secs}s "
                f"(elapsed: {elapsed}s)"
            )

        # Parse and validate
        try:
            content = raw["choices"][0]["message"]["content"]
            json_dict = _extract_json(content)
            result = ExtractionResult.model_validate(json_dict)
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise LLMValidationError(
                f"LM Studio response could not be parsed: {exc}"
            ) from exc
        except ValidationError as exc:
            raise LLMValidationError(
                f"LM Studio response failed schema validation: {exc}"
            ) from exc

        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "LM Studio extraction complete",
            extra={
                "provider": PROVIDER_NAME,
                "email_count": len(email_batch),
                "action_item_count": len(result.action_items),
                "duration_ms": duration_ms,
                "error": None,
            },
        )
        return result

    async def _post(self, url: str, payload: dict) -> dict:
        """Execute the HTTP POST to LM Studio (separated for testability)."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status >= 400:
                        body = await resp.text()
                        raise LLMProviderError(
                            f"LM Studio returned HTTP {resp.status}: {body[:200]}"
                        )
                    return await resp.json(content_type=None)
        except aiohttp.ClientConnectorError as exc:
            raise LLMProviderError(
                f"LM Studio is unreachable at {self._base_url}: {exc}"
            ) from exc
        except LLMProviderError:
            raise
        except aiohttp.ClientError as exc:
            raise LLMProviderError(
                f"LM Studio request failed: {exc}"
            ) from exc
