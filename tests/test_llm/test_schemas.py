"""Tests for Story 3.1: Pydantic data models and extraction schema."""
import pytest
from pydantic import ValidationError

from open_fleet.llm.schemas import ActionItem, ExtractionResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _valid_action_item(**overrides) -> dict:
    base = {
        "description": "Review the proposal",
        "client": "Acme Corp",
        "sender": "Alice <alice@acme.com>",
        "email_timestamp": "2026-03-01T09:00:00+00:00",
        "deadline": "2026-03-05T17:00:00+00:00",
        "priority": "urgent",
        "sentiment": "neutral",
        "context": "Please review the attached proposal by EOD Friday.",
    }
    base.update(overrides)
    return base


def _valid_result(**overrides) -> dict:
    base = {
        "action_items": [_valid_action_item()],
        "emails_scanned": 42,
        "timeframe": "last 24 hours",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# ActionItem field types and values
# ---------------------------------------------------------------------------

class TestActionItemFields:
    def test_valid_action_item_parses(self):
        item = ActionItem(**_valid_action_item())
        assert item.description == "Review the proposal"
        assert item.client == "Acme Corp"
        assert item.sender == "Alice <alice@acme.com>"
        assert item.priority == "urgent"
        assert item.sentiment == "neutral"

    def test_deadline_can_be_none(self):
        item = ActionItem(**_valid_action_item(deadline=None))
        assert item.deadline is None

    def test_all_priority_values_accepted(self):
        for priority in ("urgent", "this_week", "no_deadline"):
            item = ActionItem(**_valid_action_item(priority=priority))
            assert item.priority == priority

    def test_invalid_priority_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ActionItem(**_valid_action_item(priority="low"))
        assert "priority" in str(exc_info.value).lower()

    def test_all_sentiment_values_accepted(self):
        for sentiment in ("neutral", "frustrated", "escalated"):
            item = ActionItem(**_valid_action_item(sentiment=sentiment))
            assert item.sentiment == sentiment

    def test_invalid_sentiment_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            ActionItem(**_valid_action_item(sentiment="angry"))
        assert "sentiment" in str(exc_info.value).lower()

    def test_missing_required_field_raises(self):
        data = _valid_action_item()
        del data["description"]
        with pytest.raises(ValidationError) as exc_info:
            ActionItem(**data)
        assert "description" in str(exc_info.value)

    def test_context_truncated_to_100_chars(self):
        long_context = "x" * 150
        item = ActionItem(**_valid_action_item(context=long_context))
        assert len(item.context) == 100

    def test_context_under_100_chars_unchanged(self):
        short = "Short context."
        item = ActionItem(**_valid_action_item(context=short))
        assert item.context == short


# ---------------------------------------------------------------------------
# ExtractionResult
# ---------------------------------------------------------------------------

class TestExtractionResult:
    def test_valid_result_parses(self):
        result = ExtractionResult.model_validate(_valid_result())
        assert result.emails_scanned == 42
        assert result.timeframe == "last 24 hours"
        assert len(result.action_items) == 1
        assert isinstance(result.action_items[0], ActionItem)

    def test_empty_action_items_list_accepted(self):
        result = ExtractionResult.model_validate(_valid_result(action_items=[]))
        assert result.action_items == []

    def test_multiple_action_items(self):
        items = [_valid_action_item(), _valid_action_item(priority="this_week")]
        result = ExtractionResult.model_validate(_valid_result(action_items=items))
        assert len(result.action_items) == 2

    def test_missing_emails_scanned_raises(self):
        data = _valid_result()
        del data["emails_scanned"]
        with pytest.raises(ValidationError) as exc_info:
            ExtractionResult.model_validate(data)
        assert "emails_scanned" in str(exc_info.value)

    def test_missing_timeframe_raises(self):
        data = _valid_result()
        del data["timeframe"]
        with pytest.raises(ValidationError) as exc_info:
            ExtractionResult.model_validate(data)
        assert "timeframe" in str(exc_info.value)

    def test_invalid_action_item_nested_raises(self):
        data = _valid_result(action_items=[_valid_action_item(priority="bad")])
        with pytest.raises(ValidationError) as exc_info:
            ExtractionResult.model_validate(data)
        assert "priority" in str(exc_info.value).lower()

    def test_no_partial_object_on_validation_error(self):
        """model_validate must raise — never return a partial object."""
        data = _valid_result()
        del data["timeframe"]
        result = None
        with pytest.raises(ValidationError):
            result = ExtractionResult.model_validate(data)
        assert result is None


# ---------------------------------------------------------------------------
# Import isolation — no circular dependencies
# ---------------------------------------------------------------------------

def test_schemas_has_no_forbidden_imports():
    """llm/schemas.py must not import from adapters/, tools/, or core/."""
    import ast
    import pathlib

    source = pathlib.Path("src/open_fleet/llm/schemas.py").read_text()
    tree = ast.parse(source)

    forbidden_prefixes = (
        "open_fleet.adapters",
        "open_fleet.tools",
        "open_fleet.core",
    )

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                for prefix in forbidden_prefixes:
                    assert not node.module.startswith(prefix), (
                        f"schemas.py imports from forbidden module: {node.module}"
                    )
