# src/open_fleet/core/orchestrator.py
"""Extraction orchestrator — coordinates the full triage pipeline end-to-end.

Pipeline: GmailClient.fetch_emails() → GmailClient.parse_email() (per message)
          → LLMRouter.run_extraction() → ResponseFormatter.format()

All failure modes are caught and returned as ⚠️/❌ Slack-ready strings.
No imports from adapters/, slack_bolt, or slack_sdk (NFR15, NFR16).
"""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable

from open_fleet.core.response import ResponseFormatter
from open_fleet.exceptions import GmailAuthError, GmailRateLimitError, LLMTimeoutError
from open_fleet.llm.router import LLMRouter
from open_fleet.tools.gmail import GmailClient

logger = logging.getLogger("open_fleet.core.orchestrator")

_NotifyFn = Callable[[str], Awaitable[None]]


class Orchestrator:
    """Coordinates the end-to-end extraction pipeline.

    Args:
        gmail_client: Configured GmailClient for fetching and parsing emails.
        llm_router:   Configured LLMRouter for running LLM extraction.
    """

    def __init__(self, gmail_client: GmailClient, llm_router: LLMRouter) -> None:
        self._gmail = gmail_client
        self._router = llm_router

    async def run(self, timeframe: str, notify: _NotifyFn | None = None) -> list[str]:
        """Execute the full triage pipeline for the given timeframe.

        Args:
            timeframe: Human-readable window string, e.g. "last 24 hours".
            notify:    Optional async callback forwarded to GmailClient and
                       LLMRouter for mid-pipeline Slack warnings (rate-limit
                       retries, LM Studio → Gemini fallback, etc.).

        Returns:
            list[str]: One or more Slack-ready message strings. On success,
            formatted action items grouped by priority. On failure, a single
            ❌ error string — never an empty list, never a partial result.
        """
        try:
            raw_messages = await self._gmail.fetch_emails(timeframe, notify=notify)
            parsed_emails = [GmailClient.parse_email(msg) for msg in raw_messages]
            result = await self._router.run_extraction(parsed_emails, timeframe, notify=notify)
            return ResponseFormatter.format(result)
        except GmailAuthError:
            return ["❌ Gmail authentication expired — run scripts/setup_gmail_auth.py to reconnect"]
        except GmailRateLimitError:
            return ["❌ Gmail API rate limit — extraction could not complete after retries"]
        except LLMTimeoutError:
            return ["❌ LLM extraction failed — both LM Studio and Gemini unavailable"]
        except Exception:
            logger.error("Unexpected error in extraction pipeline", exc_info=True)
            return ["❌ Unexpected error — check logs for details"]
