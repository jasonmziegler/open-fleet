# src/open_fleet/adapters/slack/handler.py
"""Slack command handler — the only module in the project that imports slack_bolt (NFR15).

Parses natural language DM commands, calls Orchestrator.run(), and delivers
each response string as a sequential say() call in the same DM (FR1, FR2, FR3).

Timeframe parsing rules:
  - "today" / "today's" / "urgent today"     → "last 24 hours"
  - "since <phrase>"                          → "since <phrase>"
  - "last <N> hours/days"                     → "last <N> hours/days"
  - anything else                             → "last 24 hours" (default)
"""
from __future__ import annotations

import logging
import re

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from open_fleet.core.orchestrator import Orchestrator

logger = logging.getLogger("open_fleet.adapters.slack.handler")

# Patterns evaluated in order — first match wins.
_TIMEFRAME_PATTERNS: list[tuple[re.Pattern, str | None]] = [
    # "since <phrase>" — keep "since" in the result so the orchestrator has the full phrase
    (re.compile(r"\b(since\s+.+)", re.IGNORECASE), None),
    # "last N hours/days"
    (re.compile(r"\b(last\s+\d+\s+(?:hours?|days?))\b", re.IGNORECASE), None),
    # any mention of "today" maps to last 24 hours
    (re.compile(r"\btoday\b", re.IGNORECASE), "last 24 hours"),
]
_DEFAULT_TIMEFRAME = "last 24 hours"


def _parse_timeframe(text: str) -> str:
    """Extract a timeframe string from a natural language command."""
    for pattern, fixed_result in _TIMEFRAME_PATTERNS:
        m = pattern.search(text)
        if m:
            # fixed_result overrides capture group (e.g. "today" → "last 24 hours")
            return fixed_result if fixed_result is not None else m.group(1).strip()
    return _DEFAULT_TIMEFRAME


class SlackHandler:
    """Registers the message handler on a slack_bolt AsyncApp.

    Args:
        app:          Configured slack_bolt AsyncApp instance.
        orchestrator: Wired Orchestrator ready to run extractions.
    """

    def __init__(self, app: AsyncApp, orchestrator: Orchestrator) -> None:
        self._app = app
        self._orchestrator = orchestrator
        self._register()

    def _register(self) -> None:
        """Attach the DM message listener to the app."""

        @self._app.message()
        async def handle_message(message: dict, say) -> None:  # type: ignore[type-arg]
            text: str = message.get("text", "")
            timeframe = _parse_timeframe(text)
            logger.info(
                "Received Slack command",
                extra={"text": text[:120], "parsed_timeframe": timeframe},
            )

            async def notify(msg: str) -> None:
                await say(msg)

            responses = await self._orchestrator.run(timeframe, notify=notify)
            for response in responses:
                await say(response)

    @property
    def app(self) -> AsyncApp:
        return self._app


async def start(app: AsyncApp, slack_app_token: str) -> None:
    """Connect the app via Socket Mode and block until stopped.

    Args:
        app:             Configured AsyncApp (with SlackHandler already registered).
        slack_app_token: The xapp-... Socket Mode token from config.
    """
    handler = AsyncSocketModeHandler(app, slack_app_token)
    await handler.start_async()
