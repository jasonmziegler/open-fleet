# Story 1.1: Project Scaffold & Dependency Configuration

Status: Done

## Story

As a developer,
I want a properly structured `src/open_fleet/` project with all module directories, pinned dependencies, and version-control exclusions in place,
So that the interface-isolation architecture is enforced by directory boundaries from day one and every dependency version is deterministic.

## Acceptance Criteria

**Given** a fresh clone of the repository
**When** the developer runs `pip install -r requirements.txt -r requirements-dev.txt` and then `python test_setup.py`
**Then** all required packages import successfully with no errors
**And** the directory structure exists: `src/open_fleet/`, `adapters/slack/`, `core/`, `tools/`, `llm/`, `tests/test_core/`, `tests/test_tools/`, `tests/test_llm/`, `logs/`
**And** `requirements.txt` contains pinned production dependencies: `slack-bolt==1.27.0`, `slack-sdk==3.40.1`, `google-api-python-client==2.190.0`, `google-auth-oauthlib==1.2.4`, `google-generativeai==0.10.0`, `python-dotenv==1.2.1`, `pydantic==2.12.5`, `aiohttp`
**And** `requirements-dev.txt` contains: `pytest==9.1.0`, `black==26.1.0`, `ruff==0.15.1`
**And** `.env.example` lists all required environment variables with placeholder values and inline comments
**And** `.gitignore` excludes `.env`, `token.json`, and `logs/`
**And** `start.bat` exists as a stub entry point (`python -m open_fleet.main`)

## Tasks / Subtasks

- [x] Update `requirements.txt` to pinned production versions (AC: #1)
  - [x] Replace all existing packages with architecture-specified pinned versions
  - [x] Remove outdated packages: `requests==2.31.0`, `google-auth-httplib2==0.2.0`, `flake8==7.0.0`, `pytest`, `black` (moving those last 3 to dev requirements)
  - [x] Add `pydantic==2.12.5` (was missing from original requirements.txt entirely)
  - [x] Pin `aiohttp` to latest stable (verify current stable on PyPI — target ~3.11.x)
- [x] Create `requirements-dev.txt` with dev tooling (AC: #1)
  - [x] `pytest==9.1.0`, `black==26.1.0`, `ruff==0.15.1`
- [x] Create `src/open_fleet/` directory structure with all `__init__.py` stubs (AC: #2)
  - [x] `src/open_fleet/__init__.py`
  - [x] `src/open_fleet/main.py` (stub — see Dev Notes for exact content)
  - [x] `src/open_fleet/config.py` (stub — empty placeholder only, NOT implemented in this story)
  - [x] `src/open_fleet/exceptions.py` (stub — empty placeholder only, NOT implemented in this story)
  - [x] `src/open_fleet/logging_setup.py` (stub — empty placeholder only, NOT implemented in this story)
  - [x] `src/open_fleet/adapters/__init__.py`
  - [x] `src/open_fleet/adapters/slack/__init__.py`
  - [x] `src/open_fleet/adapters/slack/handler.py` (stub)
  - [x] `src/open_fleet/core/__init__.py`
  - [x] `src/open_fleet/core/orchestrator.py` (stub)
  - [x] `src/open_fleet/core/response.py` (stub)
  - [x] `src/open_fleet/tools/__init__.py`
  - [x] `src/open_fleet/tools/gmail.py` (stub)
  - [x] `src/open_fleet/llm/__init__.py`
  - [x] `src/open_fleet/llm/router.py` (stub)
  - [x] `src/open_fleet/llm/lmstudio.py` (stub)
  - [x] `src/open_fleet/llm/gemini.py` (stub)
  - [x] `src/open_fleet/llm/schemas.py` (stub)
- [x] Create `tests/` directory structure (AC: #2)
  - [x] `tests/__init__.py`
  - [x] `tests/test_core/__init__.py`
  - [x] `tests/test_tools/__init__.py`
  - [x] `tests/test_llm/__init__.py`
- [x] Create `logs/` directory with `.gitkeep` (AC: #2)
  - [x] Add `.gitkeep` inside so the directory is tracked by git without logging its contents (already gitignored)
- [x] Create `scripts/` directory (AC: implied by architecture)
  - [x] `scripts/__init__.py` (empty — placeholder for `setup_gmail_auth.py` created in Story 2.1)
- [x] Create `.env.example` with all required env vars (AC: #3)
  - [x] See Dev Notes for exact contents
- [x] Verify `.gitignore` covers required exclusions (AC: #4)
  - [x] Confirm `.env`, `token.json`, `logs/` are already excluded (they are — `.gitignore` already correct, no changes needed)
- [x] Create `start.bat` stub (AC: #5)
  - [x] See Dev Notes for exact contents
- [x] Update `test_setup.py` to verify all new requirements and directory structure (AC: #1-#2)
  - [x] Import all production packages and confirm no import errors
  - [x] Assert all required directories exist
  - [x] Print pass/fail for each check

## Dev Notes

### Critical: What Already Exists (Do Not Break)

The following files exist and have specific change requirements:

**`requirements.txt`** — EXISTS, needs complete replacement:
- Current state has outdated versions AND wrong packages (see below)
- Completely replace the file with the architecture-specified versions

**`test_setup.py`** — EXISTS, needs complete replacement:
- Current implementation only checks `slack_bolt`, `google.auth`, `dotenv`
- AC requires: all packages import + directory structure validation
- Replace entirely with a comprehensive checker

**`.gitignore`** — EXISTS and is already correct:
- `.env`, `token.json`, `logs/` are already excluded
- **Do not modify `.gitignore`** — it already satisfies the AC

**`README.md`** — EXISTS, do not touch in this story.

**`DESKTOP_SETUP.md`** — EXISTS, do not touch.

### Required: `requirements.txt` (full replacement)

```
# Slack Integration
slack-bolt==1.27.0
slack-sdk==3.40.1

# Gmail API
google-api-python-client==2.190.0
google-auth-oauthlib==1.2.4

# LLM Integration
google-generativeai==0.8.6

# HTTP & Async
aiohttp==3.11.11

# Environment Variables
python-dotenv==1.2.1

# Data Validation
pydantic==2.12.5
```

**⚠️ REMOVED from old requirements.txt (intentional):**
- `requests==2.31.0` — not used; `aiohttp` handles all HTTP (architecture mandates `aiohttp` for LM Studio calls)
- `google-auth-httplib2==0.2.0` — transitive dep of `google-api-python-client`, no need to pin directly
- `pytest`, `black`, `flake8` — moved to `requirements-dev.txt`; `flake8` replaced by `ruff`

**⚠️ PACKAGE WARNING — `google-generativeai==0.10.0`:**
Google deprecated `google-generativeai` in favor of `google-genai` (the new unified SDK) in late 2024. Before using `0.10.0`, verify this version exists on PyPI (`pip index versions google-generativeai`). If `0.10.0` is not available:
1. Use the highest available `0.x` version (likely `0.8.x`)
2. Note the version used in your completion notes
3. Do NOT switch to `google-genai` in this story — that is an architecture decision that must be made separately

### Required: `requirements-dev.txt` (new file)

```
# Testing
pytest==9.1.0

# Formatting
black==26.1.0

# Linting (replaces flake8)
ruff==0.15.1
```

### Required: `start.bat` (new file, project root)

```bat
@echo off
cd /d "%~dp0"
python -m open_fleet.main
```

Note: stdout/stderr redirection to `logs/startup.log` is a Story 5.1 requirement. This story only needs the basic stub.

### Required: `.env.example` (new file, project root)

```
# Slack Bot Token (xoxb-...) — from Slack app settings > OAuth & Permissions
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Slack App Token (xapp-...) — from Slack app settings > Basic Information > App-Level Tokens
SLACK_APP_TOKEN=xapp-your-app-token-here

# Gemini API Key — from Google AI Studio (aistudio.google.com)
GEMINI_API_KEY=your-gemini-api-key-here

# LM Studio base URL (optional, default: http://localhost:1234/v1)
LM_STUDIO_BASE_URL=http://localhost:1234/v1

# LM Studio response timeout in seconds (optional, default: 30)
LM_STUDIO_TIMEOUT_SECS=30

# Path to Gmail OAuth token file (optional, default: token.json)
GMAIL_TOKEN_PATH=token.json

# Log output directory (optional, default: logs/)
LOG_DIR=logs/
```

### Required: Stub File Content Pattern

All stub files (modules not implemented in this story) use this pattern:

```python
# src/open_fleet/config.py
"""Configuration loading and startup validation.

Implemented in Story 1.3.
"""
```

**`src/open_fleet/main.py`** is the one exception — it needs a runnable stub:

```python
"""Entry point for the open-fleet agent.

Full implementation completed across Stories 1.3, 1.4, 4.3.
"""


def main() -> None:
    print("open-fleet agent starting...")
    print("Run pip install -r requirements.txt -r requirements-dev.txt first.")
    print("Full implementation pending.")


if __name__ == "__main__":
    main()
```

### Required: Updated `test_setup.py` (full replacement)

The existing `test_setup.py` only checks 3 packages. The AC requires it to validate all packages AND the directory structure. Replace entirely:

```python
#!/usr/bin/env python3
"""
Validates that project setup is complete:
- All required packages importable
- Expected directory structure present
"""

import sys
from pathlib import Path

FAILURES: list[str] = []


def check(label: str, condition: bool) -> None:
    status = "✅" if condition else "❌"
    print(f"{status} {label}")
    if not condition:
        FAILURES.append(label)


# --- Package Imports ---
print("\n=== Package Checks ===")

try:
    import slack_bolt
    check(f"slack-bolt ({slack_bolt.__version__})", True)
except ImportError:
    check("slack-bolt", False)

try:
    import slack_sdk
    check(f"slack-sdk ({slack_sdk.__version__})", True)
except ImportError:
    check("slack-sdk", False)

try:
    import googleapiclient
    check("google-api-python-client", True)
except ImportError:
    check("google-api-python-client", False)

try:
    import google_auth_oauthlib
    check("google-auth-oauthlib", True)
except ImportError:
    check("google-auth-oauthlib", False)

try:
    import google.generativeai
    check("google-generativeai", True)
except ImportError:
    check("google-generativeai", False)

try:
    import aiohttp
    check(f"aiohttp ({aiohttp.__version__})", True)
except ImportError:
    check("aiohttp", False)

try:
    import dotenv
    check("python-dotenv", True)
except ImportError:
    check("python-dotenv", False)

try:
    import pydantic
    check(f"pydantic ({pydantic.__version__})", True)
except ImportError:
    check("pydantic", False)

# --- Directory Structure ---
print("\n=== Directory Structure Checks ===")

root = Path(__file__).parent
required_dirs = [
    "src/open_fleet",
    "src/open_fleet/adapters",
    "src/open_fleet/adapters/slack",
    "src/open_fleet/core",
    "src/open_fleet/tools",
    "src/open_fleet/llm",
    "tests",
    "tests/test_core",
    "tests/test_tools",
    "tests/test_llm",
    "logs",
    "scripts",
]

for d in required_dirs:
    path = root / d
    check(f"Directory: {d}/", path.is_dir())

# --- Key Files ---
print("\n=== Key File Checks ===")

required_files = [
    "requirements.txt",
    "requirements-dev.txt",
    ".env.example",
    "start.bat",
    "src/open_fleet/__init__.py",
    "src/open_fleet/main.py",
]

for f in required_files:
    path = root / f
    check(f"File: {f}", path.is_file())

# --- Summary ---
print(f"\n{'=' * 40}")
if FAILURES:
    print(f"❌ {len(FAILURES)} check(s) failed:")
    for f in FAILURES:
        print(f"   - {f}")
    sys.exit(1)
else:
    print("🎉 All checks passed! Project scaffold complete.")
    sys.exit(0)
```

### Project Structure Notes

**Target directory layout (complete):**
```
open-fleet/
├── src/
│   └── open_fleet/
│       ├── __init__.py
│       ├── main.py              ← runnable stub
│       ├── config.py            ← empty stub (Story 1.3)
│       ├── exceptions.py        ← empty stub (Story 1.2)
│       ├── logging_setup.py     ← empty stub (Story 1.4)
│       ├── adapters/
│       │   ├── __init__.py
│       │   └── slack/
│       │       ├── __init__.py
│       │       └── handler.py   ← empty stub (Story 4.3)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── orchestrator.py  ← empty stub (Story 4.2)
│       │   └── response.py      ← empty stub (Story 4.1)
│       ├── tools/
│       │   ├── __init__.py
│       │   └── gmail.py         ← empty stub (Story 2.1+)
│       └── llm/
│           ├── __init__.py
│           ├── router.py        ← empty stub (Story 3.4)
│           ├── lmstudio.py      ← empty stub (Story 3.2)
│           ├── gemini.py        ← empty stub (Story 3.3)
│           └── schemas.py       ← empty stub (Story 3.1)
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   │   └── __init__.py
│   ├── test_tools/
│   │   └── __init__.py
│   └── test_llm/
│       └── __init__.py
├── logs/
│   └── .gitkeep
├── scripts/
│   └── __init__.py              ← placeholder for setup_gmail_auth.py (Story 2.1)
├── requirements.txt             ← REPLACE existing
├── requirements-dev.txt         ← CREATE new
├── .env.example                 ← CREATE new
├── .env                         ← gitignored (you create this locally, not committed)
├── start.bat                    ← CREATE new
└── test_setup.py                ← REPLACE existing
```

**Alignment with architecture module boundary rules (enforced by this structure):**
- `adapters/slack/` is the ONLY directory that will import `slack_bolt` (Stories 4.x)
- `core/` will have zero imports from `adapters/`, `tools/`, or `llm/` (Stories 4.1-4.2)
- `config.py` will be imported by `main.py` only (Story 1.3)
- `exceptions.py` will be importable by any module (Story 1.2)

**Scope boundary for THIS story:**
- Create file/directory structure with stubs ONLY
- Do NOT implement any logic in any module except `test_setup.py` and `main.py` (stub)
- Do NOT run or test the agent — just verify structure and package imports via `test_setup.py`
- Implementation of `exceptions.py` → Story 1.2, `config.py` → Story 1.3, etc.

### Architecture Compliance

All requirements for this story derive from:
- [Source: _bmad-output/planning-artifacts/architecture.md#Starter Template Evaluation]
- [Source: _bmad-output/planning-artifacts/architecture.md#Dependency Version Updates]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1]
- [Source: _bmad-output/planning-artifacts/prd.md#Implementation Considerations]

Key architecture rules active in this story:
- **No external scaffold tool** — manual directory creation (NFR per architecture)
- **`src/` layout** — `src/open_fleet/` is the package root, enforcing module boundaries
- **Pinned versions** — every dependency pinned to exact version for reproducibility
- **`ruff` replaces `flake8`** — `ruff 0.15.1` in dev requirements, `flake8` removed

### References

- [Source: _bmad-output/planning-artifacts/architecture.md#Project Structure: src/ Layout with Enforced Layering]
- [Source: _bmad-output/planning-artifacts/architecture.md#Dependency Version Updates]
- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1: Project Scaffold & Dependency Configuration]
- [Source: _bmad-output/planning-artifacts/prd.md#Implementation Considerations — "Pin all dependency versions in requirements.txt"]
- [Source: _bmad-output/planning-artifacts/prd.md#Security & Configuration — FR30, NFR5, NFR6]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- **google-generativeai version**: `0.10.0` not available on PyPI; used `0.8.6` (highest available 0.x as per story fallback instructions). Note: Google has deprecated this package in favor of `google-genai` — architecture decision deferred to a future story.
- **pytest version**: `9.1.0` not available on PyPI; used `9.0.2` (highest available at time of implementation).
- **protobuf compatibility**: Python 3.14.2 breaks protobuf 4.x C extension (`google._upb._message` metaclass API removed). Added `protobuf==5.29.6` to `requirements.txt` to ensure Python 3.14 compatibility. `google-generativeai==0.8.6` is compatible with protobuf 5.29.6.
- **slack_bolt `__version__`**: `slack_bolt` module does not expose `__version__` attribute; used `importlib.metadata.version()` for version reporting in `test_setup.py`.
- **Windows stdout encoding**: Python 3.14 on Windows defaults to cp1252 which cannot encode emoji; added `io.TextIOWrapper` UTF-8 wrapper at start of `test_setup.py`.
- **ruff F401**: Import-probe pattern in `test_setup.py` correctly annotated with `# noqa: F401`; `ruff check` passes clean.

### Completion Notes List

- All 26 checks in `test_setup.py` pass (8 package checks, 12 directory checks, 6 file checks)
- `ruff check src/ tests/ test_setup.py` — all checks pass with zero warnings
- `.gitignore` already covered all required exclusions — no modifications needed
- `protobuf==5.29.6` added to `requirements.txt` as required transitive pin for Python 3.14 compatibility
- `google-generativeai==0.8.6` emits a FutureWarning about deprecation; this is expected and tracked for future architecture decision
- All stub modules created with correct docstring pattern as specified in Dev Notes
- `src/open_fleet/main.py` implemented as runnable stub per Dev Notes spec

### File List

**Created:**
- `requirements-dev.txt`
- `.env.example`
- `start.bat`
- `src/open_fleet/__init__.py`
- `src/open_fleet/main.py`
- `src/open_fleet/config.py`
- `src/open_fleet/exceptions.py`
- `src/open_fleet/logging_setup.py`
- `src/open_fleet/adapters/__init__.py`
- `src/open_fleet/adapters/slack/__init__.py`
- `src/open_fleet/adapters/slack/handler.py`
- `src/open_fleet/core/__init__.py`
- `src/open_fleet/core/orchestrator.py`
- `src/open_fleet/core/response.py`
- `src/open_fleet/tools/__init__.py`
- `src/open_fleet/tools/gmail.py`
- `src/open_fleet/llm/__init__.py`
- `src/open_fleet/llm/router.py`
- `src/open_fleet/llm/lmstudio.py`
- `src/open_fleet/llm/gemini.py`
- `src/open_fleet/llm/schemas.py`
- `tests/__init__.py`
- `tests/test_core/__init__.py`
- `tests/test_tools/__init__.py`
- `tests/test_llm/__init__.py`
- `logs/.gitkeep`
- `scripts/__init__.py`

**Modified:**
- `requirements.txt` (complete replacement — updated versions, removed outdated packages, added pydantic and protobuf pin)
- `test_setup.py` (complete replacement — comprehensive package + directory structure validator)

## Change Log

- 2026-02-28: Story 1.1 implemented — project scaffold created with full `src/open_fleet/` module structure, all dependency versions pinned, `test_setup.py` validates 26 checks. Version adjustments: `google-generativeai` pinned to `0.8.6` (0.10.0 not on PyPI), `pytest` pinned to `9.0.2` (9.1.0 not on PyPI), `protobuf==5.29.6` added for Python 3.14 compatibility.
