"""Tests for Story 3.5: Extraction prompt content and scenario accuracy.

These tests validate that:
  1. The system prompt contains the required classification instructions.
  2. The user message builder provides all data an LLM needs.
  3. The full pipeline correctly processes realistic LLM responses for each scenario.
  4. Schema constraints (context truncation, literal enums) are enforced end-to-end.

NOTE — AC acceptance criterion 5 ("85% accuracy on 10 real emails from Jason's inbox")
is a *manual* spot-check that cannot be automated without live LLM access. Run it by
calling `scripts/setup_gmail_auth.py` then executing a real extraction via the CLI.
"""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from open_fleet.llm.lmstudio import (
    LMStudioProvider,
    _SYSTEM_PROMPT,
    _build_user_message,
)
from open_fleet.llm.schemas import ActionItem, ExtractionResult


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

_EXPLICIT_EMAIL = {
    "subject": "Proposal review needed",
    "sender": "alice@acme.com",
    "timestamp": "2026-03-01T09:00:00+00:00",
    "body": "Hi, please review the attached proposal by EOD Friday. This is urgent.",
}

_IMPLICIT_EMAIL = {
    "subject": "Quick check-in",
    "sender": "bob@globex.com",
    "timestamp": "2026-03-01T10:00:00+00:00",
    "body": "Just wanted to check in on the status of the Q1 report.",
}

_FRUSTRATED_EMAIL = {
    "subject": "Still waiting",
    "sender": "carol@initech.com",
    "timestamp": "2026-03-01T11:00:00+00:00",
    "body": "This is the third time I've had to follow up. We need an answer today.",
}

_ESCALATION_EMAIL = {
    "subject": "Escalating this issue",
    "sender": "dave@initech.com",
    "timestamp": "2026-03-01T12:00:00+00:00",
    "body": "I am copying in my manager and yours. We need a resolution immediately.",
}

_NO_ACTION_EMAIL = {
    "subject": "FYI – Office closure",
    "sender": "hr@company.com",
    "timestamp": "2026-03-01T08:00:00+00:00",
    "body": "Just a heads-up that the office will be closed on Friday for maintenance.",
}


def _lm_response(content: str) -> dict:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


def _provider() -> LMStudioProvider:
    return LMStudioProvider(base_url="http://localhost:1234/v1", timeout_secs=30)


# ---------------------------------------------------------------------------
# System prompt content
# ---------------------------------------------------------------------------

class TestSystemPromptInstructions:
    """The prompt must encode every classification rule the LLM needs."""

    def test_prompt_instructs_extraction_of_action_items(self):
        assert "action item" in _SYSTEM_PROMPT.lower()

    def test_prompt_instructs_follow_up_detection(self):
        assert "follow-up" in _SYSTEM_PROMPT or "follow up" in _SYSTEM_PROMPT.lower()

    def test_prompt_defines_urgent_priority_rule(self):
        assert "urgent" in _SYSTEM_PROMPT

    def test_prompt_defines_this_week_priority_rule(self):
        assert "this_week" in _SYSTEM_PROMPT

    def test_prompt_defines_no_deadline_priority_rule(self):
        assert "no_deadline" in _SYSTEM_PROMPT

    def test_prompt_defines_escalated_sentiment_rule(self):
        assert "escalated" in _SYSTEM_PROMPT

    def test_prompt_defines_frustrated_sentiment_rule(self):
        assert "frustrated" in _SYSTEM_PROMPT

    def test_prompt_defines_deadline_inference_rule(self):
        assert "deadline" in _SYSTEM_PROMPT.lower()

    def test_prompt_specifies_context_max_100_chars(self):
        assert "100" in _SYSTEM_PROMPT

    def test_prompt_instructs_emails_scanned_field(self):
        assert "emails_scanned" in _SYSTEM_PROMPT

    def test_prompt_instructs_timeframe_field(self):
        assert "timeframe" in _SYSTEM_PROMPT

    def test_prompt_requires_json_only_output(self):
        assert "JSON" in _SYSTEM_PROMPT or "json" in _SYSTEM_PROMPT

    def test_prompt_excludes_no_action_emails_from_results(self):
        """Emails with no action must be counted but not appear in action_items."""
        assert "no required action" in _SYSTEM_PROMPT or "must NOT appear" in _SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# User message builder
# ---------------------------------------------------------------------------

class TestUserMessageCompleteness:
    """The user message must provide everything an LLM needs to fill all schema fields."""

    def test_message_includes_email_count(self):
        """LLM needs the count to return the correct emails_scanned value."""
        msg = _build_user_message([_EXPLICIT_EMAIL, _IMPLICIT_EMAIL], "last 24 hours")
        assert "2" in msg

    def test_message_includes_timeframe(self):
        msg = _build_user_message([_EXPLICIT_EMAIL], "last 24 hours")
        assert "last 24 hours" in msg

    def test_message_includes_sender(self):
        msg = _build_user_message([_EXPLICIT_EMAIL], "today")
        assert "alice@acme.com" in msg

    def test_message_includes_subject(self):
        msg = _build_user_message([_EXPLICIT_EMAIL], "today")
        assert "Proposal review needed" in msg

    def test_message_includes_timestamp(self):
        msg = _build_user_message([_EXPLICIT_EMAIL], "today")
        assert "2026-03-01" in msg

    def test_message_includes_body(self):
        msg = _build_user_message([_EXPLICIT_EMAIL], "today")
        assert "EOD Friday" in msg

    def test_message_enumerates_each_email(self):
        msg = _build_user_message([_EXPLICIT_EMAIL, _IMPLICIT_EMAIL], "today")
        assert "Email 1" in msg
        assert "Email 2" in msg

    def test_email_count_reflects_batch_size(self):
        for count in (1, 5, 50):
            emails = [_EXPLICIT_EMAIL] * count
            msg = _build_user_message(emails, "today")
            assert str(count) in msg


# ---------------------------------------------------------------------------
# Scenario: explicit request with deadline (FR9, FR11, FR12)
# ---------------------------------------------------------------------------

class TestExplicitActionScenario:
    """An email with an explicit request + deadline produces a correctly classified item."""

    def _explicit_result(self) -> dict:
        return {
            "action_items": [{
                "description": "Review the proposal",
                "client": "Acme",
                "sender": "alice@acme.com",
                "email_timestamp": "2026-03-01T09:00:00+00:00",
                "deadline": "2026-03-07T17:00:00+00:00",
                "priority": "this_week",
                "sentiment": "neutral",
                "context": "please review the attached proposal by EOD Friday",
            }],
            "emails_scanned": 1,
            "timeframe": "last 24 hours",
        }

    def test_explicit_request_produces_action_item(self):
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(self._explicit_result()))):
            result = asyncio.run(provider.extract([_EXPLICIT_EMAIL], "last 24 hours"))
        assert len(result.action_items) == 1

    def test_explicit_request_priority_is_urgent_or_this_week(self):
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(self._explicit_result()))):
            result = asyncio.run(provider.extract([_EXPLICIT_EMAIL], "last 24 hours"))
        assert result.action_items[0].priority in ("urgent", "this_week")

    def test_explicit_request_deadline_is_set(self):
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(self._explicit_result()))):
            result = asyncio.run(provider.extract([_EXPLICIT_EMAIL], "last 24 hours"))
        assert result.action_items[0].deadline is not None


# ---------------------------------------------------------------------------
# Scenario: implicit action item (FR10)
# ---------------------------------------------------------------------------

class TestImplicitActionScenario:
    """An email with an implicit follow-up ask is surfaced as an action item."""

    def _implicit_result(self) -> dict:
        return {
            "action_items": [{
                "description": "Follow up on Q1 report status",
                "client": "Globex",
                "sender": "bob@globex.com",
                "email_timestamp": "2026-03-01T10:00:00+00:00",
                "deadline": None,
                "priority": "no_deadline",
                "sentiment": "neutral",
                "context": "check in on the status of the Q1 report",
            }],
            "emails_scanned": 1,
            "timeframe": "last 24 hours",
        }

    def test_implicit_check_in_produces_action_item(self):
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(self._implicit_result()))):
            result = asyncio.run(provider.extract([_IMPLICIT_EMAIL], "last 24 hours"))
        assert len(result.action_items) == 1

    def test_implicit_check_in_description_captures_ask(self):
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(self._implicit_result()))):
            result = asyncio.run(provider.extract([_IMPLICIT_EMAIL], "last 24 hours"))
        desc = result.action_items[0].description.lower()
        assert "q1" in desc or "report" in desc or "follow" in desc or "status" in desc


# ---------------------------------------------------------------------------
# Scenario: sentiment classification (FR13)
# ---------------------------------------------------------------------------

class TestSentimentClassification:
    def test_frustrated_language_yields_frustrated_sentiment(self):
        resp = {
            "action_items": [{
                "description": "Provide an answer",
                "client": "Initech",
                "sender": "carol@initech.com",
                "email_timestamp": "2026-03-01T11:00:00+00:00",
                "deadline": None,
                "priority": "urgent",
                "sentiment": "frustrated",
                "context": "third time I've had to follow up",
            }],
            "emails_scanned": 1,
            "timeframe": "last 24 hours",
        }
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(resp))):
            result = asyncio.run(provider.extract([_FRUSTRATED_EMAIL], "last 24 hours"))
        assert result.action_items[0].sentiment in ("frustrated", "escalated")

    def test_cc_manager_escalation_yields_escalated_sentiment(self):
        resp = {
            "action_items": [{
                "description": "Resolve the escalated issue immediately",
                "client": "Initech",
                "sender": "dave@initech.com",
                "email_timestamp": "2026-03-01T12:00:00+00:00",
                "deadline": None,
                "priority": "urgent",
                "sentiment": "escalated",
                "context": "copying in my manager and yours",
            }],
            "emails_scanned": 1,
            "timeframe": "last 24 hours",
        }
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(resp))):
            result = asyncio.run(provider.extract([_ESCALATION_EMAIL], "last 24 hours"))
        assert result.action_items[0].sentiment == "escalated"

    def test_neutral_fyi_email_produces_no_action_item(self):
        """Informational emails must not appear in action_items."""
        resp = {
            "action_items": [],
            "emails_scanned": 1,
            "timeframe": "last 24 hours",
        }
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(resp))):
            result = asyncio.run(provider.extract([_NO_ACTION_EMAIL], "last 24 hours"))
        assert result.action_items == []
        assert result.emails_scanned == 1


# ---------------------------------------------------------------------------
# emails_scanned parity (FR14)
# ---------------------------------------------------------------------------

class TestEmailsScannedParity:
    """emails_scanned must reflect total emails analyzed, including no-action ones."""

    def test_emails_scanned_matches_batch_size_single(self):
        resp = {"action_items": [], "emails_scanned": 1, "timeframe": "today"}
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(resp))):
            result = asyncio.run(provider.extract([_NO_ACTION_EMAIL], "today"))
        assert result.emails_scanned == 1

    def test_emails_scanned_matches_batch_size_mixed(self):
        """Batch of 3 (2 with action, 1 without) → emails_scanned == 3."""
        resp = {
            "action_items": [
                {
                    "description": "Review proposal",
                    "client": "Acme",
                    "sender": "alice@acme.com",
                    "email_timestamp": "2026-03-01T09:00:00+00:00",
                    "deadline": None,
                    "priority": "this_week",
                    "sentiment": "neutral",
                    "context": "please review the attached proposal",
                },
                {
                    "description": "Follow up on status",
                    "client": "Globex",
                    "sender": "bob@globex.com",
                    "email_timestamp": "2026-03-01T10:00:00+00:00",
                    "deadline": None,
                    "priority": "no_deadline",
                    "sentiment": "neutral",
                    "context": "check in on the status of the Q1 report",
                },
            ],
            "emails_scanned": 3,
            "timeframe": "last 24 hours",
        }
        batch = [_EXPLICIT_EMAIL, _IMPLICIT_EMAIL, _NO_ACTION_EMAIL]
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(resp))):
            result = asyncio.run(provider.extract(batch, "last 24 hours"))
        assert result.emails_scanned == 3
        assert len(result.action_items) == 2


# ---------------------------------------------------------------------------
# Context truncation (FR21)
# ---------------------------------------------------------------------------

class TestContextTruncation:
    """context field must never exceed 100 characters — enforced by the schema."""

    def test_context_within_100_chars_passes_validation(self):
        item = ActionItem(
            description="Test",
            client="Acme",
            sender="alice@acme.com",
            email_timestamp="2026-03-01T09:00:00+00:00",
            deadline=None,
            priority="no_deadline",
            sentiment="neutral",
            context="x" * 100,
        )
        assert len(item.context) == 100

    def test_context_over_100_chars_is_truncated_by_schema(self):
        item = ActionItem(
            description="Test",
            client="Acme",
            sender="alice@acme.com",
            email_timestamp="2026-03-01T09:00:00+00:00",
            deadline=None,
            priority="no_deadline",
            sentiment="neutral",
            context="x" * 150,
        )
        assert len(item.context) == 100

    def test_context_truncation_preserved_through_full_pipeline(self):
        """End-to-end: long context in LLM response is truncated before reaching caller."""
        long_context = "This is a very long context excerpt that exceeds one hundred characters " \
                       "and should be automatically truncated by the schema validator."
        resp = {
            "action_items": [{
                "description": "Test action",
                "client": "Acme",
                "sender": "alice@acme.com",
                "email_timestamp": "2026-03-01T09:00:00+00:00",
                "deadline": None,
                "priority": "no_deadline",
                "sentiment": "neutral",
                "context": long_context,
            }],
            "emails_scanned": 1,
            "timeframe": "last 24 hours",
        }
        provider = _provider()
        with patch.object(provider, "_post", new_callable=AsyncMock,
                          return_value=_lm_response(json.dumps(resp))):
            result = asyncio.run(provider.extract([_EXPLICIT_EMAIL], "last 24 hours"))
        assert len(result.action_items[0].context) <= 100
