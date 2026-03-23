# Story 4.1: Response Formatter

Status: done

## Story

As Jason,
I want extracted action items formatted into a prioritized, emoji-coded Slack report with sender, timestamp, and a context excerpt per item,
so that I can scan my full day's action items in under two minutes without opening Gmail.

## Acceptance Criteria

**AC1 — Priority grouping and ordering:**
**Given** a valid `ExtractionResult` with action items of mixed priorities
**When** `ResponseFormatter.format(result: ExtractionResult) -> list[str]` is called
**Then** it returns one or more strings grouping action items under priority headers in order:
`🔴 Urgent` → `💬 Needs Response` → `⏰ Approaching Deadline` → `🟡 This Week` → `🟢 No Deadline`
**And** groups with no items are omitted from the output

**AC2 — Item rendering:**
**Given** an `ActionItem` is rendered
**When** it appears in the formatted output
**Then** it includes: sender name, UTC timestamp formatted as human-readable local date/time, and `context` truncated to 100 characters
**And** a sentiment indicator is shown for `frustrated` or `escalated` items (e.g., `💬 frustrated`)

**AC3 — Response header:**
**Given** a response header is rendered
**When** it appears at the top of the first message
**Then** it includes the total `emails_scanned` count and the `timeframe` string from `ExtractionResult` (FR22)

**AC4 — Message splitting:**
**Given** the formatted output exceeds 4,000 characters
**When** `format()` returns the result
**Then** it returns a `list[str]` with content split across multiple strings, each ≤ 4,000 characters, with no action item cut mid-entry (FR23)

**AC5 — No Slack imports:**
**Given** `core/response.py` is inspected
**When** its imports are checked
**Then** it contains zero imports from `slack_bolt`, `slack_sdk`, or any Slack-specific module (NFR15, NFR16)

## Tasks / Subtasks

- [x] Implement `ResponseFormatter` class in `src/open_fleet/core/response.py` (AC1, AC2, AC3, AC4, AC5)
  - [x] Define `_GROUPS` list of `(bucket_index, header_text)` tuples in priority order
  - [x] Implement `_assign_bucket(item: ActionItem) -> int` — maps priority+sentiment to display bucket
  - [x] Implement `_display_name(sender: str) -> str` — extracts name from `"Name <email>"` format
  - [x] Implement `_format_timestamp(email_timestamp: str) -> str` — ISO8601 → human-readable (`Mon 01 Mar 09:00 UTC`)
  - [x] Implement `_format_item(item: ActionItem) -> str` — renders sender, timestamp, sentiment indicator, context
  - [x] Implement `_assemble(chunks: list[str]) -> list[str]` — joins chunks into messages ≤ 4,000 chars without mid-chunk splits
  - [x] Implement `ResponseFormatter.format(result: ExtractionResult) -> list[str]` as a `@staticmethod`
  - [x] Verify zero imports from `slack_bolt`, `slack_sdk`, or any Slack module
- [x] Write tests in `tests/test_core/test_response.py` (AC1–AC5)
  - [x] Test header includes `timeframe` and `emails_scanned`
  - [x] Test singular/plural "email"/"emails" in header
  - [x] Test all bucket assignment logic (urgent, frustrated/escalated, this_week+deadline, this_week, no_deadline)
  - [x] Test group ordering (urgent before this_week, needs_response before this_week, etc.)
  - [x] Test empty groups are omitted
  - [x] Test item rendering: sender display name extraction, context, timestamp format, sentiment indicator
  - [x] Test `_display_name` with `"Name <email>"`, raw email, and `"<email>"` formats
  - [x] Test `_format_timestamp` with valid and invalid inputs
  - [x] Test message splitting: single short result → 1 message; 60 items → multiple messages; no message > 4,000 chars; all items preserved; no mid-entry cuts
  - [x] Test zero Slack imports via `ast` parse of `response.py`
- [x] Run `pytest tests/test_core/test_response.py -v` — all pass
- [x] Run `ruff check src/open_fleet/core/response.py tests/test_core/test_response.py` — clean

## Dev Notes

### Bucket Assignment Logic

The `_assign_bucket` function must follow this **exact priority order** — urgent wins over sentiment:

```python
def _assign_bucket(item: ActionItem) -> int:
    if item.priority == "urgent":
        return 0  # 🔴 Urgent (sentiment irrelevant — urgent always wins)
    if item.sentiment in ("frustrated", "escalated"):
        return 1  # 💬 Needs Response
    if item.priority == "this_week" and item.deadline:
        return 2  # ⏰ Approaching Deadline
    if item.priority == "this_week":
        return 3  # 🟡 This Week
    return 4      # 🟢 No Deadline (no_deadline + neutral)
```

**Critical:** An urgent item with `sentiment="frustrated"` still goes to bucket 0 (🔴 Urgent), NOT bucket 1.

### `_GROUPS` Definition (order must match epics exactly)

```python
_GROUPS: list[tuple[int, str]] = [
    (0, "🔴 *Urgent*"),
    (1, "💬 *Needs Response*"),
    (2, "⏰ *Approaching Deadline*"),
    (3, "🟡 *This Week*"),
    (4, "🟢 *No Deadline*"),
]
```

### `_MAX_MSG_CHARS` Constant

```python
_MAX_MSG_CHARS = 4_000
```

### `_assemble` Splitting Logic

The function receives a flat list of "chunks" (header string, group headers, item strings). It joins them with `"\n"` separators but **never starts a new message mid-chunk**:

```python
def _assemble(chunks: list[str]) -> list[str]:
    messages: list[str] = []
    current = ""
    for chunk in chunks:
        sep = "\n" if current else ""
        if current and len(current) + len(sep) + len(chunk) > _MAX_MSG_CHARS:
            messages.append(current)
            current = chunk
        else:
            current = current + sep + chunk
    if current:
        messages.append(current)
    return messages
```

### `_format_item` Output Format

```
• *Name* — Mon 01 Mar 09:00 UTC | 💬 frustrated
  Context text here (max 100 chars)
```

- Sentiment indicator only shown for `"frustrated"` or `"escalated"` — never for `"neutral"`
- Format: `| 💬 {sentiment}` appended to the timestamp line

### `_format_timestamp` Target Format

```python
ts.strftime("%a %d %b %H:%M UTC")
# → "Sun 01 Mar 09:00 UTC"
```

Handle `ValueError` and `TypeError` gracefully — return raw string on parse failure.

### Import Boundary (CRITICAL)

`core/response.py` IS allowed to import from `llm/schemas.py` — the architecture explicitly states `core/response.py` depends on `ActionItem` and `ExtractionResult` as the data contract. This is the **only** non-`core` import permitted.

```python
# PERMITTED in core/response.py
from open_fleet.llm.schemas import ActionItem, ExtractionResult

# FORBIDDEN — zero Slack imports
import slack_bolt          # FORBIDDEN
import slack_sdk           # FORBIDDEN
from slack_bolt import ... # FORBIDDEN
```

The AC5 test validates this via `ast` module parse.

### Header Format

```
📬 *Email Triage* — {timeframe} | {count} {email/emails} scanned
```

Use singular "email" when `emails_scanned == 1`, plural "emails" otherwise.

### Existing Code Context

Both `response.py` and `tests/test_core/test_response.py` have been started — check their current state before writing. Do not recreate from scratch if they are partially or fully complete; validate against ACs and tasks instead.

### File Locations

- Implementation: `src/open_fleet/core/response.py`
- Tests: `tests/test_core/test_response.py`

### Project Structure Notes

- `core/` module has no `__init__.py` exports for response — import directly: `from open_fleet.core.response import ResponseFormatter`
- Test helper `_item()` factory function reduces test boilerplate (keyword-only args with sensible defaults)
- Test helper `_result()` wraps `ExtractionResult` construction
- Tests should import private helpers (`_assign_bucket`, `_display_name`, `_format_timestamp`) directly for unit testing

### Testing Framework

- `pytest` (no async tests needed — `ResponseFormatter.format()` is synchronous)
- Class-based test grouping (pattern established in previous stories): `TestHeader`, `TestBucketAssignment`, `TestGroupOrdering`, `TestItemRendering`, `TestDisplayName`, `TestFormatTimestamp`, `TestMessageSplitting`, `TestNoSlackImports`
- Run from project root: `pytest tests/test_core/test_response.py -v`
- No `.env` required — `ResponseFormatter` is a pure function with no config dependencies

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 4.1: Response Formatter]
- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure: src/ Layout with Enforced Layering]
- [Source: _bmad-output/planning-artifacts/architecture.md#Structure Patterns — Module Responsibility Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision Impact Analysis — Implementation Sequence step 9]
- [Source: _bmad-output/planning-artifacts/epics.md#FR20, FR21, FR22, FR23]
- [Source: _bmad-output/planning-artifacts/architecture.md#Format Patterns — Slack Message Format]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `src/open_fleet/core/response.py` — ResponseFormatter class, _assign_bucket, _display_name, _format_timestamp, _format_item, _assemble
- `tests/test_core/test_response.py` — 43 tests covering AC1–AC5 (TestHeader, TestBucketAssignment, TestGroupOrdering, TestItemRendering, TestDisplayName, TestFormatTimestamp, TestMessageSplitting, TestNoSlackImports)

## Change Log

- 2026-03-04: Story 4.1 created via create-story workflow. Implementation partially in progress (response.py modified, test_response.py untracked in working tree).
- 2026-03-14: Code review complete. Fixed: removed unused `import pytest` (ruff F401), strengthened `test_item_omits_angle_bracket_email_when_name_present` to assert email address is absent from output. All 38 tests passing, ruff clean. Story status updated to review.
- 2026-03-22: Senior dev review (adversarial). Fixed: (H1) `_format_timestamp` now converts to UTC via `.astimezone(timezone.utc)` before formatting — previously non-UTC offsets were formatted with wrong time but labeled "UTC"; (H2) `_format_item` now explicitly truncates context to 100 chars as defensive measure, not relying solely on schema validator; (L1) `_format_timestamp` fallback now returns `str(email_timestamp)` to guarantee str return type. Added 5 new tests: all-5-groups ordering, non-UTC timezone conversion, None timestamp, empty display name, empty context. 43 tests passing, ruff clean.
