# tests/test_adapters/test_handler.py
"""Tests for the Slack command handler — timeframe parsing and message dispatch."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from open_fleet.adapters.slack.handler import SlackHandler, _parse_timeframe


# ── _parse_timeframe unit tests ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "text, expected",
    [
        # "today" variants → last 24 hours
        ("extract today's emails", "last 24 hours"),
        ("what's urgent today?", "last 24 hours"),
        ("check TODAY", "last 24 hours"),
        # "since <phrase>" passthrough (including the word "since")
        ("check emails since yesterday 5pm", "since yesterday 5pm"),
        ("triage since last Monday", "since last Monday"),
        # "last N hours/days"
        ("get emails from the last 48 hours", "last 48 hours"),
        ("last 3 days", "last 3 days"),
        # default fallback
        ("run extraction", "last 24 hours"),
        ("", "last 24 hours"),
        ("what do I need to do?", "last 24 hours"),
    ],
)
def test_parse_timeframe(text: str, expected: str) -> None:
    assert _parse_timeframe(text) == expected


# ── SlackHandler integration tests ───────────────────────────────────────────


def _make_app():
    """Build a minimal mock AsyncApp that captures registered handlers."""
    app = MagicMock()
    app._registered_handlers: list = []

    def message_decorator():
        def register(fn):
            app._registered_handlers.append(fn)
            return fn
        return register

    app.message = message_decorator
    return app


def _make_orchestrator(responses=("Response part 1", "Response part 2")):
    orch = MagicMock()
    orch.run = AsyncMock(return_value=list(responses))
    return orch


def test_handler_registers_message_listener():
    app = _make_app()
    SlackHandler(app=app, orchestrator=_make_orchestrator())
    assert len(app._registered_handlers) == 1


def test_handler_calls_orchestrator_with_parsed_timeframe():
    app = _make_app()
    orch = _make_orchestrator()
    SlackHandler(app=app, orchestrator=orch)
    handler_fn = app._registered_handlers[0]

    say = AsyncMock()
    asyncio.run(handler_fn(message={"text": "extract today's emails"}, say=say))

    orch.run.assert_called_once()
    call_args = orch.run.call_args
    timeframe = call_args.args[0] if call_args.args else call_args.kwargs.get("timeframe")
    assert timeframe == "last 24 hours"


def test_handler_sends_each_response_as_separate_say():
    app = _make_app()
    orch = _make_orchestrator(responses=["Part 1", "Part 2", "Part 3"])
    SlackHandler(app=app, orchestrator=orch)
    handler_fn = app._registered_handlers[0]

    say = AsyncMock()
    asyncio.run(handler_fn(message={"text": "check emails"}, say=say))

    assert say.call_count == 3
    assert say.call_args_list[0].args[0] == "Part 1"
    assert say.call_args_list[1].args[0] == "Part 2"
    assert say.call_args_list[2].args[0] == "Part 3"


def test_handler_passes_notify_to_orchestrator():
    """notify callback passed to orchestrator must forward strings to say()."""

    async def capture_run(timeframe, notify=None):
        if notify:
            await notify("⚠️ LM Studio unavailable — falling back to Gemini")
        return ["Done"]

    app = _make_app()
    orch = MagicMock()
    orch.run = capture_run
    SlackHandler(app=app, orchestrator=orch)
    handler_fn = app._registered_handlers[0]

    say = AsyncMock()
    asyncio.run(handler_fn(message={"text": "run triage"}, say=say))

    # say() called once for the notify warning, once for the response
    assert say.call_count == 2
    assert "LM Studio" in say.call_args_list[0].args[0]
    assert say.call_args_list[1].args[0] == "Done"


def test_handler_since_timeframe():
    app = _make_app()
    orch = _make_orchestrator()
    SlackHandler(app=app, orchestrator=orch)
    handler_fn = app._registered_handlers[0]

    say = AsyncMock()
    asyncio.run(handler_fn(message={"text": "check emails since yesterday 5pm"}, say=say))

    call_args = orch.run.call_args
    timeframe = call_args.args[0] if call_args.args else call_args.kwargs.get("timeframe")
    assert timeframe == "since yesterday 5pm"
