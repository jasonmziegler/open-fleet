# Story 1.2: Typed Exception Hierarchy

Status: done

## Story

As a developer,
I want a typed exception hierarchy defined in `exceptions.py` before any other module is implemented,
so that every error condition across the codebase has a named, specific type that can be caught with precision.

## Acceptance Criteria

**Given** `src/open_fleet/exceptions.py` is imported in a test
**When** each exception class is inspected
**Then** `OpenFleetError` is the base class for all project exceptions, inheriting from `Exception`
**And** `GmailError(OpenFleetError)` is the base for all Gmail failures, with subclasses `GmailAuthError`, `GmailRateLimitError`, `GmailFetchError`
**And** `LLMError(OpenFleetError)` is the base for all LLM failures, with subclasses `LLMTimeoutError`, `LLMValidationError`, `LLMProviderError`
**And** `ConfigError(OpenFleetError)` covers missing or invalid configuration values
**And** catching `OpenFleetError` catches all of the above subclasses
**And** no other module in the project defines custom exception classes

## Tasks / Subtasks

- [x] Verify `src/open_fleet/exceptions.py` satisfies all ACs (AC: all)
  - [x] Confirm `OpenFleetError(Exception)` base class present
  - [x] Confirm `GmailError(OpenFleetError)` with subclasses `GmailAuthError`, `GmailRateLimitError`, `GmailFetchError`
  - [x] Confirm `LLMError(OpenFleetError)` with subclasses `LLMTimeoutError`, `LLMValidationError`, `LLMProviderError`
  - [x] Confirm `ConfigError(OpenFleetError)` present
- [x] Run existing test suite (AC: all)
  - [x] Run `pytest tests/test_core/test_exceptions.py -v` and confirm all 6 tests pass
- [x] Scan codebase for custom exception definitions outside `exceptions.py` (AC: last AC)
  - [x] Search for `class \w*Error` in all `.py` files except `exceptions.py`
  - [x] Confirm zero results

## Dev Notes

### Critical: Implementation Already Complete

**The Story 1.1 dev agent implemented `exceptions.py` beyond the stub specification.** The file at `src/open_fleet/exceptions.py` is fully implemented with the complete exception hierarchy. A test file at `tests/test_core/test_exceptions.py` also already exists.

**Dev agent task for this story is verification only:**
1. Read `src/open_fleet/exceptions.py` — confirm complete hierarchy
2. Run `pytest tests/test_core/test_exceptions.py -v` — confirm all 6 tests pass
3. Grep for additional exception class definitions in other modules — confirm none exist

If all checks pass, mark the story done. Do NOT modify `exceptions.py` or the test file unless a gap is found.

### Current Implementation State

`src/open_fleet/exceptions.py` contains (as verified at story creation time):

```python
class OpenFleetError(Exception): pass

class GmailError(OpenFleetError): pass
class GmailAuthError(GmailError): pass       # OAuth token invalid/expired
class GmailRateLimitError(GmailError): pass  # HTTP 429
class GmailFetchError(GmailError): pass      # General fetch failure

class LLMError(OpenFleetError): pass
class LLMTimeoutError(LLMError): pass        # 30s threshold exceeded
class LLMValidationError(LLMError): pass     # Pydantic schema mismatch
class LLMProviderError(LLMError): pass       # Provider unreachable

class ConfigError(OpenFleetError): pass      # Missing/invalid .env vars
```

`tests/test_core/test_exceptions.py` exists with 6 tests:
- `test_open_fleet_error_is_exception`
- `test_gmail_hierarchy`
- `test_llm_hierarchy`
- `test_config_error_hierarchy`
- `test_catching_base_catches_all_subclasses`
- `test_exceptions_carry_message`

### Previous Story Intelligence (Story 1.1)

The Story 1.1 dev agent noted these important lessons that carry forward:
- **Python 3.14 compatibility**: `protobuf==5.29.6` was added to `requirements.txt` for Python 3.14 compatibility
- **`pytest==9.0.2`** is the actual installed version (9.1.0 was unavailable on PyPI)
- **`google-generativeai==0.8.6`** is the actual installed version (0.10.0 was unavailable on PyPI); emits FutureWarning about deprecation — expected
- **Windows stdout encoding**: Python 3.14 on Windows defaults to cp1252; apply UTF-8 encoding wrapper if writing any scripts that output emoji
- **ruff**: run `ruff check src/ tests/` and confirm zero warnings after any changes

### Exception Usage Across the Codebase

These exception classes are actively used throughout the codebase (confirmed by Epics 3 & 4 implementation):
- `GmailAuthError`, `GmailRateLimitError`, `GmailFetchError` — `tools/gmail.py`
- `LLMTimeoutError`, `LLMValidationError`, `LLMProviderError` — `llm/lmstudio.py`, `llm/gemini.py`, `llm/router.py`
- `OpenFleetError` — `core/orchestrator.py` (catch boundary for all structured failures)
- `ConfigError` — `config.py` (Story 1.3)

Do NOT rename, remove, or restructure these classes — every upstream module depends on the exact class names.

### Architecture Compliance

- `exceptions.py` is importable by any module — no layer restriction [Source: architecture.md#Structure Patterns]
- No circular dependencies — `exceptions.py` imports nothing from the project
- No other module may define custom exception classes [Source: epics.md#Story 1.2 AC]
- Exception raising rule: always raise specific subclass, never `OpenFleetError` directly [Source: architecture.md#Process Patterns]

### Module Boundary Rules (Reminder)

```
exceptions.py  → importable by ALL modules (only cross-layer import allowed)
core/          → imports exceptions, NOT adapters/tools/llm
tools/         → imports exceptions, NOT core/llm
llm/           → imports exceptions, NOT core/tools/adapters
adapters/      → imports exceptions + core (NOT tools/llm directly)
```

### Project Structure Notes

- `src/open_fleet/exceptions.py` — target file (fully implemented)
- `tests/test_core/test_exceptions.py` — test file (fully implemented)
- No new files to create in this story

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.2: Typed Exception Hierarchy]
- [Source: _bmad-output/planning-artifacts/architecture.md#API & Communication Patterns — Error Handling Convention]
- [Source: _bmad-output/planning-artifacts/architecture.md#Process Patterns — Exception Raising]
- [Source: _bmad-output/implementation-artifacts/1-1-project-scaffold-dependency-configuration.md#Dev Agent Record]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Verified `src/open_fleet/exceptions.py` fully implements the typed exception hierarchy per all ACs: `OpenFleetError(Exception)` as base, `GmailError`/`GmailAuthError`/`GmailRateLimitError`/`GmailFetchError`, `LLMError`/`LLMTimeoutError`/`LLMValidationError`/`LLMProviderError`, and `ConfigError(OpenFleetError)`.
- Ran `pytest tests/test_core/test_exceptions.py -v`: all 6 tests passed.
- Grepped `class \w+Error` across all `.py` files: matches outside `exceptions.py` are all test grouping classes (`TestGmailErrorHandling`, `TestLLMErrorHandling`, `TestConnectionError`, etc.) — not exception definitions. AC satisfied.
- Full regression suite: 256 tests passed, 0 failures (2 pre-existing warnings only).
- No files created or modified — verification-only story as documented in Dev Notes.

### File List

- `tests/test_core/test_exceptions.py` — Updated: added `GmailError` and `LLMError` to catch-all test; parameterized message-carry test to cover all 10 exception classes

### Change Log

- 2026-03-17: Verification-only story completed. Confirmed exceptions.py fully implements typed hierarchy per all ACs. All 6 exception tests and full 256-test regression suite pass. Zero custom exception definitions found outside exceptions.py.
- 2026-03-17: **Code review (claude-opus-4-6)** — Found 3 MEDIUM, 2 LOW issues. Fixed M2 & M3 (intermediate base classes missing from catch-all test) and L2 (parameterized message test to cover all 10 classes). Fixed L1 (doc inconsistency "5 tests" → "6 tests"). Flagged M1 (Story 1.1 sprint status stuck at `review`) as out-of-scope. Post-fix: 15 exception tests pass, 265 full regression pass.
