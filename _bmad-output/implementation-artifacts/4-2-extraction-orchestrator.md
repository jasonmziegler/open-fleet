# Story 4.2: Extraction Orchestrator

Status: done

## Story

As Jason,
I want the end-to-end triage workflow coordinated in a single orchestrator that handles all failure modes uniformly,
so that every run delivers either a complete formatted report or a precise ⚠️/❌ error message — never silence, never a crash.

## Acceptance Criteria

**AC1 — Happy path pipeline:**
**Given** a valid timeframe string is passed to `Orchestrator.run(timeframe: str) -> list[str]`
**When** it executes successfully
**Then** it calls `GmailClient.fetch_emails()` → `GmailClient.parse_email()` for each message → `LLMRouter.run_extraction()` → `ResponseFormatter.format()`
**And** returns the formatted `list[str]` ready for Slack delivery
**And** the full pipeline completes within 60 seconds for up to 200 emails (NFR1, NFR4)

**AC2 — GmailAuthError handling:**
**Given** `GmailAuthError` is raised during the Gmail fetch
**When** the orchestrator catches it
**Then** it returns `["❌ Gmail authentication expired — run scripts/setup_gmail_auth.py to reconnect"]`

**AC3 — GmailRateLimitError handling:**
**Given** `GmailRateLimitError` is raised
**When** the orchestrator catches it
**Then** it returns `["❌ Gmail API rate limit — extraction could not complete after retries"]`

**AC4 — LLMTimeoutError handling:**
**Given** `LLMTimeoutError` is raised by the router (both providers exhausted)
**When** the orchestrator catches it
**Then** it returns `["❌ LLM extraction failed — both LM Studio and Gemini unavailable"]`

**AC5 — Unexpected exception handling:**
**Given** an unexpected exception (not an `OpenFleetError` subclass) is raised anywhere in the pipeline
**When** the orchestrator catches it
**Then** it returns `["❌ Unexpected error — check logs for details"]`
**And** logs the full exception traceback at `ERROR` level

**AC6 — No Slack imports:**
**Given** `core/orchestrator.py` is inspected
**When** its imports are checked
**Then** it contains zero imports from `adapters/`, and zero imports of `slack_bolt` or `slack_sdk` (NFR15, NFR16)

## Tasks / Subtasks

- [x] Implement `Orchestrator` class in `src/open_fleet/core/orchestrator.py` (AC1–AC6)
  - [x] Define `_NotifyFn` type alias: `Callable[[str], Awaitable[None]]`
  - [x] Implement `__init__(self, gmail_client: GmailClient, llm_router: LLMRouter) -> None` with dependency injection
  - [x] Implement `async def run(self, timeframe: str, notify: _NotifyFn | None = None) -> list[str]` pipeline
  - [x] Pipeline step 1: `await self._gmail.fetch_emails(timeframe, notify=notify)` → raw messages
  - [x] Pipeline step 2: `[GmailClient.parse_email(msg) for msg in raw_messages]` → parsed email dicts (sync)
  - [x] Pipeline step 3: `await self._router.run_extraction(parsed_emails, timeframe, notify=notify)` → ExtractionResult
  - [x] Pipeline step 4: `ResponseFormatter.format(result)` → list[str] (sync call, return directly)
  - [x] Add specific except clauses: `GmailAuthError`, `GmailRateLimitError`, `LLMTimeoutError`
  - [x] Add catch-all `except Exception` with `logger.error(..., exc_info=True)` and generic error message
  - [x] Verify zero imports from `adapters/`, `slack_bolt`, `slack_sdk`
- [x] Write tests in `tests/test_core/test_orchestrator.py` (AC1–AC6)
  - [x] Test happy path: mock GmailClient + LLMRouter + verify ResponseFormatter.format called with result
  - [x] Test happy path: return value is list[str] from ResponseFormatter
  - [x] Test pipeline order: fetch → parse → run_extraction → format (mocks called in correct order)
  - [x] Test notify callback threaded to fetch_emails and run_extraction
  - [x] Test notify=None default (no callback) works without error
  - [x] Test GmailAuthError caught → returns exact error string (AC2)
  - [x] Test GmailRateLimitError caught → returns exact error string (AC3)
  - [x] Test LLMTimeoutError caught → returns exact error string (AC4)
  - [x] Test ValueError (unexpected, non-OpenFleetError) → returns generic error string (AC5)
  - [x] Test unexpected exception → logger.error called with exc_info=True (AC5)
  - [x] Test zero Slack imports via `ast` parse of `orchestrator.py` (AC6)
- [x] Run `pytest tests/test_core/test_orchestrator.py -v` — all pass
- [x] Run `ruff check src/open_fleet/core/orchestrator.py tests/test_core/test_orchestrator.py` — clean

## Dev Notes

### Orchestrator Design

```python
# src/open_fleet/core/orchestrator.py
import asyncio
import logging
from collections.abc import Awaitable, Callable

from open_fleet.core.response import ResponseFormatter
from open_fleet.exceptions import GmailAuthError, GmailRateLimitError, LLMTimeoutError
from open_fleet.llm.router import LLMRouter
from open_fleet.tools.gmail import GmailClient

logger = logging.getLogger("open_fleet.core.orchestrator")

_NotifyFn = Callable[[str], Awaitable[None]]


class Orchestrator:
    def __init__(self, gmail_client: GmailClient, llm_router: LLMRouter) -> None:
        self._gmail = gmail_client
        self._router = llm_router

    async def run(self, timeframe: str, notify: _NotifyFn | None = None) -> list[str]:
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
```

**Critical details:**
- `parse_email` is a `@staticmethod` on `GmailClient` — call as `GmailClient.parse_email(msg)`, not `self._gmail.parse_email(msg)`
- `notify` is threaded through to both `fetch_emails` and `run_extraction` — do NOT create a separate notify inside the orchestrator
- `ResponseFormatter.format()` is a `@staticmethod` — call as `ResponseFormatter.format(result)`, not via instance
- The catch-all `except Exception:` catches BOTH unexpected non-OpenFleetError exceptions AND any unhandled `OpenFleetError` subclasses (e.g., `GmailFetchError`, `LLMValidationError`, `LLMProviderError`) — all fall through to the generic handler

### Error Message Strings (copy exactly — no variation)

```python
# AC2
"❌ Gmail authentication expired — run scripts/setup_gmail_auth.py to reconnect"

# AC3
"❌ Gmail API rate limit — extraction could not complete after retries"

# AC4
"❌ LLM extraction failed — both LM Studio and Gemini unavailable"

# AC5 (generic fallback)
"❌ Unexpected error — check logs for details"
```

Format rules (from architecture): `❌` = failure (cannot complete), single space after emoji, em dash (—) separator, no trailing punctuation.

### Import Constraints (HARD RULES)

```python
# PERMITTED imports in core/orchestrator.py
from open_fleet.core.response import ResponseFormatter
from open_fleet.exceptions import GmailAuthError, GmailRateLimitError, LLMTimeoutError
from open_fleet.llm.router import LLMRouter
from open_fleet.tools.gmail import GmailClient

# FORBIDDEN — zero Slack imports
import slack_bolt          # FORBIDDEN
import slack_sdk           # FORBIDDEN
from adapters import ...   # FORBIDDEN
```

Note: `core/orchestrator.py` DOES import from `tools/` and `llm/` for type hints and the `GmailClient.parse_email` call. The hard constraint from the story AC is only "no imports from adapters/, slack_bolt, slack_sdk".

### Pipeline Data Flow

```
timeframe: str
    ↓
GmailClient.fetch_emails(timeframe, notify) → list[dict]  ← raw Gmail API message dicts
    ↓ (per-message)
GmailClient.parse_email(raw_msg) → dict[subject, sender, timestamp, body]
    ↓
LLMRouter.run_extraction(parsed_emails, timeframe, notify) → ExtractionResult
    ↓
ResponseFormatter.format(result) → list[str]
    ↓
return to Slack handler
```

`fetch_emails` → full Gmail API resource dicts (not the same as parsed dicts)
`parse_email` → `{"subject": str, "sender": str, "timestamp": str, "body": str}`
`run_extraction` → receives `list[dict]` with those 4 keys
`format()` → returns list because messages may be split at 4,000-char Slack limit

### Testing Pattern — asyncio.run() (not pytest-asyncio)

**Critical:** This project does NOT use `pytest-asyncio`. All async tests use `asyncio.run()`. See `tests/test_llm/test_router.py` for the established pattern.

```python
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from open_fleet.core.orchestrator import Orchestrator
from open_fleet.exceptions import GmailAuthError, GmailRateLimitError, LLMTimeoutError
from open_fleet.llm.schemas import ActionItem, ExtractionResult

# Helpers
def _gmail_client(fetch_return=None, parse_return=None):
    client = MagicMock()
    client.fetch_emails = AsyncMock(return_value=fetch_return or [{"id": "1"}])
    # parse_email is a @staticmethod — patch at class level for tests
    return client

def _router(run_return=None):
    router = MagicMock()
    router.run_extraction = AsyncMock(return_value=run_return or _valid_result())
    return router

# Test async methods with asyncio.run()
class TestHappyPath:
    def test_run_returns_formatted_messages(self):
        orch = Orchestrator(gmail_client=_gmail_client(), llm_router=_router())
        result = asyncio.run(orch.run("last 24 hours"))
        assert isinstance(result, list)
        assert len(result) >= 1
```

**Mocking `GmailClient.parse_email` (static method):**
```python
# parse_email is a @staticmethod, mock at the class level
with patch.object(GmailClient, "parse_email", return_value=_parsed_email()):
    result = asyncio.run(orch.run("last 24 hours"))
```

**Verifying logger.error with exc_info:**
```python
import logging
with patch.object(logging.getLogger("open_fleet.core.orchestrator"), "error") as mock_log:
    asyncio.run(orch.run("last 24 hours"))
    mock_log.assert_called_once()
    _, kwargs = mock_log.call_args
    assert kwargs.get("exc_info") is True
```

### Previous Story Intelligence (Story 4.1 — Response Formatter)

- `ResponseFormatter` is in `src/open_fleet/core/response.py` — **already implemented and in review**
- `ResponseFormatter.format()` is a `@staticmethod` returning `list[str]`
- `ExtractionResult` and `ActionItem` are the Pydantic types flowing into the orchestrator from `llm/schemas.py`
- The `_MAX_MSG_CHARS = 4_000` splitting logic is handled inside `ResponseFormatter.format()` — orchestrator just returns whatever `format()` gives it
- Test pattern from `test_response.py`: class-based test groups (`TestHeader`, `TestHappyPath`, etc.), no async tests needed there

**From Story 4.1 dev notes:**
- Import path: `from open_fleet.core.response import ResponseFormatter`
- `format()` receives a fully validated `ExtractionResult` — the orchestrator is responsible for ensuring it's valid before calling

### Previous Story Intelligence (Story 3.4 — LLM Router)

- `LLMRouter.run_extraction(email_batch, timeframe, notify=None) -> ExtractionResult`
- `email_batch` is `list[dict]` with keys: `subject`, `sender`, `timestamp`, `body` — exactly what `parse_email()` returns
- Already handles: LM Studio → Gemini fallback, validation retry (1x), provider logging (5 required fields)
- `LLMTimeoutError` is raised when BOTH providers fail — the router exhausts all fallback options before raising
- `LLMProviderError` or `LLMValidationError` may also propagate from router if Gemini also fails — both fall to orchestrator's catch-all `except Exception`

### Git Intelligence

Recent commits establishing patterns:
- `b8f871c` — Story 3.5: test pattern uses `asyncio.run()` for all async calls
- `ca90b24` — Story 3.4: LLMRouter uses `_NotifyFn = Callable[[str], Awaitable[None]]` — same type alias pattern to use in orchestrator
- `70a7e05` — Story 3.3: GeminiProvider follows config injection (constructor args only)

File patterns established in previous stories:
- Module logger: `logging.getLogger("open_fleet.<module>")` e.g. `"open_fleet.core.orchestrator"`
- Private type alias: `_NotifyFn = Callable[[str], Awaitable[None]]` — both `router.py` and `gmail.py` already define this; orchestrator defines its own (no shared import)

### Existing Stub

`src/open_fleet/core/orchestrator.py` already exists as a stub:
```python
# src/open_fleet/core/orchestrator.py
"""Extraction orchestrator.

Implemented in Story 4.2.
"""
```
Replace entire file content — do not append.

### Project Structure Notes

- Implementation: `src/open_fleet/core/orchestrator.py`
- Tests: `tests/test_core/test_orchestrator.py` (does not exist yet — create it)
- No `__init__.py` export needed — import directly: `from open_fleet.core.orchestrator import Orchestrator`
- `tests/test_core/__init__.py` already exists (do not recreate)

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 4.2: Extraction Orchestrator]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication Patterns — Error Handling Convention]
- [Source: _bmad-output/planning-artifacts/architecture.md#Structure Patterns — Module Responsibility Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture.md#Format Patterns — Slack Message Format]
- [Source: _bmad-output/planning-artifacts/architecture.md#Decision Impact Analysis — Implementation Sequence step 8]
- [Source: src/open_fleet/tools/gmail.py — GmailClient.fetch_emails(), parse_email()]
- [Source: src/open_fleet/llm/router.py — LLMRouter.run_extraction()]
- [Source: src/open_fleet/core/response.py — ResponseFormatter.format()]
- [Source: tests/test_llm/test_router.py — asyncio.run() test pattern]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented `Orchestrator` class in `src/open_fleet/core/orchestrator.py` with 4-step pipeline and 4 error handlers
- `parse_email` called as `@staticmethod` (`GmailClient.parse_email(msg)`) — not via instance
- `notify` callback threaded through to both `fetch_emails` and `run_extraction` with `notify=None` default
- Catch-all `except Exception` handles both unexpected non-OpenFleetError exceptions and unhandled OpenFleetError subclasses (e.g. `LLMProviderError`, `GmailFetchError`)
- 21 tests in `tests/test_core/test_orchestrator.py` — all pass; ruff clean
- Full regression suite: 239 passed, 0 failures

### File List

- `src/open_fleet/core/orchestrator.py` — Orchestrator class, `_NotifyFn` alias, `run()` pipeline with error handling
- `tests/test_core/test_orchestrator.py` — 21 tests: TestHappyPath (8), TestNotifyCallback (3), TestGmailErrorHandling (4), TestLLMErrorHandling (1), TestUnexpectedErrorHandling (4), TestNoSlackImports (1)

## Change Log

- 2026-03-15: Story 4.2 created via create-story workflow.
- 2026-03-15: Implementation complete. Orchestrator class implemented with full pipeline and all error handlers. 19 tests passing, ruff clean. Story status updated to review.
- 2026-03-15: Code review fixes applied. Added explicit pipeline order test (H1), added `spec=LLMRouter` to `_router()` mock (H2), patched `parse_email` in fragile test (M1), added `format()` exception test (M2). 21 tests passing, ruff clean.
