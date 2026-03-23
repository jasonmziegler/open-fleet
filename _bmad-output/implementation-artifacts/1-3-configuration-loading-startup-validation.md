# Story 1.3: Configuration Loading & Startup Validation

Status: done

## Story

As Jason (operator),
I want all configuration loaded from `.env` at startup with immediate, specific error messages if anything is missing or invalid,
so that I can fix misconfiguration in seconds rather than debugging why the agent silently failed.

## Acceptance Criteria

1. **Given** the agent is started with a missing required env var (e.g., `SLACK_BOT_TOKEN` absent)
   **When** `config.py` runs its validation
   **Then** a `ConfigError` is raised immediately, before any external connection is attempted
   **And** the error message names the exact missing variable and its expected format

2. **Given** all required env vars are present and `token.json` exists at the configured path
   **When** `config.py` runs its validation
   **Then** a `Config` object is returned with all values accessible as typed attributes
   **And** optional vars (`LM_STUDIO_BASE_URL`, `GMAIL_TOKEN_PATH`, `LOG_DIR`, `LM_STUDIO_TIMEOUT_SECS`) use documented defaults when absent from `.env`

3. **Given** `token.json` does not exist at the configured path
   **When** `config.py` runs its validation
   **Then** a `ConfigError` is raised with a message directing the user to run `scripts/setup_gmail_auth.py`

4. **Given** `config.py` is imported into a test without an `.env` file present
   **When** config values are passed as constructor arguments to other modules
   **Then** all other modules operate correctly without reading any env vars directly (config injection pattern enforced)

## Tasks / Subtasks

- [x] Verify `src/open_fleet/config.py` satisfies all ACs (AC: all)
  - [x] Confirm `Config` dataclass has all required fields as typed attributes
  - [x] Confirm `load()` raises `ConfigError` for missing required vars with specific messages
  - [x] Confirm `load()` raises `ConfigError` when `token.json` is absent with actionable message
  - [x] Confirm optional vars use documented defaults when absent
  - [x] Confirm `Config` is frozen (immutable) to prevent shared state mutation
- [x] Run existing test suite (AC: all)
  - [x] Run `pytest tests/test_core/test_config.py -v` and confirm all tests pass
- [x] Verify config injection pattern across the codebase (AC: 4)
  - [x] Grep for `os.getenv` or `os.environ` in all `.py` files except `config.py` and test files
  - [x] Grep for `load_dotenv` in all `.py` files except `config.py`
  - [x] Confirm `config.py` is imported only by `main.py`
- [x] Run full regression suite (AC: all)
  - [x] Run `pytest` and confirm zero failures

## Dev Notes

### Critical: Implementation Already Complete

**The implementation of `config.py` was completed during previous stories (likely Story 4.3 or earlier).** The file at `src/open_fleet/config.py` is fully implemented with:
- `Config` frozen dataclass with all 7 typed fields
- `load()` function that validates required vars, resolves optional vars with defaults, checks token.json existence
- Proper `ConfigError` exceptions with actionable error messages
- `env_file=None` parameter for test isolation

**A test file at `tests/test_core/test_config.py` already exists with 8 tests:**
- `test_missing_single_required_var_raises`
- `test_missing_multiple_required_vars_raises`
- `test_missing_token_json_raises`
- `test_returns_config_with_typed_attributes`
- `test_optional_vars_use_defaults`
- `test_optional_vars_overridden`
- `test_invalid_timeout_raises`
- `test_config_is_frozen`

**Dev agent task for this story is verification only:**
1. Read `src/open_fleet/config.py` — confirm complete implementation matches all ACs
2. Run `pytest tests/test_core/test_config.py -v` — confirm all 8 tests pass
3. Verify config injection pattern: grep for direct env var access outside `config.py`
4. Verify `config.py` is imported only by `main.py`
5. Run full regression suite

If all checks pass, mark the story done. Do NOT modify `config.py` or the test file unless a gap is found.

### Current Implementation State

`src/open_fleet/config.py` contains:

```python
_REQUIRED: dict[str, str] = {
    "SLACK_BOT_TOKEN": "xoxb-...",
    "SLACK_APP_TOKEN": "xapp-...",
    "GEMINI_API_KEY": "string (from Google AI Studio)",
}

_DEFAULTS: dict[str, str] = {
    "LM_STUDIO_BASE_URL": "http://localhost:1234/v1",
    "LM_STUDIO_TIMEOUT_SECS": "30",
    "GMAIL_TOKEN_PATH": "token.json",
    "LOG_DIR": "logs",
}

@dataclass(frozen=True)
class Config:
    slack_bot_token: str
    slack_app_token: str
    gemini_api_key: str
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_timeout_secs: int = 30
    gmail_token_path: Path = field(default_factory=lambda: Path("token.json"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))

def load(env_file: str | Path | None = ".env") -> Config:
    # Validates required vars, resolves optional vars, checks token.json
```

### Required Environment Variables

| Variable | Format | Required |
|---|---|---|
| `SLACK_BOT_TOKEN` | `xoxb-...` | Yes |
| `SLACK_APP_TOKEN` | `xapp-...` | Yes |
| `GEMINI_API_KEY` | string | Yes |
| `LM_STUDIO_BASE_URL` | URL | No (default: `http://localhost:1234/v1`) |
| `LM_STUDIO_TIMEOUT_SECS` | integer | No (default: `30`) |
| `GMAIL_TOKEN_PATH` | file path | No (default: `token.json`) |
| `LOG_DIR` | directory path | No (default: `logs`) |

### Config Usage in main.py (Verified)

`main.py` is the ONLY module that imports `config.py`. It calls `config_module.load()` and passes config values to constructors:

```python
cfg = config_module.load()
gmail_client = GmailClient(token_path=cfg.gmail_token_path)
lmstudio = LMStudioProvider(base_url=cfg.lm_studio_base_url, timeout_secs=cfg.lm_studio_timeout_secs)
gemini = GeminiProvider(api_key=cfg.gemini_api_key)
```

This confirms the config injection pattern is enforced — no module reads `.env` directly.

### Previous Story Intelligence (Story 1.2)

Key learnings that carry forward:
- **Python 3.14 compatibility**: `protobuf==5.29.6` was added for Python 3.14 compatibility
- **`pytest==9.0.2`** is the actual installed version (9.1.0 was unavailable)
- **`google-generativeai==0.8.6`** is the actual installed version (0.10.0 was unavailable)
- **Windows stdout encoding**: Python 3.14 on Windows defaults to cp1252
- **ruff**: run `ruff check src/ tests/` and confirm zero warnings after any changes
- **Full regression suite**: 265 tests existed at end of Story 1.2

### Architecture Compliance

- `config.py` imports only `os`, `dataclasses`, `pathlib`, `dotenv`, and `open_fleet.exceptions` — no circular dependencies [Source: architecture.md#Structure Patterns]
- `Config` is a frozen dataclass — immutable, preventing shared state mutation
- `load(env_file=None)` enables test isolation without `.env` file [Source: architecture.md#Config Injection Pattern]
- `config.py` is imported by `main.py` ONLY — verified in current codebase [Source: architecture.md#Structure Patterns]

### Module Boundary Rules (Reminder)

```
config.py      -> imported by main.py ONLY
exceptions.py  -> importable by ALL modules
core/          -> imports exceptions, NOT adapters/tools/llm
tools/         -> imports exceptions, NOT core/llm
llm/           -> imports exceptions, NOT core/tools/adapters
adapters/      -> imports exceptions + core (NOT tools/llm directly)
```

### Project Structure Notes

- `src/open_fleet/config.py` — target file (fully implemented)
- `tests/test_core/test_config.py` — test file (fully implemented, 8 tests)
- No new files to create in this story

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.3: Configuration Loading & Startup Validation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Authentication & Security]
- [Source: _bmad-output/planning-artifacts/architecture.md#Structure Patterns — Config Injection Pattern]
- [Source: _bmad-output/planning-artifacts/architecture.md#Naming Patterns — Environment Variable Names]
- [Source: _bmad-output/implementation-artifacts/1-1-project-scaffold-dependency-configuration.md#Dev Agent Record]
- [Source: _bmad-output/implementation-artifacts/1-2-typed-exception-hierarchy.md#Previous Story Intelligence]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — verification-only story, no implementation changes required.

### Completion Notes List

- ✅ Verified `Config` frozen dataclass has all 7 typed fields matching ACs
- ✅ Verified `load()` raises `ConfigError` for missing required vars with exact variable name + expected format in message
- ✅ Verified `ConfigError` raised when `token.json` absent, with `setup_gmail_auth.py` actionable message
- ✅ Verified optional vars (`LM_STUDIO_BASE_URL`, `LM_STUDIO_TIMEOUT_SECS`, `GMAIL_TOKEN_PATH`, `LOG_DIR`) use documented defaults
- ✅ Verified `Config(frozen=True)` — mutation raises `FrozenInstanceError`
- ✅ All 8 tests in `tests/test_core/test_config.py` pass
- ✅ Config injection pattern confirmed: `os.environ` / `os.getenv` / `load_dotenv` used only in `config.py`
- ✅ `config.py` imported only by `main.py` (via `import open_fleet.config as config_module`)
- ✅ Code review fixed M1 (DRY: Config field defaults now reference _DEFAULTS) and M2 (positive-integer validation for LM_STUDIO_TIMEOUT_SECS)
- ✅ Added `test_non_positive_timeout_raises` parametrized test (3 cases: 0, -1, -100)
- ✅ Full regression suite: 268 passed, 0 failures, 1 warning

### File List

- `src/open_fleet/config.py` (modified: field defaults now reference `_DEFAULTS` to eliminate duplication; added positive-integer validation for `LM_STUDIO_TIMEOUT_SECS`)
- `tests/test_core/test_config.py` (modified: added `test_non_positive_timeout_raises` parametrized test)

**Note (M3):** `tests/test_core/test_exceptions.py` was found modified but uncommitted — changes originated from Story 1.2 (parametrized `test_exceptions_carry_message`, added base classes to `test_catching_base_catches_all_subclasses`). These changes are unrelated to this story but should be committed.
