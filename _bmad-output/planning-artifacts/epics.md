---
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
workflowStatus: complete
completedAt: '2026-02-28'
inputDocuments:
  - 'planning-artifacts/prd.md'
  - 'planning-artifacts/architecture.md'
workflowType: 'epics-and-stories'
project_name: 'open-fleet'
user_name: 'Jason'
date: '2026-02-28'
---

# open-fleet - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for open-fleet, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: User can trigger email extraction using natural language Slack messages (e.g., `extract today's emails`, `what's urgent today?`)
FR2: User can specify a custom timeframe for email extraction (e.g., `check emails since yesterday 5pm`)
FR3: User can receive all agent responses directly in a Slack DM
FR4: Agent can authenticate with Gmail using OAuth 2.0 and maintain a persistent refresh token
FR5: Agent can fetch emails from the user's Gmail inbox for a specified timeframe (default: last 24 hours)
FR6: Agent can paginate Gmail results to process batches of 150-200+ emails in a single extraction run
FR7: Agent can extract subject, sender, timestamp, and body text from multi-part emails (HTML and plain text)
FR8: Agent can handle Gmail API rate limit errors by retrying with exponential backoff and notifying the user of any resulting delay
FR9: Agent can identify explicit action requests within email content (requests, approvals, deliverables)
FR10: Agent can identify implicit action items (questions requiring response, pending decisions)
FR11: Agent can extract deadlines from email content, both explicit ("by EOD Friday") and implied ("urgent", "ASAP")
FR12: Agent can classify each action item by priority tier (urgent, this_week, no_deadline)
FR13: Agent can detect and classify email sender sentiment (neutral, frustrated, escalated)
FR14: Agent can batch-process multiple emails in a single LLM inference call
FR15: Agent can route extraction requests to LM Studio as the primary LLM provider
FR16: Agent can automatically fall back to Gemini when LM Studio is unavailable or exceeds the response timeout
FR17: Agent can validate LLM output against a required JSON schema (Pydantic) before use
FR18: Agent can retry a failed or invalid LLM response once before escalating to graceful failure
FR19: Agent can log which LLM provider handled each extraction run
FR20: Agent can deliver a formatted Slack response with action items grouped by priority tier (🔴 Urgent → 💬 Needs Response → ⏰ Approaching deadline → 🟡 This week → 🟢 No deadline)
FR21: Agent can include sender, timestamp, and a context excerpt (max 100 characters) for each action item
FR22: Agent can report the total email count and timeframe scanned in the response header
FR23: Agent can split responses that exceed Slack's 4,000-character message size limit across multiple sequential messages
FR24: Agent can deliver structured error notifications using consistent ⚠️/❌ formatting with actionable next steps
FR25: Agent can validate all required configuration values at startup and halt with specific, actionable error messages if any are missing or invalid
FR26: Agent can detect Gmail OAuth token expiry and notify the user via Slack at least 3 days before the token expires
FR27: Agent can start automatically on system boot without manual terminal intervention
FR28: Agent can write structured logs for each extraction run (provider used, email count, duration, errors)
FR29: Agent can monitor Gemini free tier quota usage and alert the user when approaching the daily limit
FR30: User can configure all credentials and service settings via a `.env` file without modifying source code
FR31: Agent can store Gmail OAuth refresh tokens in a local file, outside of source code and version control
FR32: Agent can process email content through the local LLM provider without transmitting data externally when LM Studio is active
FR33: Agent can discard raw email body content after each extraction run without writing it to persistent storage

### NonFunctional Requirements

NFR1: End-to-end extraction response time (Slack command received → Slack response delivered) must not exceed 60 seconds for batches of up to 200 emails under normal operating conditions.
NFR2: LM Studio inference requests must complete within 30 seconds; requests exceeding this threshold trigger the Gemini fallback path.
NFR3: Gmail fetch and parse operations must complete within 20 seconds to preserve the overall 60-second response budget.
NFR4: Response time must not exceed the 60-second ceiling regardless of batch size — 200 emails must complete within the same budget as 50 emails.
NFR5: All credentials (Slack tokens, Gmail OAuth tokens, Gemini API key) must be stored in `.env` and excluded from version control via `.gitignore`. No credentials may appear in source code.
NFR6: Gmail OAuth refresh tokens must be stored in a local `token.json` file outside the source tree and excluded from version control.
NFR7: Raw email body content must not be written to disk at any point during or after an extraction run.
NFR8: When LM Studio is active, email content must not leave the local machine. When Gemini is active, email content must be transmitted only over HTTPS to Google's API endpoints.
NFR9: The agent must not expose any inbound network ports. All external communication is outbound-only.
NFR10: The agent must achieve 95%+ availability during working hours (Monday–Friday, 7am–6pm local time).
NFR11: The agent process must restart automatically after a crash within 60 seconds, without manual intervention, via the OS-level task scheduler.
NFR12: LLM provider failover from LM Studio to Gemini must be automatic and require no user action. The user must be notified via Slack when failover occurs.
NFR13: A failed extraction must never deliver a partial or malformed response. The outcome is either a complete valid response or a clearly formatted error message — no silent partial results.
NFR14: The agent must maintain 7 days of structured local logs sufficient to diagnose any failure without reproduction.
NFR15: The Slack Bolt framework must not be imported or referenced in any module outside the interface adapter layer (`adapters/slack/`).
NFR16: All core extraction functions must accept and return interface-agnostic data types — plain Python types and Pydantic models only, no Slack-specific objects.
NFR17: Adding a new interface adapter (e.g., Teams, Discord) must require no modifications to any existing core, LLM, or tool module — only creation of a new adapter module.

### Additional Requirements

- **Project Structure First (Story 1.1):** Architecture specifies no external scaffold tool. The `src/open_fleet/` directory layout is established manually as the first implementation story, enforcing the interface-isolation architecture required by NFR15-17.
- **Async execution model throughout:** All I/O functions must be `async def` using `asyncio`. Synchronous `google-api-python-client` calls must be wrapped with `loop.run_in_executor(None, ...)`. This cascades to every module.
- **Custom exception hierarchy (`exceptions.py`) must be created first:** `OpenFleetError` base → `GmailError`, `LLMError`, `ConfigError` subclasses. Required by all other modules; must exist before any other module is implemented.
- **Pydantic v2 data contract:** `ActionItem` and `ExtractionResult` Pydantic models in `llm/schemas.py` are the typed boundary between the LLM layer and core layer. `ExtractionResult.model_validate()` called on every LLM response.
- **Config injection pattern (mandatory):** `config.py` reads `.env` once at startup. All other modules receive config values as constructor arguments — never read `.env` directly. Required for test isolation.
- **Gmail OAuth setup script:** One-time `scripts/setup_gmail_auth.py` — separate from main entry point. Run once before first launch to generate `token.json`. `config.py` fails fast if `token.json` absent.
- **Windows Task Scheduler process management:** `start.bat` → `python -m open_fleet.main`. Configured to trigger at system startup; restart on failure up to 3 times with 60-second delay.
- **Structured JSON logging:** `RotatingFileHandler` (10MB × 7 files) in `logs/open_fleet.log`. JSON formatter. Every extraction run log entry must include: `provider`, `email_count`, `action_item_count`, `duration_ms`, `error`.
- **Implementation sequence is ordered (architecture constraint):** `exceptions.py` → `config.py` → `logging_setup.py` → `llm/schemas.py` → `tools/gmail.py` → `llm/lmstudio.py` + `llm/gemini.py` → `llm/router.py` → `core/orchestrator.py` → `core/response.py` → `adapters/slack/handler.py` → `main.py`
- **Module boundary hard rules:** `adapters/slack/` is the ONLY place `slack_bolt` is imported. `core/` has no imports from `adapters/`, `tools/`, or `llm/`. `config.py` imported by `main.py` only. `exceptions.py` importable by any module.
- **Dependency version updates required:** Update pinned versions in `requirements.txt`; create `requirements-dev.txt` with pytest, black, ruff. ruff replaces flake8.
- **No CI/CD for MVP:** Solo developer, local-only deployment. Slack notifications serve as the operational alerting channel.
- **LLM prompt structure:** Both providers use two-message format (system + user). Provider name strings: always lowercase `"lmstudio"` and `"gemini"`.
- **All datetimes UTC ISO8601:** `datetime.now(timezone.utc).isoformat()` — naive datetimes and unix timestamps are forbidden.
- **Slack message format rules:** `⚠️` for warnings (degraded but running), `❌` for failures (cannot complete). Single space after emoji, em dash (—) as separator. Always include: what failed | why | what to do next.

### FR Coverage Map

FR1: Epic 4 — Slack command: trigger extraction via natural language message
FR2: Epic 4 — Slack command: custom timeframe specification
FR3: Epic 4 — Slack command: all responses delivered via Slack DM
FR4: Epic 2 — Gmail OAuth 2.0 authentication with persistent refresh token
FR5: Epic 2 — Gmail inbox fetch for specified timeframe
FR6: Epic 2 — Gmail pagination for 150-200+ email batches
FR7: Epic 2 — Multi-part email parsing (subject, sender, timestamp, body)
FR8: Epic 2 — Gmail rate limit handling with exponential backoff + user notification
FR9: Epic 3 — Identify explicit action requests in email content
FR10: Epic 3 — Identify implicit action items (questions, pending decisions)
FR11: Epic 3 — Extract deadlines (explicit and implied)
FR12: Epic 3 — Classify action items by priority tier (urgent/this_week/no_deadline)
FR13: Epic 3 — Detect and classify sender sentiment (neutral/frustrated/escalated)
FR14: Epic 3 — Batch-process multiple emails in a single LLM inference call
FR15: Epic 3 — Route extraction to LM Studio as primary LLM provider
FR16: Epic 3 — Auto-fallback to Gemini when LM Studio unavailable or times out
FR17: Epic 3 — Validate LLM output against Pydantic JSON schema before use
FR18: Epic 3 — Retry failed/invalid LLM response once before graceful failure
FR19: Epic 3 — Log which LLM provider handled each extraction run
FR20: Epic 4 — Formatted Slack response grouped by priority tier (🔴→💬→⏰→🟡→🟢)
FR21: Epic 4 — Include sender, timestamp, 100-char context excerpt per action item
FR22: Epic 4 — Report total email count and timeframe in response header
FR23: Epic 4 — Split responses exceeding Slack's 4,000-char limit across sequential messages
FR24: Epic 4 — Structured error notifications using ⚠️/❌ formatting with actionable next steps
FR25: Epic 1 — Startup config validation: fail fast with specific actionable error messages
FR26: Epic 5 — Detect Gmail OAuth token expiry; Slack alert 3 days in advance
FR27: Epic 5 — Auto-start on system boot without manual intervention
FR28: Epic 5 — Structured logs per extraction run (provider, email count, duration, errors)
FR29: Epic 5 — Monitor Gemini free tier quota; Slack alert when approaching daily limit
FR30: Epic 1 — All credentials and settings configurable via .env file
FR31: Epic 1 — Gmail OAuth refresh tokens stored in local token.json outside source control
FR32: Epic 3 — Email content not transmitted externally when LM Studio is active provider
FR33: Epic 2 — Raw email body content discarded after each extraction run (not written to disk)

## Epic List

### Epic 1: Project Foundation & Architecture Scaffold
Jason has a properly structured project with enforced module boundaries, all dependencies pinned, configuration management with fail-fast startup validation, a typed exception hierarchy, and structured logging — the complete architectural skeleton that all feature development builds upon.
**FRs covered:** FR25, FR30, FR31
**NFRs addressed:** NFR5, NFR6, NFR9, NFR15, NFR16, NFR17

### Epic 2: Gmail Email Retrieval
Jason can connect to his Gmail inbox, authenticate via OAuth 2.0, and retrieve/parse up to 200+ emails for any requested timeframe — the data pipeline that feeds the triage engine, including rate limit handling and guaranteed no-disk-write of raw email content.
**FRs covered:** FR4, FR5, FR6, FR7, FR8, FR33
**NFRs addressed:** NFR3, NFR6, NFR7, NFR8 (local-only aspect)

### Epic 3: AI Action Item Extraction Engine
Emails are intelligently analyzed to surface explicit and implicit action items with priority tiers, deadlines, and sentiment — using LM Studio locally with automatic Gemini fallback, Pydantic-validated JSON output, and per-run provider logging.
**FRs covered:** FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR32
**NFRs addressed:** NFR2, NFR8 (Gemini HTTPS), NFR12, NFR13

### Epic 4: Slack Command Interface & Triage Reports
The complete end-to-end triage workflow is live: Jason types a natural language command in Slack DM and receives a formatted, priority-grouped action item report in under 60 seconds — the full user experience working for the first time.
**FRs covered:** FR1, FR2, FR3, FR20, FR21, FR22, FR23, FR24
**NFRs addressed:** NFR1, NFR4, NFR15, NFR16, NFR17

### Epic 5: Operational Reliability & Proactive Monitoring
The agent runs every working day without babysitting — auto-starts on boot, recovers from crashes automatically, proactively alerts Jason about Gmail token expiry and Gemini quota limits, and maintains 7 days of structured diagnostic logs.
**FRs covered:** FR26, FR27, FR28, FR29
**NFRs addressed:** NFR10, NFR11, NFR14

---

## Epic 1: Project Foundation & Architecture Scaffold

Jason has a properly structured project with enforced module boundaries, all dependencies pinned, configuration management with fail-fast startup validation, a typed exception hierarchy, and structured logging — the complete architectural skeleton that all feature development builds upon.

### Story 1.1: Project Scaffold & Dependency Configuration

As a developer,
I want a properly structured `src/open_fleet/` project with all module directories, pinned dependencies, and version-control exclusions in place,
So that the interface-isolation architecture is enforced by directory boundaries from day one and every dependency version is deterministic.

**Acceptance Criteria:**

**Given** a fresh clone of the repository
**When** the developer runs `pip install -r requirements.txt -r requirements-dev.txt` and then `python test_setup.py`
**Then** all required packages import successfully with no errors
**And** the directory structure exists: `src/open_fleet/`, `adapters/slack/`, `core/`, `tools/`, `llm/`, `tests/test_core/`, `tests/test_tools/`, `tests/test_llm/`, `logs/`
**And** `requirements.txt` contains pinned production dependencies: `slack-bolt==1.27.0`, `slack-sdk==3.40.1`, `google-api-python-client==2.190.0`, `google-auth-oauthlib==1.2.4`, `google-generativeai==0.10.0`, `python-dotenv==1.2.1`, `pydantic==2.12.5`, `aiohttp`
**And** `requirements-dev.txt` contains: `pytest==9.1.0`, `black==26.1.0`, `ruff==0.15.1`
**And** `.env.example` lists all required environment variables with placeholder values and inline comments
**And** `.gitignore` excludes `.env`, `token.json`, and `logs/`
**And** `start.bat` exists as a stub entry point (`python -m open_fleet.main`)

### Story 1.2: Typed Exception Hierarchy

As a developer,
I want a typed exception hierarchy defined in `exceptions.py` before any other module is implemented,
So that every error condition across the codebase has a named, specific type that can be caught with precision.

**Acceptance Criteria:**

**Given** `src/open_fleet/exceptions.py` is imported in a test
**When** each exception class is inspected
**Then** `OpenFleetError` is the base class for all project exceptions, inheriting from `Exception`
**And** `GmailError(OpenFleetError)` is the base for all Gmail failures, with subclasses `GmailAuthError`, `GmailRateLimitError`, `GmailFetchError`
**And** `LLMError(OpenFleetError)` is the base for all LLM failures, with subclasses `LLMTimeoutError`, `LLMValidationError`, `LLMProviderError`
**And** `ConfigError(OpenFleetError)` covers missing or invalid configuration values
**And** catching `OpenFleetError` catches all of the above subclasses
**And** no other module in the project defines custom exception classes

### Story 1.3: Configuration Loading & Startup Validation

As Jason (operator),
I want all configuration loaded from `.env` at startup with immediate, specific error messages if anything is missing or invalid,
So that I can fix misconfiguration in seconds rather than debugging why the agent silently failed.

**Acceptance Criteria:**

**Given** the agent is started with a missing required env var (e.g., `SLACK_BOT_TOKEN` absent)
**When** `config.py` runs its validation
**Then** a `ConfigError` is raised immediately, before any external connection is attempted
**And** the error message names the exact missing variable and its expected format

**Given** all required env vars are present and `token.json` exists at the configured path
**When** `config.py` runs its validation
**Then** a `Config` object is returned with all values accessible as typed attributes
**And** optional vars (`LM_STUDIO_BASE_URL`, `GMAIL_TOKEN_PATH`, `LOG_DIR`, `LM_STUDIO_TIMEOUT_SECS`) use documented defaults when absent from `.env`

**Given** `token.json` does not exist at the configured path
**When** `config.py` runs its validation
**Then** a `ConfigError` is raised with a message directing the user to run `scripts/setup_gmail_auth.py`

**Given** `config.py` is imported into a test without an `.env` file present
**When** config values are passed as constructor arguments to other modules
**Then** all other modules operate correctly without reading any env vars directly (config injection pattern enforced)

### Story 1.4: Structured Logging Infrastructure

As a developer,
I want structured JSON logging with a rotating file handler initialized at process start,
So that every run produces queryable diagnostic logs retained for 7 days without manual cleanup.

**Acceptance Criteria:**

**Given** `logging_setup.py` is called in `main.py` before any other module initializes
**When** any module calls `logging.getLogger("open_fleet.<module>")`
**Then** log records are written to `logs/open_fleet.log` in JSON format with fields: `timestamp`, `level`, `module`
**And** the same log records are echoed to stdout via `StreamHandler` for development visibility

**Given** `logs/open_fleet.log` reaches 10MB
**When** the next log entry is written
**Then** the log file rotates to a `.log.1` backup and a fresh `open_fleet.log` is created
**And** up to 7 backup files are retained (≈70MB maximum total log storage)

**Given** the test suite runs without a `.env` file
**When** `logging_setup.py` is imported in tests
**Then** test log output goes to stdout only and does not write to `logs/open_fleet.log`

---

## Epic 2: Gmail Email Retrieval

Jason can connect to his Gmail inbox, authenticate via OAuth 2.0, and retrieve/parse up to 200+ emails for any requested timeframe — the raw data pipeline that feeds the triage engine, including rate limit handling and guaranteed no-disk-write of raw email content.

### Story 2.1: Gmail OAuth Authentication Setup

As Jason,
I want a one-time setup script that guides me through Gmail OAuth 2.0 authentication and stores a refresh token locally,
So that the agent has persistent, secure Gmail access before its first run without any credentials appearing in source code.

**Acceptance Criteria:**

**Given** `scripts/setup_gmail_auth.py` is run for the first time
**When** the script executes
**Then** a browser window opens to the Google OAuth consent screen for the configured Google Cloud project
**And** after Jason grants consent, a `token.json` file is written to the path specified by `GMAIL_TOKEN_PATH`
**And** `token.json` contains a valid refresh token that survives process restarts
**And** `token.json` is excluded from version control via `.gitignore`

**Given** `token.json` already exists when the script is run again
**When** the script executes
**Then** the existing token is refreshed if expired, or the script confirms the token is still valid without opening a browser

**Given** `GmailClient` is initialized in `tools/gmail.py`
**When** it loads credentials from `token.json`
**Then** it uses `google-auth-oauthlib` to refresh the access token automatically when expired
**And** raises `GmailAuthError` if the token file is missing, corrupt, or the refresh fails

### Story 2.2: Gmail Email Fetch & Pagination

As Jason,
I want the agent to reliably fetch up to 200+ emails from my Gmail inbox for any specified timeframe,
So that no email is missed when I request a triage — regardless of inbox volume.

**Acceptance Criteria:**

**Given** a timeframe string (e.g., `"last 24 hours"`, `"since yesterday 5pm"`) is passed to `GmailClient.fetch_emails()`
**When** the method executes
**Then** it queries the Gmail API with an appropriate `after:` date filter derived from the timeframe
**And** it paginates through all results using `nextPageToken` until all matching messages are retrieved
**And** it returns a list of raw message dicts for all emails in the timeframe, with no artificial cap below the actual inbox count

**Given** the inbox contains 200 emails matching the timeframe
**When** `fetch_emails()` executes
**Then** all 200 message IDs are retrieved across as many paginated requests as needed
**And** the operation completes within 20 seconds (NFR3)

**Given** `fetch_emails()` is called from an async context
**When** the synchronous `google-api-python-client` calls execute
**Then** they are wrapped with `asyncio.get_event_loop().run_in_executor(None, ...)` so the event loop is not blocked

### Story 2.3: Email Content Parsing

As Jason,
I want subject, sender, timestamp, and clean body text reliably extracted from every email format my inbox contains,
So that the LLM extraction engine receives usable, complete content for every message.

**Acceptance Criteria:**

**Given** a plain-text email message
**When** `GmailClient.parse_email()` processes it
**Then** it returns a dict with `subject`, `sender` (From: header display name + address), `timestamp` (UTC ISO8601), and `body` (plain text content)

**Given** a multi-part email with both `text/plain` and `text/html` parts
**When** `parse_email()` processes it
**Then** it returns the `text/plain` part as `body`, ignoring HTML
**And** if no `text/plain` part exists, it strips HTML tags from `text/html` and returns the plain text

**Given** the parsed email dict is returned from `parse_email()`
**When** the extraction run completes
**Then** the raw `body` string is not written to any file on disk at any point during or after processing (NFR7, FR33)
**And** only the structured extraction result (Pydantic model) may be logged, never the raw email body

### Story 2.4: Gmail Rate Limit Handling

As Jason,
I want the agent to retry Gmail API calls with exponential backoff when rate limits are hit, and notify me via Slack if the delay is significant,
So that temporary quota errors never silently break my morning triage.

**Acceptance Criteria:**

**Given** the Gmail API returns an HTTP 429 response during `fetch_emails()`
**When** the error is caught
**Then** the request is retried after 1 second, then 2 seconds, then 4 seconds (exponential backoff)
**And** a `⚠️ Gmail API rate limit hit — extraction will retry in {n} seconds` message is sent to Jason's Slack DM before each retry delay

**Given** all retry attempts are exhausted without a successful response
**When** the final retry fails
**Then** a `GmailRateLimitError` is raised with the number of attempts made
**And** the orchestrator catches this and sends `❌ Gmail API rate limit — extraction could not complete after retries` to Slack

**Given** the Gmail API returns a non-429 error (e.g., network timeout, 500)
**When** the error is caught in `tools/gmail.py`
**Then** a `GmailFetchError` is raised with the HTTP status and response detail
**And** no retry is attempted for non-rate-limit errors

---

## Epic 3: AI Action Item Extraction Engine

Emails are intelligently analyzed to surface explicit and implicit action items with priority tiers, deadlines, and sentiment — using LM Studio locally with automatic Gemini fallback, Pydantic-validated JSON output, and per-run provider logging.

### Story 3.1: Pydantic Data Models & Extraction Schema

As a developer,
I want typed Pydantic v2 models defining the exact data contract between the LLM layer and the core layer,
So that LLM responses are validated against a strict schema and malformed data can never reach the response formatter.

**Acceptance Criteria:**

**Given** `llm/schemas.py` is imported
**When** the models are inspected
**Then** `ActionItem` is a Pydantic `BaseModel` with fields: `description: str`, `client: str`, `sender: str`, `email_timestamp: str`, `deadline: str | None`, `priority: Literal["urgent", "this_week", "no_deadline"]`, `sentiment: Literal["neutral", "frustrated", "escalated"]`, `context: str`
**And** `ExtractionResult` is a Pydantic `BaseModel` with fields: `action_items: list[ActionItem]`, `emails_scanned: int`, `timeframe: str`

**Given** a valid JSON dict matching the schema
**When** `ExtractionResult.model_validate(json_dict)` is called
**Then** it returns a typed `ExtractionResult` instance with no errors

**Given** a JSON dict with a missing required field or an invalid `priority` value
**When** `ExtractionResult.model_validate(json_dict)` is called
**Then** it raises a Pydantic `ValidationError` with a descriptive message identifying the invalid field
**And** no partial or partially-valid object is returned

**Given** `llm/schemas.py` is imported in `core/` modules
**When** the import is checked
**Then** `llm/schemas.py` contains no imports from `adapters/`, `tools/`, or `core/` (no circular dependencies)

### Story 3.2: LM Studio Provider Integration

As Jason,
I want the agent to send batched email content to my local LM Studio instance using a structured prompt and receive a validated JSON extraction response,
So that local inference is the primary zero-cost triage path with no data leaving my machine.

**Acceptance Criteria:**

**Given** LM Studio is running and reachable at `LM_STUDIO_BASE_URL`
**When** `LMStudioProvider.extract(email_batch: list[dict]) -> ExtractionResult` is called
**Then** it constructs a two-message prompt (`{"role": "system", ...}` + `{"role": "user", ...}`) with the extraction system prompt and batched email content
**And** it sends the request via `aiohttp` to `{LM_STUDIO_BASE_URL}/chat/completions`
**And** it returns a validated `ExtractionResult` on success

**Given** the LM Studio request does not complete within `LM_STUDIO_TIMEOUT_SECS` (default: 30)
**When** `asyncio.wait_for()` triggers
**Then** an `LLMTimeoutError` is raised with the elapsed time and configured timeout value

**Given** LM Studio is unreachable (connection refused)
**When** the `aiohttp` request fails
**Then** an `LLMProviderError` is raised immediately without waiting for timeout

**Given** LM Studio returns a response with email content
**When** the request completes
**Then** no email body content is written to disk at any point during the call (FR32)
**And** the provider name string logged is always `"lmstudio"` (lowercase, no variations)

### Story 3.3: Gemini Fallback Provider Integration

As Jason,
I want the agent to use Gemini as a cloud fallback when LM Studio is unavailable,
So that a triage run is never blocked by local model downtime.

**Acceptance Criteria:**

**Given** a valid `GEMINI_API_KEY` is configured
**When** `GeminiProvider.extract(email_batch: list[dict]) -> ExtractionResult` is called
**Then** it constructs the same two-message prompt structure used by the LM Studio provider
**And** it calls `google-generativeai`'s `generate_content_async()` with the prompt
**And** it returns a validated `ExtractionResult` on success

**Given** Gemini returns a response
**When** email content was included in the prompt
**Then** the content was transmitted only over HTTPS to Google's API endpoint (NFR8)
**And** the provider name string logged is always `"gemini"` (lowercase, no variations)

**Given** `GeminiProvider` is tested in isolation
**When** it is instantiated with a `GEMINI_API_KEY` constructor argument
**Then** it does not read any environment variables directly (config injection pattern)

### Story 3.4: LLM Router with Automatic Fallback & Retry

As Jason,
I want LLM provider selection, timeout detection, schema validation, and one-retry-before-fail handled automatically,
So that the agent always delivers either a valid extraction result or a clear error — never garbled or partial output.

**Acceptance Criteria:**

**Given** LM Studio is available
**When** `LLMRouter.run_extraction(email_batch) -> ExtractionResult` is called
**Then** it routes to `LMStudioProvider` first
**And** on success, returns the validated `ExtractionResult` and logs `provider: "lmstudio"`

**Given** LM Studio raises `LLMTimeoutError` or `LLMProviderError`
**When** the router catches the error
**Then** it automatically falls back to `GeminiProvider` without user intervention (NFR12)
**And** logs `provider: "gemini"` for the run

**Given** the active provider returns a response that fails `ExtractionResult.model_validate()`
**When** `LLMValidationError` is raised
**Then** the router retries the same provider exactly once with the same prompt
**And** if the retry also fails validation, raises `LLMValidationError` to the orchestrator (NFR13)

**Given** both providers fail (LM Studio timeout + Gemini validation error after retry)
**When** the router exhausts all attempts
**Then** it raises the final `LLMError` subclass with full context
**And** no partial or unvalidated data is returned under any failure path (NFR13)

**Given** any extraction run completes (success or failure)
**When** the run is logged
**Then** the log entry includes all 5 required fields: `provider`, `email_count`, `action_item_count`, `duration_ms`, `error` (FR19)

### Story 3.5: Action Item Extraction Prompt & Accuracy Validation

As Jason,
I want the LLM prompted precisely enough to reliably identify action items, deadlines, priority, and sentiment from real email batches at 85%+ accuracy,
So that I can trust the output enough to stop manually reading 200 emails every morning.

**Acceptance Criteria:**

**Given** an email containing an explicit request ("Please review the proposal by EOD Friday")
**When** the extraction prompt is sent to either provider
**Then** the response includes an `ActionItem` with `priority: "urgent"` or `priority: "this_week"` and a `deadline` field matching the specified date (FR9, FR11, FR12)

**Given** an email containing an implicit ask ("Just wanted to check in on the status of...")
**When** the extraction prompt processes it
**Then** the response includes an `ActionItem` with `description` capturing the implicit follow-up needed (FR10)

**Given** an email from a sender using frustrated language ("This is the third time we've had to push this back")
**When** the extraction prompt processes it
**Then** the response includes an `ActionItem` with `sentiment: "escalated"` or `sentiment: "frustrated"` (FR13)

**Given** a batch of emails is sent for extraction
**When** the LLM response is received
**Then** the `emails_scanned` field in `ExtractionResult` matches the count of emails sent in the batch (FR14)
**And** the `context` field for each `ActionItem` is truncated to a maximum of 100 characters

**Given** a manual spot-check of 10 real emails from Jason's inbox
**When** extraction results are compared against manually identified action items
**Then** at least 85% of real action items are surfaced (success threshold per PRD)

---

## Epic 4: Slack Command Interface & Triage Reports

The complete end-to-end triage workflow is live: Jason types a natural language command in Slack DM and receives a formatted, priority-grouped action item report in under 60 seconds — the full user experience working for the first time.

### Story 4.1: Response Formatter

As Jason,
I want extracted action items formatted into a prioritized, emoji-coded Slack report with sender, timestamp, and a context excerpt per item,
So that I can scan my full day's action items in under two minutes without opening Gmail.

**Acceptance Criteria:**

**Given** a valid `ExtractionResult` with action items of mixed priorities
**When** `ResponseFormatter.format(result: ExtractionResult) -> list[str]` is called
**Then** it returns one or more strings grouping action items under priority headers in order: `🔴 Urgent` → `💬 Needs Response` → `⏰ Approaching Deadline` → `🟡 This Week` → `🟢 No Deadline`
**And** groups with no items are omitted from the output

**Given** an `ActionItem` is rendered
**When** it appears in the formatted output
**Then** it includes: sender name, UTC timestamp formatted as human-readable local date/time, priority label, and `context` truncated to 100 characters
**And** a sentiment indicator is shown for `frustrated` or `escalated` items (e.g., `💬 frustrated`)

**Given** a response header is rendered
**When** it appears at the top of the first message
**Then** it includes the total `emails_scanned` count and the `timeframe` string from `ExtractionResult` (FR22)

**Given** the formatted output exceeds 4,000 characters
**When** `format()` returns the result
**Then** it returns a `list[str]` with content split across multiple strings, each under 4,000 characters, with no action item cut mid-entry (FR23)

**Given** `core/response.py` is inspected
**When** its imports are checked
**Then** it contains zero imports from `slack_bolt`, `slack_sdk`, or any Slack-specific module (NFR15, NFR16)

### Story 4.2: Extraction Orchestrator

As Jason,
I want the end-to-end triage workflow coordinated in a single orchestrator that handles all failure modes uniformly,
So that every run delivers either a complete formatted report or a precise ⚠️/❌ error message — never silence, never a crash.

**Acceptance Criteria:**

**Given** a valid timeframe string is passed to `Orchestrator.run(timeframe: str) -> list[str]`
**When** it executes successfully
**Then** it calls `GmailClient.fetch_emails()` → `GmailClient.parse_email()` for each message → `LLMRouter.run_extraction()` → `ResponseFormatter.format()`
**And** returns the formatted `list[str]` ready for Slack delivery
**And** the full pipeline completes within 60 seconds for up to 200 emails (NFR1, NFR4)

**Given** `GmailAuthError` is raised during the Gmail fetch
**When** the orchestrator catches it
**Then** it returns `["❌ Gmail authentication expired — run scripts/setup_gmail_auth.py to reconnect"]`

**Given** `GmailRateLimitError` is raised
**When** the orchestrator catches it
**Then** it returns `["❌ Gmail API rate limit — extraction could not complete after retries"]`

**Given** `LLMTimeoutError` is raised by the router (both providers exhausted)
**When** the orchestrator catches it
**Then** it returns `["❌ LLM extraction failed — both LM Studio and Gemini unavailable"]`

**Given** an unexpected exception (not an `OpenFleetError` subclass) is raised anywhere in the pipeline
**When** the orchestrator catches it
**Then** it returns `["❌ Unexpected error — check logs for details"]`
**And** logs the full exception traceback at `ERROR` level

**Given** `core/orchestrator.py` is inspected
**When** its imports are checked
**Then** it contains zero imports from `adapters/`, and zero imports of `slack_bolt` or `slack_sdk` (NFR15, NFR16)

### Story 4.3: Slack Command Handler & End-to-End Wiring

As Jason,
I want to type a natural language command in my Slack DM and receive the full triage report back in the same DM within 60 seconds,
So that Slack is the only interface I ever need to interact with the agent.

**Acceptance Criteria:**

**Given** the agent is running and connected via Slack Socket Mode
**When** Jason sends `extract today's emails` in a DM to the bot
**Then** the handler parses the command, calls `Orchestrator.run("last 24 hours")`, and delivers all response strings sequentially via `say()` in the same DM (FR1, FR3)

**Given** Jason sends `check emails since yesterday 5pm`
**When** the handler parses the command
**Then** it extracts the timeframe `"since yesterday 5pm"` and passes it to the orchestrator (FR2)

**Given** Jason sends `what's urgent today?`
**When** the handler parses the command
**Then** it maps this to a `"last 24 hours"` timeframe and calls the orchestrator

**Given** the orchestrator returns multiple strings (split response)
**When** the handler delivers them
**Then** each string is sent as a separate sequential `say()` call in the correct order (FR23)

**Given** `adapters/slack/handler.py` is inspected
**When** its imports are checked
**Then** `slack_bolt` is imported only in this file — no other module in the project imports it (NFR15)
**And** `main.py` wires `config.py` → `logging_setup.py` → `Orchestrator` → `SlackHandler` in the correct initialization order
**And** the Socket Mode connection is established via `AsyncApp` with `SLACK_APP_TOKEN`

---

## Epic 5: Operational Reliability & Proactive Monitoring

The agent runs every working day without babysitting — auto-starts on boot, recovers from crashes automatically, proactively alerts Jason about Gmail token expiry and Gemini quota limits, and maintains 7 days of structured diagnostic logs.

### Story 5.1: Windows Auto-Start & Crash Recovery

As Jason,
I want the agent to start automatically when my computer boots and restart itself within 60 seconds after any crash,
So that it's available every morning without me ever having to open a terminal.

**Acceptance Criteria:**

**Given** `start.bat` is configured as a Windows Task Scheduler task triggered at system startup
**When** the computer boots
**Then** the agent process starts automatically without any manual intervention (FR27)
**And** the Slack Socket Mode connection is established within 60 seconds of boot

**Given** the agent process crashes unexpectedly
**When** Windows Task Scheduler detects the process has exited
**Then** it restarts the process within 60 seconds (NFR11)
**And** the restart policy is configured for up to 3 automatic restart attempts

**Given** `start.bat` is inspected
**When** its contents are reviewed
**Then** it invokes `python -m open_fleet.main` from the correct working directory
**And** stdout and stderr are redirected to `logs/startup.log` for diagnosis of boot-time failures

**Given** the Task Scheduler configuration is documented
**When** a new machine setup is performed
**Then** the README or operational runbook contains step-by-step Task Scheduler setup instructions sufficient for Jason to configure it without external help

### Story 5.2: Extraction Run Structured Logging

As Jason,
I want every extraction run to write a complete structured log entry with all required diagnostic fields,
So that I can reconstruct exactly what happened in any failed run using up to 7 days of retained logs — without needing to reproduce the failure.

**Acceptance Criteria:**

**Given** an extraction run completes successfully
**When** the orchestrator logs the result
**Then** a JSON log entry is written to `logs/open_fleet.log` containing all 5 required fields: `provider` (`"lmstudio"` or `"gemini"`), `email_count` (int), `action_item_count` (int), `duration_ms` (int), `error` (null) (FR28, NFR14)
**And** the `timestamp` field is a UTC ISO8601 string

**Given** an extraction run fails at any stage
**When** the orchestrator logs the failure
**Then** a JSON log entry is written with `error` containing the exception type and message
**And** `action_item_count` is 0 and `provider` reflects whichever provider was active when the failure occurred (or `null` if failure was pre-LLM)

**Given** `logs/open_fleet.log` is inspected after 7 days of daily runs
**When** log retention is verified
**Then** at least 7 days of extraction run entries are present (RotatingFileHandler retains sufficient history)
**And** no raw email body content appears anywhere in any log file (NFR7)

**Given** the test suite runs log assertions
**When** `logging_setup.py` is used in tests with a mock handler
**Then** the 5-field schema is verifiable without writing to the production log file

### Story 5.3: Gmail OAuth Token Expiry Monitoring

As Jason,
I want a proactive Slack alert at least 3 days before my Gmail OAuth token expires,
So that I'm never locked out of my own triage tool on a Monday morning because a token quietly expired over the weekend.

**Acceptance Criteria:**

**Given** the agent starts up and `token.json` exists
**When** `config.py` or a startup health check reads the token's expiry metadata
**Then** if the token expires within 3 days, a `⚠️ Gmail OAuth token expires in {n} days — run scripts/setup_gmail_auth.py to refresh` message is sent to Jason's Slack DM (FR26)
**And** the agent continues running normally — the warning does not halt operation

**Given** the token expiry check runs
**When** the token has more than 3 days remaining
**Then** no Slack message is sent and startup proceeds silently

**Given** the token has already expired at startup
**When** the check runs
**Then** a `❌ Gmail OAuth token has expired — run scripts/setup_gmail_auth.py to reconnect` message is sent
**And** the agent starts but will return a `GmailAuthError` on the first extraction attempt

**Given** `token.json` does not contain expiry metadata
**When** the check runs
**Then** the check is skipped gracefully and logged at `WARNING` level — no crash, no Slack message

### Story 5.4: Gemini Quota Monitoring & Alert

As Jason,
I want a Slack alert when my Gemini free tier daily quota approaches its limit,
So that I can take action before my fallback LLM becomes unavailable mid-day.

**Acceptance Criteria:**

**Given** a Gemini extraction call completes
**When** the response includes token usage metadata
**Then** the cumulative daily token count is tracked in memory for the current process lifetime (FR29)
**And** when cumulative usage reaches 80% of the configured daily limit (default: 1M tokens/day), a `⚠️ Gemini quota at 80% — {used} of {limit} tokens used today` message is sent to Jason's Slack DM

**Given** the quota alert has already fired once today
**When** subsequent Gemini calls push usage higher
**Then** a second alert fires at 95% threshold
**And** no further alerts are sent above 95% to avoid Slack noise

**Given** the agent process restarts mid-day
**When** Gemini calls resume
**Then** the in-memory counter resets to 0 (acceptable behavior — persistent quota tracking is post-MVP)
**And** the behavior is documented in the operational runbook

**Given** Gemini is not used in a run (LM Studio is the active provider)
**When** the quota check runs
**Then** no Slack message is sent and the counter is not incremented
