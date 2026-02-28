---
stepsCompleted: ['step-01-init', 'step-02-context', 'step-03-starter', 'step-04-decisions', 'step-05-patterns']
inputDocuments:
  - 'planning-artifacts/prd.md'
  - 'planning-artifacts/product-brief-open-fleet-2026-02-16.md'
workflowType: 'architecture'
project_name: 'open-fleet'
user_name: 'Jason'
date: '2026-02-21'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

33 FRs organized across 7 capability areas:

- **Command Interface (FR1-3):** Natural language Slack DM parsing with custom timeframe support.
- **Email Processing (FR4-8):** Gmail OAuth 2.0 with pagination for 150-200 email volumes, multi-part email handling, and rate limit backoff.
- **Action Item Extraction (FR9-14):** LLM-powered extraction of explicit/implicit actions, deadlines, priority tiers (urgent/this-week/no-deadline), and sentiment classification (neutral/frustrated/escalated) via batch processing.
- **LLM Routing & Reliability (FR15-19):** LM Studio (primary) → Gemini (auto-fallback), JSON schema validation, one-retry-before-fail policy, provider logging per run.
- **Response Delivery (FR20-24):** Priority-grouped Slack output with sender/timestamp/100-char context excerpts; message splitting for 4,000-char limit; structured ⚠️/❌ error messages.
- **System Health & Operations (FR25-29):** Startup config validation (fail fast), OAuth token expiry 3-day advance Slack alert, Windows Task Scheduler auto-start, 7-day structured local logs, Gemini quota monitoring.
- **Security & Configuration (FR30-33):** .env-based secrets, local token.json for OAuth, no raw email content written to disk, local-only email processing when LM Studio is active.

**Non-Functional Requirements:**

| Category | Key Constraints |
|---|---|
| Performance | <60s end-to-end; Gmail fetch ≤20s; LM Studio timeout at 30s |
| Security | Credentials in .env only; no raw email to disk; outbound-only network |
| Reliability | 95% uptime; auto-restart <60s; automatic LLM failover; no silent partial failures |
| Architecture | Zero Slack dependency in core; interface-agnostic function signatures; new adapters require no core changes |

**Scale & Complexity:**

- Primary domain: Python backend service / API orchestration
- Complexity level: Medium
- Architecture components: ~5 (Slack adapter, Agent core/orchestrator, Gmail tool, LLM router, Logging/config)
- Single user, single Gmail account, no database, stateless extraction model

### Technical Constraints & Dependencies

- **Platform:** Windows — auto-start via Task Scheduler, not systemd/launchd
- **Network model:** Outbound-only — Slack Socket Mode (persistent WebSocket), Gmail HTTPS, Gemini HTTPS, LM Studio localhost:1234. No inbound ports, no public URL, no reverse proxy.
- **LM Studio:** Local HTTP server on same machine — availability is non-deterministic; must be treated as an unreliable external dependency
- **Gmail OAuth:** Refresh token persisted in `token.json` outside source tree; access tokens expire and must be proactively monitored
- **Slack message limits:** 4,000 chars/block — responses exceeding this must be split across sequential messages
- **Data retention constraint:** Raw email bodies must not be written to disk at any point (NFR7); structured extraction output (JSON) may be logged for debugging

**LLM Output Schema (enforced at runtime):**
```json
{
  "action_items": [
    {
      "description": "string",
      "client": "string",
      "sender": "string",
      "email_timestamp": "ISO8601",
      "deadline": "ISO8601 | null",
      "priority": "urgent | this_week | no_deadline",
      "sentiment": "neutral | frustrated | escalated",
      "context": "string (max 100 chars)"
    }
  ],
  "emails_scanned": "integer",
  "timeframe": "string"
}
```

### Cross-Cutting Concerns Identified

1. **Interface isolation** — NFR15-17 mandate zero Slack imports outside the adapter layer. Affects every module boundary decision.
2. **Error handling & Slack notification** — Every external call failure (Gmail, LM Studio, Gemini) must produce a structured ⚠️/❌ Slack message. This is a consistent pattern that crosses all modules.
3. **Performance budget enforcement** — The 60s ceiling is architecturally partitioned: Gmail ≤20s, LLM ≤30s, ~10s orchestration/Slack delivery. Must be enforced at each layer.
4. **LLM provider abstraction** — Routing logic, fallback detection, schema validation, and provider logging must be centralized — not scattered across extraction calls.
5. **Secrets & configuration management** — .env parsing, startup validation, and fail-fast behavior must run before any external call is attempted.
6. **Data privacy enforcement** — No raw email content to disk at any point in any code path, regardless of LLM provider.
7. **Process lifecycle** — Auto-start, crash recovery, and OAuth token expiry proactive alerting span operational concerns that are architecturally relevant.

## Starter Template Evaluation

### Primary Technology Domain

Pure Python backend service — no web scaffold generator applicable. The "starter" decision for this project type is the directory structure layout, which directly enforces the interface-agnostic architecture mandated by NFR15-17.

### No External Scaffold Tool

The PRD explicitly mandates "no framework lock-in" and "custom Python scripts." A cookiecutter or project generator would add a dependency layer that contradicts the lean-by-design principle. Project structure is established manually as the first implementation story.

### Project Structure: `src/` Layout with Enforced Layering

Directory boundaries are the enforcement mechanism for NFR15-17. The rule "zero Slack imports outside the adapter layer" is made structurally explicit by separating `adapters/` from `core/`, `tools/`, and `llm/`.

**Recommended Structure:**

```
open-fleet/
├── src/
│   └── open_fleet/
│       ├── __init__.py
│       ├── main.py              # Entry point: starts Slack Socket Mode
│       ├── config.py            # .env loading + startup validation (fail fast)
│       ├── adapters/
│       │   └── slack/
│       │       ├── __init__.py
│       │       └── handler.py   # ONLY place slack_bolt is imported
│       ├── core/
│       │   ├── __init__.py
│       │   ├── orchestrator.py  # Coordinates extraction run end-to-end
│       │   └── response.py      # Formats output (no Slack types)
│       ├── tools/
│       │   ├── __init__.py
│       │   └── gmail.py         # Gmail OAuth + fetch + pagination
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── router.py        # LM Studio/Gemini routing + fallback logic
│       │   ├── lmstudio.py      # LM Studio HTTP provider
│       │   ├── gemini.py        # Gemini API provider
│       │   └── schemas.py       # JSON schema validation
│       └── logging_setup.py     # Structured logging configuration
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_tools/
│   └── test_llm/
├── logs/                        # 7-day rotating logs (gitignored)
├── requirements.txt             # Pinned production dependencies
├── requirements-dev.txt         # Dev tools: pytest, ruff, black
├── .env.example                 # Template committed to source control
├── .env                         # Secrets (gitignored)
├── token.json                   # Gmail OAuth refresh token (gitignored)
├── test_setup.py                # Environment validation script
└── start.bat                    # Windows Task Scheduler entry point
```

**Architectural Decisions Established by This Structure:**

- **Interface isolation enforced by directory boundary** — `adapters/slack/` is the only directory that imports `slack_bolt`. Verifiable by checking imports against directory location.
- **`core/` is interface-agnostic by definition** — `orchestrator.py` and `response.py` accept and return plain Python dicts/lists. No Slack, Gmail, or LLM-specific types cross this layer.
- **`llm/router.py` is the single routing decision point** — All LM Studio/Gemini selection, timeout detection, fallback, schema validation, and provider logging happens here.
- **`config.py` runs first** — Validates all `.env` vars before any external call is attempted. Fail-fast enforced by import order in `main.py`.
- **`tests/` mirrors `src/` module structure** — `core/`, `tools/`, and `llm/` are fully testable without a Slack connection.

### Dependency Version Updates

| Package | Pinned | Current | Action |
|---|---|---|---|
| slack-bolt | 1.18.0 | 1.27.0 | Update |
| slack-sdk | 3.27.0 | 3.40.1 | Update |
| google-api-python-client | 2.122.0 | 2.190.0 | Update |
| google-auth-oauthlib | 1.2.0 | 1.2.4 | Update |
| google-generativeai | 0.4.0 | 0.10.0 | Update |
| python-dotenv | 1.0.1 | 1.2.1 | Update |
| pytest | 8.0.2 | 9.1.0 | Move to requirements-dev.txt |
| black | 24.2.0 | 26.1.0 | Move to requirements-dev.txt |
| flake8 | 7.0.0 | — | Replace with ruff 0.15.1 |

`ruff` replaces `flake8` — covers all flake8 rules plus 800+ additional checks at 10-100x speed, pairs cleanly with `black`.

**First Implementation Story:** Create `src/open_fleet/` directory structure, update `requirements.txt`, create `requirements-dev.txt`, verify `test_setup.py` passes against updated deps.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Async execution model — affects every module's function signatures
- LLM output validation approach — affects data types flowing through core
- Error handling convention — affects every cross-layer call

**Important Decisions (Shape Architecture):**
- Logging implementation — affects observability and debugging capability
- Gmail OAuth setup flow — affects Day 1 operational experience

**Deferred Decisions (Post-MVP):**
- LLM batch size tuning — runtime concern, not architecture
- Gemini quota monitoring frequency — configurable at runtime
- Additional interface adapters (Teams, Discord) — Phase 3+

---

### Data Architecture

**No database.** Stateless extraction model — each run is independent. No raw email content persists to disk. Structured extraction output (Pydantic models serialized to JSON) may be written to local log files for debugging only.

**LLM Output Validation: Pydantic v2.12.5**

Typed models defined in `llm/schemas.py` serve as the data contract between the LLM layer and the core layer:

```python
# llm/schemas.py
from pydantic import BaseModel
from typing import Literal

class ActionItem(BaseModel):
    description: str
    client: str
    sender: str
    email_timestamp: str          # ISO8601
    deadline: str | None          # ISO8601 or null
    priority: Literal["urgent", "this_week", "no_deadline"]
    sentiment: Literal["neutral", "frustrated", "escalated"]
    context: str                  # max 100 chars

class ExtractionResult(BaseModel):
    action_items: list[ActionItem]
    emails_scanned: int
    timeframe: str
```

`ExtractionResult.model_validate(json_data)` is called on every LLM response. Pydantic `ValidationError` triggers one retry before graceful failure (FR17-18). The `ActionItem` type flows through `core/` — no raw dicts cross layer boundaries.

**Log Storage:** Python `RotatingFileHandler` — 10MB per file × 7 backups ≈ 70MB max. Files written to `logs/open_fleet.log`. Minimum 7-day retention satisfied by file rotation policy.

---

### Authentication & Security

All authentication decisions were established in the PRD. Implementation notes:

| Service | Method | Storage | Implementation |
|---|---|---|---|
| Slack bot | `SLACK_BOT_TOKEN` | `.env` | Loaded via `config.py` at startup |
| Slack socket | `SLACK_APP_TOKEN` | `.env` | Loaded via `config.py` at startup |
| Gmail | OAuth 2.0 refresh token | `token.json` | `google-auth-oauthlib` flow |
| Gemini | `GEMINI_API_KEY` | `.env` | Loaded via `config.py` at startup |
| LM Studio | None | N/A | `LM_STUDIO_BASE_URL` env var (default: `http://localhost:1234/v1`) |

**Gmail OAuth Setup Flow:** One-time browser-based consent handled by a separate `scripts/setup_gmail_auth.py` script. Run once before first launch to generate `token.json`. Not embedded in `main.py` — startup assumes `token.json` exists and validates it; if absent, `config.py` fails fast with an actionable error message pointing to the setup script.

---

### API & Communication Patterns

**Execution Model: Async (asyncio)**

Slack Bolt runs in async mode (`AsyncApp`). All I/O operations use async/await:

| Dependency | Async Strategy |
|---|---|
| LM Studio | `aiohttp` — native async HTTP to `localhost:1234/v1` |
| Gemini | `google-generativeai` — native `generate_content_async()` |
| Gmail API | `asyncio.get_event_loop().run_in_executor(None, sync_fn)` — wraps synchronous `google-api-python-client` |
| Slack delivery | `AsyncApp` — native async |

**LM Studio timeout:** `asyncio.wait_for(lmstudio_call(), timeout=30.0)` — `asyncio.TimeoutError` caught in `llm/router.py` triggers Gemini fallback.

**Error Handling Convention: Custom Exception Hierarchy**

All expected failure modes are typed exceptions defined in `src/open_fleet/exceptions.py`:

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

`core/orchestrator.py` is the single catch boundary — catches `OpenFleetError` subclasses and maps each to the appropriate ⚠️/❌ Slack message. Unexpected exceptions bubble to a top-level handler that emits a generic ❌ and logs the full traceback.

**Slack Response Formatting:** Plain markdown in Slack message strings (no Block Kit for MVP). Messages exceeding 4,000 chars split into sequential `say()` calls by `core/response.py`.

---

### Infrastructure & Deployment

**Process Management:** Single Python process. Entry point: `start.bat` → `python -m open_fleet.main`. Windows Task Scheduler: trigger at system startup, restart on failure up to 3 times with 60s delay.

**Logging Implementation: Built-in `logging` + JSON formatter**

Configured in `logging_setup.py`:

- `RotatingFileHandler` → `logs/open_fleet.log` (10MB × 7 files)
- `StreamHandler` → stdout (development visibility)
- JSON formatter emitting: `timestamp`, `level`, `module`, `provider`, `email_count`, `duration_ms`, `error`
- Logger naming pattern: `logging.getLogger("open_fleet.<module>")`

**No CI/CD for MVP.** Solo developer, local-only deployment. No external monitoring — Slack notifications serve as the operational alerting channel.

---

### Decision Impact Analysis

**Implementation Sequence (order matters):**
1. `exceptions.py` — needed by every other module
2. `config.py` — validates environment before anything runs
3. `logging_setup.py` — initialized at process start, before handlers
4. `llm/schemas.py` — Pydantic models used by both LLM providers and orchestrator
5. `tools/gmail.py` — independent of LLM layer
6. `llm/lmstudio.py` + `llm/gemini.py` — independent of each other
7. `llm/router.py` — depends on both providers + schemas
8. `core/orchestrator.py` — depends on gmail tool + llm router
9. `core/response.py` — depends on schemas (ActionItem type)
10. `adapters/slack/handler.py` — depends on orchestrator + response (Slack-only layer)
11. `main.py` — wires everything together

**Cross-Component Dependencies:**
- Async decision cascades to every module — all I/O functions are `async def`
- Pydantic `ActionItem` type is the data contract between `llm/router.py` → `core/orchestrator.py` → `core/response.py`
- `exceptions.py` is imported by `tools/`, `llm/`, and `core/` — no circular deps
- `config.py` is imported by `main.py` only — other modules receive config values as constructor arguments (avoids hidden global state)

## Implementation Patterns & Consistency Rules

**Critical Conflict Points Identified:** 8 areas where AI agents could make different choices that would produce incompatible, inconsistent, or broken code.

---

### Naming Patterns

**Python Code Naming — All Modules:**

| Construct | Convention | Example |
|---|---|---|
| Variables & functions | `snake_case` | `email_count`, `fetch_emails()` |
| Classes | `PascalCase` | `ActionItem`, `GmailAuthError` |
| Constants & env var names | `UPPER_SNAKE_CASE` | `LM_STUDIO_BASE_URL`, `MAX_RETRIES` |
| Module files | `snake_case.py` | `gmail.py`, `logging_setup.py` |
| Private helpers | `_leading_underscore` | `_parse_email_body()` |
| Test files | `test_<module>.py` | `test_gmail.py`, `test_router.py` |
| Test functions | `test_<module>_<scenario>` | `test_router_fallback_on_timeout` |

Type hints required on all public function signatures. Private helpers (`_` prefix) may omit type hints if trivially obvious.

**LLM Provider Name Strings (used in logs, routing, config):**

```python
# CORRECT — always lowercase
provider = "lmstudio"
provider = "gemini"

# WRONG — these variations are forbidden
provider = "LMStudio"
provider = "lm_studio"
provider = "Gemini"
provider = "google"
```

**Environment Variable Names:**

```
SLACK_BOT_TOKEN
SLACK_APP_TOKEN
GEMINI_API_KEY
LM_STUDIO_BASE_URL       # default: http://localhost:1234/v1
LM_STUDIO_TIMEOUT_SECS   # default: 30
GMAIL_TOKEN_PATH         # default: token.json
LOG_DIR                  # default: logs/
```

---

### Structure Patterns

**Module Responsibility Boundaries — HARD RULES:**

```
adapters/slack/   → ONLY place slack_bolt is imported. No business logic.
core/             → No imports from adapters/, tools/, or llm/.
                    Accepts/returns plain Python types + Pydantic models only.
tools/            → No imports from core/ or llm/.
llm/              → No imports from core/, tools/, or adapters/.
config.py         → Imported by main.py ONLY. Other modules receive
                    config values as constructor arguments.
exceptions.py     → Imported by any module. No other cross-layer imports.
```

**Config Injection Pattern — MANDATORY:**

```python
# CORRECT — config values injected as constructor args
class GmailClient:
    def __init__(self, token_path: str, max_results: int = 200):
        self.token_path = token_path
        self.max_results = max_results

# WRONG — module reads env vars directly
class GmailClient:
    def __init__(self):
        self.token_path = os.getenv("GMAIL_TOKEN_PATH")  # FORBIDDEN
```

`config.py` reads `.env` once at startup. All other modules receive values as constructor arguments. Every module is independently testable without an `.env` file.

**Prompt Template Location:** LLM prompt strings live in `llm/lmstudio.py` and `llm/gemini.py` respectively — each provider owns its prompt because providers may require different formatting.

---

### Format Patterns

**Log Record Schema — ALL extraction log calls must include these fields:**

```python
logger.info("extraction_complete", extra={
    "provider": "lmstudio",      # always: "lmstudio" | "gemini"
    "email_count": 187,          # int: emails processed
    "action_item_count": 14,     # int: items extracted
    "duration_ms": 23450,        # int: elapsed milliseconds
    "error": None,               # str | None: error message if applicable
})
```

`provider`, `email_count`, `duration_ms`, and `error` are **required** on every extraction run log entry.

**Datetime Handling — ALL datetimes are UTC, ISO8601 format:**

```python
# CORRECT
from datetime import datetime, timezone
ts = datetime.now(timezone.utc).isoformat()   # "2026-02-22T07:30:00+00:00"

# WRONG
ts = datetime.now().isoformat()               # naive datetime — FORBIDDEN
ts = int(time.time())                         # unix timestamp — FORBIDDEN
```

**Slack Message Format — MANDATORY prefix rules:**

```
⚠️ LM Studio unavailable — retrying with Gemini...
❌ Gmail authentication expired — run scripts/setup_gmail_auth.py to reconnect

Rules:
- ⚠️ for warnings (degraded but running), ❌ for failures (cannot complete)
- Single space after emoji, em dash (—) as separator
- Always include: what failed | why (if known) | what to do next
- No trailing punctuation
```

---

### Process Patterns

**Async Pattern — ALL I/O functions are `async def`:**

```python
# CORRECT — wrap sync Gmail SDK calls
async def fetch_emails(self, timeframe: str) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, self._sync_fetch, timeframe)

# WRONG — blocking I/O in async context
async def fetch_emails(self, timeframe: str) -> list[dict]:
    return self.service.users().messages().list(...).execute()  # BLOCKS
```

**LLM Timeout Pattern — ALWAYS use `asyncio.wait_for`:**

```python
# CORRECT
try:
    result = await asyncio.wait_for(self._call_provider(prompt), timeout=self.timeout_secs)
except asyncio.TimeoutError:
    raise LLMTimeoutError(f"LM Studio exceeded {self.timeout_secs}s timeout")
```

**Retry Pattern — ONE retry, explicit loop, no decorator:**

```python
# CORRECT — single retry, explicit and readable
for attempt in range(2):
    try:
        result = await self._call_and_validate(prompt)
        return result
    except LLMValidationError:
        if attempt == 1:
            raise
        logger.warning("LLM validation failed, retrying once")

# WRONG — decorator-based retry hides logic
@retry(tries=2)
async def call_llm(self, prompt): ...
```

**Exception Raising — ALWAYS raise specific subclass:**

```python
# CORRECT
raise GmailAuthError("OAuth token expired or revoked")
raise LLMTimeoutError(f"Exceeded {timeout}s threshold")

# WRONG — base class loses error type information
raise OpenFleetError("Something went wrong")
```

**LLM Prompt Structure — TWO-MESSAGE format (system + user):**

```python
# CORRECT — both providers use this structure
messages = [
    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
    {"role": "user",   "content": f"Emails to analyze:\n\n{email_batch_text}"},
]

# WRONG — single concatenated prompt string
prompt = f"{SYSTEM_PROMPT}\n\nEmails:\n{emails}"
```

---

### Enforcement Guidelines

**All AI Agents MUST:**

- Import `slack_bolt` only inside `adapters/slack/`
- Use `async def` for every function that calls I/O (Gmail, LLM, Slack)
- Wrap sync `google-api-python-client` calls with `run_in_executor`
- Raise specific exception subclasses — never the base `OpenFleetError`
- Inject config values as constructor arguments — never read `.env` in modules
- Use `"lmstudio"` and `"gemini"` (lowercase) as provider name constants
- Log extraction runs with all 5 required fields: `provider`, `email_count`, `action_item_count`, `duration_ms`, `error`
- Format all datetimes as UTC ISO8601 strings
- Prefix Slack warnings with `⚠️` and failures with `❌`
- Use two-message (system + user) prompt structure for both LLM providers

**Pattern Verification:**
- `ruff` enforces import ordering and naming conventions
- Import boundary violations caught by checking `import slack_bolt` only appears in `adapters/slack/`
- Test suite runs without any `.env` file — if tests require `.env`, config injection pattern has been violated
