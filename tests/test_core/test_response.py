"""Tests for Story 4.1: Response formatter."""
from open_fleet.core.response import ResponseFormatter, _assign_bucket, _display_name, _format_timestamp
from open_fleet.llm.schemas import ActionItem, ExtractionResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(
    *,
    description="Do something",
    client="Acme",
    sender="alice@acme.com",
    email_timestamp="2026-03-01T09:00:00+00:00",
    deadline=None,
    priority="no_deadline",
    sentiment="neutral",
    context="Please handle this.",
) -> ActionItem:
    return ActionItem(
        description=description,
        client=client,
        sender=sender,
        email_timestamp=email_timestamp,
        deadline=deadline,
        priority=priority,
        sentiment=sentiment,
        context=context,
    )


def _result(items: list[ActionItem], emails_scanned: int = 5, timeframe: str = "last 24 hours") -> ExtractionResult:
    return ExtractionResult(
        action_items=items,
        emails_scanned=emails_scanned,
        timeframe=timeframe,
    )


def _full_text(result: ExtractionResult) -> str:
    return "\n".join(ResponseFormatter.format(result))


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

class TestHeader:
    def test_header_includes_timeframe(self):
        text = _full_text(_result([], timeframe="last 24 hours"))
        assert "last 24 hours" in text

    def test_header_includes_emails_scanned_count(self):
        text = _full_text(_result([], emails_scanned=42))
        assert "42" in text

    def test_header_plural_emails_for_multiple(self):
        text = _full_text(_result([], emails_scanned=5))
        assert "emails" in text

    def test_header_singular_email_for_one(self):
        text = _full_text(_result([], emails_scanned=1))
        assert "1 email " in text or "1 email\n" in text or text.endswith("1 email")

    def test_always_returns_at_least_one_string(self):
        msgs = ResponseFormatter.format(_result([]))
        assert isinstance(msgs, list)
        assert len(msgs) >= 1

    def test_header_is_first_content(self):
        msgs = ResponseFormatter.format(_result([], timeframe="today"))
        assert "today" in msgs[0]


# ---------------------------------------------------------------------------
# Priority grouping / bucket assignment
# ---------------------------------------------------------------------------

class TestBucketAssignment:
    def test_urgent_priority_goes_to_urgent_bucket(self):
        assert _assign_bucket(_item(priority="urgent", sentiment="neutral")) == 0

    def test_urgent_stays_in_urgent_even_if_frustrated(self):
        assert _assign_bucket(_item(priority="urgent", sentiment="frustrated")) == 0

    def test_frustrated_non_urgent_goes_to_needs_response(self):
        assert _assign_bucket(_item(priority="this_week", sentiment="frustrated")) == 1

    def test_escalated_non_urgent_goes_to_needs_response(self):
        assert _assign_bucket(_item(priority="no_deadline", sentiment="escalated")) == 1

    def test_this_week_with_deadline_neutral_goes_to_approaching_deadline(self):
        assert _assign_bucket(_item(
            priority="this_week", deadline="2026-03-07T17:00:00+00:00", sentiment="neutral"
        )) == 2

    def test_this_week_without_deadline_neutral_goes_to_this_week(self):
        assert _assign_bucket(_item(priority="this_week", deadline=None, sentiment="neutral")) == 3

    def test_no_deadline_neutral_goes_to_no_deadline(self):
        assert _assign_bucket(_item(priority="no_deadline", sentiment="neutral")) == 4


class TestGroupOrdering:
    def test_urgent_group_appears_before_this_week_group(self):
        items = [
            _item(priority="this_week", description="This week task"),
            _item(priority="urgent", description="Urgent task"),
        ]
        text = _full_text(_result(items))
        assert text.index("Urgent") < text.index("This Week")

    def test_needs_response_group_appears_before_this_week(self):
        items = [
            _item(priority="this_week", sentiment="neutral", description="Normal task"),
            _item(priority="this_week", sentiment="frustrated", description="Frustrated task"),
        ]
        text = _full_text(_result(items))
        assert text.index("Needs Response") < text.index("This Week")

    def test_approaching_deadline_appears_before_this_week(self):
        items = [
            _item(priority="this_week", deadline=None, sentiment="neutral", description="No DL"),
            _item(priority="this_week", deadline="2026-03-07T17:00:00+00:00",
                  sentiment="neutral", description="Has DL"),
        ]
        text = _full_text(_result(items))
        assert text.index("Approaching") < text.index("This Week")

    def test_this_week_appears_before_no_deadline(self):
        items = [
            _item(priority="no_deadline", description="No DL"),
            _item(priority="this_week", description="This week"),
        ]
        text = _full_text(_result(items))
        assert text.index("This Week") < text.index("No Deadline")

    def test_empty_groups_are_omitted(self):
        items = [_item(priority="urgent")]
        text = _full_text(_result(items))
        assert "Needs Response" not in text
        assert "This Week" not in text
        assert "No Deadline" not in text

    def test_no_items_produces_header_only(self):
        msgs = ResponseFormatter.format(_result([]))
        assert len(msgs) == 1
        assert "🔴" not in msgs[0]
        assert "🟡" not in msgs[0]


# ---------------------------------------------------------------------------
# Item rendering
# ---------------------------------------------------------------------------

class TestItemRendering:
    def test_item_includes_sender_email(self):
        item = _item(sender="alice@acme.com")
        text = _full_text(_result([item]))
        assert "alice@acme.com" in text

    def test_item_extracts_display_name_from_angle_bracket_format(self):
        item = _item(sender="Alice Smith <alice@acme.com>")
        text = _full_text(_result([item]))
        assert "Alice Smith" in text

    def test_item_omits_angle_bracket_email_when_name_present(self):
        item = _item(sender="Alice Smith <alice@acme.com>")
        text = _full_text(_result([item]))
        assert "Alice Smith" in text
        assert "alice@acme.com" not in text

    def test_item_includes_context(self):
        item = _item(context="Please review the contract by EOD")
        text = _full_text(_result([item]))
        assert "Please review the contract by EOD" in text

    def test_item_shows_sentiment_indicator_for_frustrated(self):
        item = _item(priority="this_week", sentiment="frustrated")
        text = _full_text(_result([item]))
        assert "frustrated" in text

    def test_item_shows_sentiment_indicator_for_escalated(self):
        item = _item(priority="no_deadline", sentiment="escalated")
        text = _full_text(_result([item]))
        assert "escalated" in text

    def test_item_does_not_show_sentiment_indicator_for_neutral(self):
        item = _item(priority="no_deadline", sentiment="neutral")
        text = _full_text(_result([item]))
        assert "neutral" not in text

    def test_item_includes_formatted_timestamp(self):
        item = _item(email_timestamp="2026-03-01T09:00:00+00:00")
        text = _full_text(_result([item]))
        # Formatted as "Sun 01 Mar 09:00 UTC"
        assert "Mar" in text
        assert "09:00" in text


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

class TestDisplayName:
    def test_extracts_name_from_angle_bracket_format(self):
        assert _display_name("Alice Smith <alice@acme.com>") == "Alice Smith"

    def test_returns_raw_sender_when_no_angle_brackets(self):
        assert _display_name("alice@acme.com") == "alice@acme.com"

    def test_returns_email_when_no_display_name_before_bracket(self):
        assert _display_name("<alice@acme.com>") == "alice@acme.com"


class TestFormatTimestamp:
    def test_formats_iso_timestamp_human_readable(self):
        result = _format_timestamp("2026-03-01T09:00:00+00:00")
        assert "Mar" in result
        assert "09:00" in result

    def test_returns_raw_on_invalid_input(self):
        result = _format_timestamp("not-a-date")
        assert result == "not-a-date"


# ---------------------------------------------------------------------------
# Message splitting (FR23)
# ---------------------------------------------------------------------------

class TestMessageSplitting:
    def test_short_result_returns_single_string(self):
        result = _result([_item()])
        msgs = ResponseFormatter.format(result)
        assert len(msgs) == 1

    def test_no_message_exceeds_4000_chars(self):
        # 60 items → well over 4,000 chars total
        items = [
            _item(
                description=f"Task {i}",
                sender=f"sender{i}@longdomainname.example.com",
                context="x" * 100,
                priority="no_deadline",
            )
            for i in range(60)
        ]
        msgs = ResponseFormatter.format(_result(items, emails_scanned=60))
        for msg in msgs:
            assert len(msg) <= 4000, f"Message of {len(msg)} chars exceeds 4000"

    def test_large_result_splits_into_multiple_messages(self):
        items = [
            _item(
                description=f"Task {i}",
                sender=f"sender{i}@longdomainname.example.com",
                context="x" * 100,
                priority="no_deadline",
            )
            for i in range(60)
        ]
        msgs = ResponseFormatter.format(_result(items, emails_scanned=60))
        assert len(msgs) > 1

    def test_split_preserves_all_items(self):
        """Every item must appear somewhere across the split messages."""
        items = [
            _item(context=f"unique-marker-{i}", priority="no_deadline")
            for i in range(40)
        ]
        all_text = "\n".join(ResponseFormatter.format(_result(items, emails_scanned=40)))
        for i in range(40):
            assert f"unique-marker-{i}" in all_text, f"Item {i} missing from output"

    def test_split_never_cuts_item_mid_entry(self):
        """Context text that starts in one message must complete in the same message."""
        marker = "SPLIT_BOUNDARY_MARKER"
        # Create items where one has a distinctive multi-line context
        items = [
            _item(
                description=f"Task {i}",
                sender=f"person{i}@example.com",
                context="x" * 90,  # near-max context
                priority="no_deadline",
            )
            for i in range(50)
        ]
        # Replace one item's context with our marker
        items[25] = _item(
            sender="marker@example.com",
            context=marker,
            priority="no_deadline",
        )
        msgs = ResponseFormatter.format(_result(items, emails_scanned=50))
        # The marker must be complete inside exactly one message
        messages_containing_marker = [m for m in msgs if marker in m]
        assert len(messages_containing_marker) == 1


# ---------------------------------------------------------------------------
# No Slack imports (NFR15, NFR16)
# ---------------------------------------------------------------------------

class TestNoSlackImports:
    def test_response_module_has_no_slack_imports(self):
        import ast
        import pathlib
        source = pathlib.Path("src/open_fleet/core/response.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "slack" not in alias.name.lower(), \
                        f"response.py imports {alias.name}"
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "slack" not in node.module.lower(), \
                        f"response.py imports from {node.module}"
