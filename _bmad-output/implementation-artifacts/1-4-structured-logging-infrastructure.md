# Story 1.4: Structured Logging Infrastructure

Status: done

## Story

As a developer,
I want structured JSON logging with a rotating file handler initialized at process start,
so that every run produces queryable diagnostic logs retained for 7 days without manual cleanup.

## Acceptance Criteria

1. **Given** `logging_setup.py` is called in `main.py` before any other module initializes
   **When** any module calls `logging.getLogger("open_fleet.<module>")`
   **Then** log records are written to `logs/open_fleet.log` in JSON format with fields: `timestamp`, `level`, `module`
   **And** the same log records are echoed to stdout via `StreamHandler` for development visibility

2. **Given** `logs/open_fleet.log` reaches 10MB
   **When** the next log entry is written
   **Then** the log file rotates to a `.log.1` backup and a fresh `open_fleet.log` is created
   **And** up to 7 backup files are retained (~70MB maximum total log storage)

3. **Given** the test suite runs without a `.env` file
   **When** `logging_setup.py` is imported in tests
   **Then** test log output goes to stdout only and does not write to `logs/open_fleet.log`

## Tasks / Subtasks

- [x] Verify `src/open_fleet/logging_setup.py` satisfies all ACs (AC: all)
  - [x] Confirm `_JsonFormatter` emits JSON with required fields: `timestamp`, `level`, `module`
  - [x] Confirm `configure(log_dir=...)` sets up both RotatingFileHandler and StreamHandler
  - [x] Confirm `configure(log_dir=None)` sets up StreamHandler only (test mode)
  - [x] Confirm RotatingFileHandler uses 10MB max size and 7 backup files
  - [x] Confirm idempotent handler registration (no duplicate handlers)
  - [x] Confirm log directory creation with `parents=True`
- [x] Run existing test suite (AC: all)
  - [x] Run `pytest tests/test_core/test_logging_setup.py -v` and confirm all tests pass
- [x] Verify initialization order in `main.py` (AC: 1)
  - [x] Confirm `logging_setup.configure()` is called after `config.load()` but before any other module initializes
  - [x] Confirm `cfg.log_dir` is passed to `configure()`
- [x] Verify logger naming convention across codebase (AC: 1)
  - [x] Grep for `getLogger` calls and confirm pattern `logging.getLogger("open_fleet.<module>")`
- [x] Verify extraction logging includes required fields (architecture constraint)
  - [x] Confirm `router.py` logs with `extra={"provider", "email_count", "action_item_count", "duration_ms", "error"}`
- [x] Run full regression suite (AC: all)
  - [x] Run `pytest` and confirm zero failures

## Dev Notes

### Critical: Implementation Already Complete

**The implementation of `logging_setup.py` was completed during previous stories.** The file at `src/open_fleet/logging_setup.py` is fully implemented with:
- `_JsonFormatter` class producing JSON records with `timestamp`, `level`, `module`, `message`, and `exc_info` fields
- `configure(log_dir: Path | None = None)` function with two modes:
  - **Test mode** (`log_dir=None`): StreamHandler to stdout only
  - **Production mode** (`log_dir` provided): RotatingFileHandler + StreamHandler
- Constants: `_MAX_BYTES = 10 * 1024 * 1024` (10MB), `_BACKUP_COUNT = 7`, `_LOG_FILENAME = "open_fleet.log"`
- Idempotent: checks for existing handlers before adding new ones
- Creates log directory with `parents=True` if missing

**A test file at `tests/test_core/test_logging_setup.py` already exists with 12+ tests** covering:
- JSON format validation and required fields
- Test mode (stdout only, no file output)
- Production mode (file + stdout output)
- RotatingFileHandler configuration (maxBytes, backupCount)
- Log directory creation
- Idempotency (no duplicate handlers)
- Propagation settings

**Dev agent task for this story is verification only:**
1. Read `src/open_fleet/logging_setup.py` — confirm complete implementation matches all ACs
2. Run `pytest tests/test_core/test_logging_setup.py -v` — confirm all tests pass
3. Verify initialization order in `main.py`: `config.load()` → `logging_setup.configure(cfg.log_dir)` → component creation
4. Verify logger naming convention: grep for `getLogger` calls across codebase
5. Verify extraction logging fields in `router.py` match architecture requirements
6. Run full regression suite

If all checks pass, mark the story done. Do NOT modify `logging_setup.py` or the test file unless a gap is found.

### Current Implementation State

`src/open_fleet/logging_setup.py` contains:

```python
_LOG_FORMAT_FIELDS = ("timestamp", "level", "module")
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_BACKUP_COUNT = 7
_LOG_FILENAME = "open_fleet.log"

class _JsonFormatter(logging.Formatter):
    # Emits JSON: {"timestamp": "...", "level": "INFO", "module": "open_fleet.test", "message": "..."}

def configure(log_dir: Path | None = None) -> None:
    # log_dir=None → stdout only (test mode)
    # log_dir=Path → RotatingFileHandler + StreamHandler (production mode)
```

### Initialization Order in main.py (Verified Pattern)

```python
cfg = config_module.load()                           # 1. Config first
logging_setup.configure(log_dir=cfg.log_dir)         # 2. Logging second
# ... then build components ...
gmail_client = GmailClient(token_path=cfg.gmail_token_path)
lmstudio = LMStudioProvider(...)
gemini = GeminiProvider(...)
```

### Logger Naming Convention

All modules must use: `logging.getLogger("open_fleet.<module_name>")`

Example from `router.py`:
```python
logger = logging.getLogger("open_fleet.router")
```

### Extraction Log Record Schema (Architecture Constraint)

All extraction log calls must include these fields in `extra`:
```python
logger.info("extraction_complete", extra={
    "provider": "lmstudio",       # "lmstudio" | "gemini"
    "email_count": 187,           # int
    "action_item_count": 14,      # int
    "duration_ms": 23450,         # int
    "error": None,                # str | None
})
```

### Previous Story Intelligence (Story 1.3)

Key learnings that carry forward:
- **Python 3.14 compatibility**: `protobuf==5.29.6` added for Python 3.14
- **`pytest==9.0.2`** is actual installed version (9.1.0 unavailable)
- **Windows stdout encoding**: Python 3.14 on Windows defaults to cp1252
- **ruff**: run `ruff check src/ tests/` and confirm zero warnings after any changes
- **Full regression suite**: 268 tests existed at end of Story 1.3
- **Code review applied DRY fix**: Config field defaults now reference `_DEFAULTS`
- Story 1.3 was also verification-only — same pattern applies here

### Architecture Compliance

- `logging_setup.py` imports only `logging`, `logging.handlers`, `pathlib`, `json`, `datetime` — stdlib only, no project imports [Source: architecture.md#Implementation Sequence]
- `logging_setup.py` is initialized 3rd in sequence: exceptions → config → **logging** → schemas → providers [Source: architecture.md#Implementation Sequence]
- JSON formatter must emit `timestamp`, `level`, `module` fields minimum [Source: architecture.md#Logging Implementation]
- No external logging library — uses Python built-in `logging` module [Source: architecture.md#Logging Implementation]
- `logs/` directory is gitignored — log files are local-only [Source: .gitignore]

### Module Boundary Rules (Reminder)

```
config.py        -> imported by main.py ONLY
exceptions.py    -> importable by ALL modules
logging_setup.py -> imported by main.py ONLY (initialization at process start)
core/            -> imports exceptions, NOT adapters/tools/llm
tools/           -> imports exceptions, NOT core/llm
llm/             -> imports exceptions, NOT core/tools/adapters
adapters/        -> imports exceptions + core (NOT tools/llm directly)
```

### Project Structure Notes

- `src/open_fleet/logging_setup.py` — target file (fully implemented, 83 lines)
- `tests/test_core/test_logging_setup.py` — test file (fully implemented, 12+ tests)
- No new files to create in this story

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.4: Structured Logging Infrastructure]
- [Source: _bmad-output/planning-artifacts/architecture.md#Logging Implementation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Log Record Schema]
- [Source: _bmad-output/planning-artifacts/architecture.md#Implementation Sequence]
- [Source: _bmad-output/planning-artifacts/architecture.md#Enforcement Guidelines]
- [Source: _bmad-output/implementation-artifacts/1-3-configuration-loading-startup-validation.md#Previous Story Intelligence]

## Dev Agent Record

### Agent Model Used

claude-opus-4-6

### Debug Log References

None — verification-only story, no implementation changes required.

### Completion Notes List

- ✅ Verified `_JsonFormatter` emits JSON with `timestamp`, `level`, `module`, `message`, `exc_info` fields (lines 36-44)
- ✅ Verified `configure(log_dir=Path)` sets up RotatingFileHandler + StreamHandler (lines 63-79)
- ✅ Verified `configure(log_dir=None)` sets up StreamHandler only for test mode (lines 63-66, conditional at 69)
- ✅ Verified RotatingFileHandler uses `_MAX_BYTES = 10MB` and `_BACKUP_COUNT = 7` (lines 27-28, 73-75)
- ✅ Verified idempotent handler registration via `if root_logger.handlers: return` (lines 57-58)
- ✅ Verified log directory creation with `log_dir.mkdir(parents=True, exist_ok=True)` (line 71)
- ✅ All 10 tests in `tests/test_core/test_logging_setup.py` pass
- ✅ Initialization order in `main.py` correct: `config.load()` (line 33) → `logging_setup.configure(log_dir=cfg.log_dir)` (line 40) → component creation (line 45+)
- ✅ All `getLogger` calls across codebase use `"open_fleet.<module>"` naming convention (9 modules verified)
- ✅ `router.py` extraction logging includes all 5 required architecture fields: `provider`, `email_count`, `action_item_count`, `duration_ms`, `error` (lines 128-134)
- ✅ Full regression suite: 273 passed, 0 failures, 1 warning
- ℹ️ Pre-existing ruff warnings (15 total across other stories' test files) — not introduced by this story

### Senior Developer Review (AI)

**Reviewer:** Jason | **Date:** 2026-03-23 | **Model:** claude-opus-4-6

**Issues Found:** 1 High, 3 Medium, 3 Low — all HIGH and MEDIUM fixed automatically.

| # | Severity | Description | Resolution |
|---|----------|-------------|------------|
| H1 | HIGH | `_JsonFormatter.format()` dropped all `extra` fields — architecture Log Record Schema fields (`provider`, `email_count`, `action_item_count`, `duration_ms`, `error`) silently lost from JSON output | Fixed: formatter now iterates `vars(record)` and includes non-builtin attrs |
| M1 | MEDIUM | Timestamp lacked UTC timezone offset (naive `%Y-%m-%dT%H:%M:%S`) — violates architecture ISO8601 mandate | Fixed: uses `datetime.fromtimestamp(record.created, tz=timezone.utc)` with `+00:00` suffix |
| M2 | MEDIUM | 3 unused imports in `test_logging_setup.py` (`sys`, `StringIO`, `Path`) — ruff F401 | Fixed: removed unused imports |
| M3 | MEDIUM | No test coverage for `extra` fields in JSON output — root cause of H1 going undetected | Fixed: added `test_extra_fields_included_in_json_output` and `test_timestamp_includes_utc_offset` |
| L1 | LOW | Timestamp lacked sub-second precision | Fixed alongside M1 — now includes milliseconds |
| L2 | LOW | Story Dev Notes claim "12+ tests" but actual count was 10 | Informational — now 12 tests after M3 fix |
| L3 | LOW | Completion Notes line references slightly off (e.g., "lines 36-44" vs actual 35-44) | Informational |

**Regression:** 275 passed, 0 failures, 1 warning. Ruff clean on changed files.

### File List

- `src/open_fleet/logging_setup.py` — Fixed `_JsonFormatter` to include `extra` fields and UTC ISO8601 timestamps
- `tests/test_core/test_logging_setup.py` — Removed unused imports; added 2 tests for extra fields and UTC timestamp
