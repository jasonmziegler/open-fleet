---
stepsCompleted: ["step-01-document-discovery", "step-02-prd-analysis", "step-03-epic-coverage-validation", "step-04-ux-alignment", "step-05-epic-quality-review", "step-06-final-assessment"]
workflowStatus: complete
completedAt: "2026-02-28"
documentsUsed:
  prd: "_bmad-output/planning-artifacts/prd.md"
  architecture: "_bmad-output/planning-artifacts/architecture.md"
  epics: "_bmad-output/planning-artifacts/epics.md"
  ux: null
---

# Implementation Readiness Assessment Report

**Date:** 2026-02-28
**Project:** open-fleet

## Document Inventory

### PRD Documents
**Whole Documents:**
- `prd.md` (36,179 bytes, modified 2026-02-21)
- `prd-validation-report.md` (21,911 bytes, modified 2026-02-21) *(validation report — not the PRD itself)*

**Sharded Documents:** None found

---

### Architecture Documents
**Whole Documents:**
- `architecture.md` (24,675 bytes, modified 2026-02-22)

**Sharded Documents:** None found

---

### Epics & Stories Documents
**Whole Documents:**
- `epics.md` (44,968 bytes, modified 2026-02-28)

**Sharded Documents:** None found

---

### UX Design Documents
**Whole Documents:** None found
**Sharded Documents:** None found

---

### Additional Documents Found
- `product-brief-open-fleet-2026-02-16.md` (53,556 bytes, modified 2026-02-20) *(product brief — supporting context)*

---

## PRD Analysis

### Functional Requirements

| ID | Requirement |
|---|---|
| FR1 | User can trigger email extraction using natural language Slack messages (e.g., `extract today's emails`, `what's urgent today?`) |
| FR2 | User can specify a custom timeframe for email extraction (e.g., `check emails since yesterday 5pm`) |
| FR3 | User can receive all agent responses directly in a Slack DM |
| FR4 | Agent can authenticate with Gmail using OAuth 2.0 and maintain a persistent refresh token |
| FR5 | Agent can fetch emails from Gmail inbox for a specified timeframe (default: last 24 hours) |
| FR6 | Agent can paginate Gmail results to process batches of 150-200+ emails in a single extraction run |
| FR7 | Agent can extract subject, sender, timestamp, and body text from multi-part emails (HTML and plain text) |
| FR8 | Agent can handle Gmail API rate limit errors by retrying with exponential backoff and notifying the user of any resulting delay |
| FR9 | Agent can identify explicit action requests within email content (requests, approvals, deliverables) |
| FR10 | Agent can identify implicit action items (questions requiring response, pending decisions) |
| FR11 | Agent can extract deadlines from email content, both explicit ("by EOD Friday") and implied ("urgent", "ASAP") |
| FR12 | Agent can classify each action item by priority tier (urgent, this week, no deadline) |
| FR13 | Agent can detect and classify email sender sentiment (neutral, frustrated, escalated) |
| FR14 | Agent can batch-process multiple emails in a single LLM inference call |
| FR15 | Agent can route extraction requests to LM Studio as the primary LLM provider |
| FR16 | Agent can automatically fall back to Gemini when LM Studio is unavailable or exceeds the response timeout |
| FR17 | Agent can validate LLM output against a required JSON schema before use |
| FR18 | Agent can retry a failed or invalid LLM response once before escalating to graceful failure |
| FR19 | Agent can log which LLM provider handled each extraction run |
| FR20 | Agent can deliver a formatted Slack response with action items grouped by priority tier (🔴 Urgent → 💬 Needs Response → ⏰ Approaching deadline → 🟡 This week → 🟢 No deadline) |
| FR21 | Agent can include sender, timestamp, and a context excerpt (max 100 characters) for each action item |
| FR22 | Agent can report the total email count and timeframe scanned in the response header |
| FR23 | Agent can split responses exceeding Slack's message size limit across multiple sequential messages |
| FR24 | Agent can deliver structured error notifications to the user when any operation fails, using consistent ⚠️/❌ formatting with actionable next steps |
| FR25 | Agent can validate all required configuration values at startup and halt with specific, actionable error messages if any are missing or invalid |
| FR26 | Agent can detect Gmail OAuth token expiry and notify the user via Slack at least 3 days before the token expires |
| FR27 | Agent can start automatically on system boot without manual terminal intervention |
| FR28 | Agent can write structured logs for each extraction run (provider used, email count, duration, errors) |
| FR29 | Agent can monitor Gemini free tier quota usage and alert the user when approaching the daily limit |
| FR30 | User can configure all credentials and service settings via a `.env` file without modifying source code |
| FR31 | Agent can store Gmail OAuth refresh tokens in a local file, outside of source code and version control |
| FR32 | Agent can process email content through the local LLM provider without transmitting data externally when LM Studio is active |
| FR33 | Agent can discard raw email body content after each extraction run without writing it to persistent storage |

**Total FRs: 33**

---

### Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR1 | Performance | End-to-end extraction response time must not exceed 60 seconds for batches of up to 200 emails under normal conditions |
| NFR2 | Performance | LM Studio inference requests must complete within 30 seconds; timeout triggers Gemini fallback |
| NFR3 | Performance | Gmail fetch and parse operations must complete within 20 seconds |
| NFR4 | Performance | 60-second ceiling must hold regardless of batch size (200 emails = same budget as 50 emails) |
| NFR5 | Security | All credentials stored in `.env`, excluded from version control; no credentials in source code |
| NFR6 | Security | Gmail OAuth refresh tokens stored in local `token.json` outside source tree, excluded from version control |
| NFR7 | Security | Raw email body content must not be written to disk at any point |
| NFR8 | Security | Email content stays on local machine when LM Studio is active; transmitted only over HTTPS to Google when Gemini is active |
| NFR9 | Security | Agent must not expose any inbound network ports; all communication is outbound-only |
| NFR10 | Reliability | 95%+ availability during working hours (Mon–Fri, 7am–6pm local time) |
| NFR11 | Reliability | Agent process must auto-restart after crash within 60 seconds via OS task scheduler |
| NFR12 | Reliability | LLM provider failover (LM Studio → Gemini) must be automatic, require no user action; user notified via Slack |
| NFR13 | Reliability | Failed extraction must never deliver partial or malformed response; result is either complete valid response or clear error message |
| NFR14 | Reliability | 7 days of structured local logs sufficient to diagnose any failure |
| NFR15 | Architecture | Slack Bolt must not be imported or referenced outside the interface adapter layer |
| NFR16 | Architecture | All core extraction functions must accept and return interface-agnostic data types (no Slack-specific objects) |
| NFR17 | Architecture | Adding a new interface adapter must require no modifications to any existing core, LLM, or tool module |

**Total NFRs: 17**

---

### Additional Requirements & Constraints

- **Dual-LLM strategy:** LM Studio (Qwen Coder 2.5) as primary; Gemini 1.5 Flash as cloud fallback
- **85%+ action item detection accuracy** validated by manual spot-check of 10% of emails weekly for first month
- **No framework lock-in:** Slack Bolt and google-api-python-client are the only significant dependencies; no LangChain or CrewAI
- **Single Python process:** Auto-start via Windows Task Scheduler on boot
- **Slack Socket Mode only:** Persistent outbound WebSocket, no public URL, no tunnel required
- **Required JSON schema for LLM output:** `action_items[]` with description, client, sender, email_timestamp, deadline, priority, sentiment, context
- **Startup validation:** Check all `.env` vars, LM Studio reachability, Gmail token validity before accepting any commands
- **Gemini quota tracking:** Alert at 80% of daily quota (1M tokens/day, 15 RPM)
- **Slack rate limiting:** 1 message/sec per channel; response buffering required
- **Log retention:** Minimum 7 days structured logs
- **Version pinning:** All dependency versions pinned in `requirements.txt`

---

### PRD Completeness Assessment

The PRD is well-structured and thorough. Key observations:

**Strengths:**
- 33 FRs and 17 NFRs are clearly numbered, atomic, and largely testable
- User journeys directly map to requirement groups (cross-reference table provided)
- Success criteria are measurable with specific numeric targets
- Architecture constraints (NFR15-17) are explicit about interface-agnostic core

**Areas requiring close attention during epic/story coverage validation:**
- FR14 (batch-processing): No limit on how many emails per LLM call — needs a story-level decision
- NFR4: "Same 60-second ceiling for 50 emails as for 200" is an aggressive constraint — story must include a performance test or validation
- FR29 (Gemini quota monitoring): Requires tracking token consumption per run — implementation detail needs a story
- FR26 (OAuth token expiry detection): Requires a background polling mechanism separate from the extraction flow — may need its own story
- NFR15-17 (architecture constraints): These are cross-cutting and easy to miss in individual stories — need to verify they're explicitly called out somewhere

---

## Epic Coverage Validation

### Coverage Matrix

| FR | PRD Requirement (summary) | Epic | Story | Status |
|---|---|---|---|---|
| FR1 | Natural language Slack command trigger | Epic 4 | Story 4.3 | ✅ Covered |
| FR2 | Custom timeframe specification | Epic 4 | Story 4.3 | ✅ Covered |
| FR3 | All responses in Slack DM | Epic 4 | Story 4.3 | ✅ Covered |
| FR4 | Gmail OAuth 2.0 + persistent refresh token | Epic 2 | Story 2.1 | ✅ Covered |
| FR5 | Fetch emails for specified timeframe (default 24h) | Epic 2 | Story 2.2 | ✅ Covered |
| FR6 | Paginate Gmail results (150-200+ emails) | Epic 2 | Story 2.2 | ✅ Covered |
| FR7 | Multi-part email parsing (subject/sender/timestamp/body) | Epic 2 | Story 2.3 | ✅ Covered |
| FR8 | Gmail rate limit: exponential backoff + user notification | Epic 2 | Story 2.4 | ✅ Covered |
| FR9 | Identify explicit action requests | Epic 3 | Story 3.5 | ✅ Covered |
| FR10 | Identify implicit action items | Epic 3 | Story 3.5 | ✅ Covered |
| FR11 | Extract deadlines (explicit and implied) | Epic 3 | Story 3.5 | ✅ Covered |
| FR12 | Classify priority (urgent/this_week/no_deadline) | Epic 3 | Story 3.5 | ✅ Covered |
| FR13 | Detect and classify sender sentiment | Epic 3 | Story 3.5 | ✅ Covered |
| FR14 | Batch-process multiple emails in single LLM call | Epic 3 | Story 3.5 | ✅ Covered |
| FR15 | Route to LM Studio as primary LLM | Epic 3 | Story 3.2 | ✅ Covered |
| FR16 | Auto-fallback to Gemini when LM Studio unavailable | Epic 3 | Story 3.4 | ✅ Covered |
| FR17 | Validate LLM output against Pydantic JSON schema | Epic 3 | Story 3.1, 3.4 | ✅ Covered |
| FR18 | Retry failed/invalid LLM response once | Epic 3 | Story 3.4 | ✅ Covered |
| FR19 | Log which LLM provider handled each run | Epic 3 | Story 3.4 | ✅ Covered |
| FR20 | Formatted Slack response grouped by priority tier | Epic 4 | Story 4.1 | ✅ Covered |
| FR21 | Sender, timestamp, 100-char context excerpt per item | Epic 4 | Story 4.1 | ✅ Covered |
| FR22 | Total email count + timeframe in response header | Epic 4 | Story 4.1 | ✅ Covered |
| FR23 | Split responses exceeding 4,000-char Slack limit | Epic 4 | Story 4.1 | ✅ Covered |
| FR24 | Structured error notifications (⚠️/❌ format) | Epic 4 | Story 4.2 | ✅ Covered |
| FR25 | Startup config validation with actionable errors | Epic 1 | Story 1.3 | ✅ Covered |
| FR26 | Gmail OAuth token expiry: Slack alert 3 days advance | Epic 5 | Story 5.3 | ✅ Covered |
| FR27 | Auto-start on system boot | Epic 5 | Story 5.1 | ✅ Covered |
| FR28 | Structured logs per extraction run | Epic 5 | Story 5.2 | ✅ Covered |
| FR29 | Gemini quota monitoring + Slack alert | Epic 5 | Story 5.4 | ✅ Covered |
| FR30 | All credentials configurable via `.env` | Epic 1 | Story 1.3 | ✅ Covered |
| FR31 | Gmail OAuth tokens in local `token.json` outside VCS | Epic 1 | Story 1.1, 2.1 | ✅ Covered |
| FR32 | Email content not transmitted externally (LM Studio path) | Epic 3 | Story 3.2 | ✅ Covered |
| FR33 | Raw email body discarded after extraction run | Epic 2 | Story 2.3 | ✅ Covered |

### NFR Coverage Summary

| NFR | Category | Covering Story | Status |
|---|---|---|---|
| NFR1 | Performance (<60s end-to-end) | Story 4.2 AC | ✅ Covered |
| NFR2 | Performance (LM Studio 30s timeout) | Story 3.2 AC | ✅ Covered |
| NFR3 | Performance (Gmail fetch <20s) | Story 2.2 AC | ✅ Covered |
| NFR4 | Performance (60s ceiling regardless of batch size) | Story 4.2 AC | ✅ Covered |
| NFR5 | Security (credentials in .env, excluded from VCS) | Story 1.1, 1.3 | ✅ Covered |
| NFR6 | Security (token.json outside source tree) | Story 1.1, 2.1 | ✅ Covered |
| NFR7 | Security (no email body written to disk) | Story 2.3, 5.2 | ✅ Covered |
| NFR8 | Security (data stays local/HTTPS per provider) | Story 3.2, 3.3 | ✅ Covered |
| NFR9 | Security (no inbound ports) | Architecture-only | ⚠️ No explicit story AC |
| NFR10 | Reliability (95% availability) | Story 5.1 (indirectly) | ⚠️ No measurable story AC |
| NFR11 | Reliability (auto-restart <60s) | Story 5.1 | ✅ Covered |
| NFR12 | Reliability (automatic LLM failover) | Story 3.4 | ✅ Covered |
| NFR13 | Reliability (no partial/malformed responses) | Story 3.4, 4.2 | ✅ Covered |
| NFR14 | Reliability (7-day logs) | Story 5.2 | ✅ Covered |
| NFR15 | Architecture (Slack Bolt only in adapter layer) | Story 4.1, 4.2, 4.3 | ✅ Covered |
| NFR16 | Architecture (interface-agnostic data types) | Story 4.1, 4.2 | ✅ Covered |
| NFR17 | Architecture (new adapter = no core changes) | Enforced by NFR15/16 | ✅ Covered |

### Missing Requirements

#### No Missing FRs
All 33 Functional Requirements from the PRD are traced to at least one story in the epics document. FR coverage is 100%.

#### NFR Gaps Found (⚠️ — Not Blocking, But Notable)

**NFR9 — No Inbound Ports:**
- Impact: The constraint is architecturally satisfied by Socket Mode, but no story acceptance criterion explicitly validates it (e.g., a test asserting no listening sockets)
- Recommendation: Add a note to Story 4.3 or Story 1.1 AC that the agent must not call `listen()` or open any server port. Low risk — architecturally enforced by the socket mode approach.

**NFR10 — 95%+ Availability:**
- Impact: This is an operational SLA, not directly testable in unit/integration tests. Story 5.1 enables it (crash recovery) but doesn't explicitly validate it as a measured outcome
- Recommendation: This is acceptable for MVP. Document in the operational runbook that the SLA is measured informally via "does it respond at 7am?" for the first month. No story change needed, but the gap should be acknowledged.

### Coverage Statistics

- **Total PRD FRs:** 33
- **FRs covered in epics:** 33
- **FR coverage percentage:** **100%**
- **Total PRD NFRs:** 17
- **NFRs with explicit story-level AC:** 15
- **NFRs addressed architecturally (no explicit AC):** 2 (NFR9, NFR10)
- **NFR coverage percentage:** **88% explicit / 100% addressed**

---

## UX Alignment Assessment

### UX Document Status

**Not Found** — No UX design document exists in `_bmad-output/planning-artifacts/`.

### Assessment: Is UX Implied?

open-fleet is a **backend-only Python agent service** with **no web UI, no mobile app, no visual components, and no user-facing web interface**. The PRD explicitly excludes a web UI from MVP scope and states: *"No UI — Slack is the only interface."*

The product's "UX" is entirely expressed through Slack message formatting, which is fully specified in:
- **FR20–FR24** (response format, priority grouping, emoji codes, error messages, message splitting)
- **PRD error message standards** (`⚠️`/`❌` formatting with actionable next steps)
- **Story 4.1** (ResponseFormatter acceptance criteria — complete Slack output specification)
- **Story 4.2** (Orchestrator error message AC — consistent error format)

### Alignment Issues

**None.** Since the interface is Slack-only and fully described in the PRD and epics, there is no UX document gap.

### Warnings

⚠️ **UX is Slack-format-only (intentional, not a gap):** The "user experience" is the quality of Slack message formatting. All visual/format requirements for the Slack output are covered in Stories 4.1–4.3 ACs. No additional UX documentation is needed for this product type.

**Conclusion:** No UX document required for this project. The Slack response format specifications in the PRD and epics serve as the complete UX specification. ✅

---

## Epic Quality Review

### Epic Structure Validation

#### Epic 1: Project Foundation & Architecture Scaffold

| Check | Result |
|---|---|
| User-centric title? | ⚠️ No — "scaffold/architecture" is technical framing |
| User/operator value delivered? | Partial — Stories 1.3 (startup validation) and 1.4 (logging) deliver operator value; Stories 1.1 and 1.2 are pure technical setup |
| Can function independently? | ✅ Yes — standalone |
| Stories sequenced correctly? | ✅ Yes — 1.1 → 1.2 → 1.3 → 1.4 follows architecture constraint |

**Verdict:** Epic 1 is a **technical milestone epic** — a known best-practices red flag. However, for a greenfield Python backend with an explicit architecture-first constraint (epics document mandates `exceptions.py` → `config.py` → `logging_setup.py` first), this is pragmatically justified. The operator value in Stories 1.3 and 1.4 partially redeems the technical framing. *Acceptable with notation.*

---

#### Epic 2: Gmail Email Retrieval

| Check | Result |
|---|---|
| User-centric title? | ✅ Yes — describes capability (what Jason can do) |
| User/operator value delivered? | ✅ Yes — data pipeline required for all downstream value |
| Can function independently using only Epic 1? | ✅ Yes — GmailClient only needs exceptions.py, config.py, logging from Epic 1 |
| Stories sequenced correctly? | ✅ Yes — 2.1 (auth) → 2.2 (fetch) → 2.3 (parse) → 2.4 (rate limits) |

**Verdict:** ✅ Well-structured epic. Stories are appropriately scoped and sequenced.

---

#### Epic 3: AI Action Item Extraction Engine

| Check | Result |
|---|---|
| User-centric title? | ⚠️ Borderline — "Engine" is technical, but the goal statement is user-centric |
| User/operator value delivered? | ✅ Yes — the core product value (action item extraction) |
| Can function independently using Epics 1-2? | ✅ Yes — LLM layer receives parsed email dicts from Epic 2 |
| Stories sequenced correctly? | ✅ Yes — 3.1 (schema) → 3.2 (LM Studio) → 3.3 (Gemini) → 3.4 (router) → 3.5 (accuracy) |

**Verdict:** ✅ Well-structured. Minor title concern only.

---

#### Epic 4: Slack Command Interface & Triage Reports

| Check | Result |
|---|---|
| User-centric title? | ✅ Yes — clearly describes the user interface and output |
| User/operator value delivered? | ✅ Yes — this is the MVP completion epic (first end-to-end use) |
| Can function independently using Epics 1-3? | ✅ Yes — Slack adapter wraps everything from Epics 1-3 |
| Stories sequenced correctly? | ✅ Yes — 4.1 (formatter) → 4.2 (orchestrator) → 4.3 (Slack wiring) |

**Verdict:** ✅ Strong epic. This is the "it works" milestone and well-defined.

---

#### Epic 5: Operational Reliability & Proactive Monitoring

| Check | Result |
|---|---|
| User-centric title? | ✅ Yes — describes the outcome (reliable daily operation) |
| User/operator value delivered? | ✅ Yes — Jason can trust the agent is running |
| Can function independently using Epics 1-4? | ✅ Yes — monitoring layers build on top of working system |
| Stories sequenced correctly? | ✅ Yes — any order viable; 5.1 → 5.2 → 5.3 → 5.4 is reasonable |

**Verdict:** ✅ Well-structured operational epic.

---

### Story Quality Assessment

#### Best Practices Compliance by Story

| Story | User Value | ACs (GWT format) | Error Paths | Independence | Rating |
|---|---|---|---|---|---|
| 1.1 Scaffold | Developer/Operator | ✅ Specific | N/A | ✅ | ✅ |
| 1.2 Exceptions | Developer only | ✅ Hierarchy tested | N/A | ✅ | ⚠️ |
| 1.3 Config Validation | ✅ Operator (fail-fast) | ✅ 4 scenarios | ✅ token.json missing | ✅ | ✅ |
| 1.4 Logging Setup | Indirect | ✅ Rotation tested | Test isolation ✅ | ✅ | ✅ |
| 2.1 Gmail OAuth | ✅ Jason | ✅ Multi-scenario | ✅ GmailAuthError | ✅ | ✅ |
| 2.2 Email Fetch | ✅ Jason | ✅ Pagination + NFR3 | N/A (no error AC) | ✅ | ⚠️ |
| 2.3 Email Parse | ✅ Jason | ✅ Multi-part + NFR7 | N/A | ✅ | ✅ |
| 2.4 Rate Limits | ✅ Jason | ✅ Backoff specified | ✅ Exhausted retries + non-429 | ✅ | ✅ |
| 3.1 Pydantic Models | Developer only | ✅ Validation tested | ✅ ValidationError | ✅ | ⚠️ |
| 3.2 LM Studio | ✅ Jason | ✅ Request structure | ✅ Timeout + conn refused | ✅ | ✅ |
| 3.3 Gemini | ✅ Jason | ✅ Same pattern | N/A | ✅ | ✅ |
| 3.4 LLM Router | ✅ Jason | ✅ All paths | ✅ Both providers fail | ✅ | ✅ |
| 3.5 Prompt Accuracy | ✅ Jason | ✅ 85% threshold | N/A | ✅ | ✅ |
| 4.1 Formatter | ✅ Jason | ✅ Groups + splitting | N/A | ✅ | ✅ |
| 4.2 Orchestrator | ✅ Jason | ✅ 4 error cases + timing | ✅ Unexpected exception | ✅ | ✅ |
| 4.3 Slack Handler | ✅ Jason | ✅ 3 command patterns | N/A | ✅ | ✅ |
| 5.1 Auto-Start | ✅ Jason | ✅ Boot + recovery | ✅ stdout/stderr redirect | ✅ | ✅ |
| 5.2 Structured Logging | ✅ Jason | ✅ 5-field schema | ✅ Failure logging | ✅ | ✅ |
| 5.3 Token Expiry | ✅ Jason | ✅ 4 scenarios | ✅ No metadata case | ✅ | ✅ |
| 5.4 Quota Monitoring | ✅ Jason | ✅ 80%+95% alerts | ✅ LM Studio path | ✅ | ✅ |

---

### Dependency Analysis

#### Epic-Level Dependency Chain
```
Epic 1 (Foundation) → Epic 2 (Gmail) → Epic 3 (LLM) → Epic 4 (Slack) → Epic 5 (Ops)
```
No circular dependencies. No epic requires a later epic. ✅

#### Within-Epic Story Dependencies
- All stories reference only prior stories within the same epic or earlier epics ✅
- No forward dependencies detected ✅
- Implementation sequence in epics document (exceptions → config → logging → schemas → gmail → lmstudio → gemini → router → orchestrator → response → handler → main) is consistent with story ordering ✅

---

### Quality Issues Found

#### 🔴 Critical Violations
**None.**

---

#### 🟠 Major Issues

**Issue M1 — Timeframe Parsing: Location Undefined**

- **Where:** Story 2.2 (GmailClient.fetch_emails()) and Story 4.3 (Slack handler)
- **Problem:** Story 4.3 says the handler "extracts the timeframe 'since yesterday 5pm'" and passes it to the orchestrator as a string. Story 2.2 says GmailClient "queries the Gmail API with an appropriate `after:` date filter derived from the timeframe." This implies GmailClient performs natural language date parsing — converting "yesterday 5pm" or "last 24 hours" to an absolute UTC datetime. However, **no story specifies the parsing logic, the library used, or the conversion rules**. This is a real implementation gap.
- **Impact:** During development, the developer must invent this logic. If GmailClient handles it, the wrong layer contains NL parsing. If the handler handles it, Story 4.3's AC is incomplete.
- **Recommendation:** Add a parsing specification to Story 2.2's AC: "Given a timeframe string, the `_parse_timeframe()` helper converts recognized patterns ('last 24 hours', 'today', 'since yesterday 5pm') to a UTC `datetime` object using [dateparser or manual logic]. If the timeframe string is unrecognized, `GmailFetchError` is raised with the unrecognized input." Alternatively, add an explicit Story 2.0 or add a Note to Story 4.3.

---

**Issue M2 — Batch Size per LLM Call Unspecified**

- **Where:** Story 3.5, FR14, NFR1/NFR4
- **Problem:** FR14 says "batch-process multiple emails in a single LLM inference call." Story 3.5 confirms `emails_scanned` matches the count sent. But for 200 emails, sending all in one call could: (a) exceed context window limits, (b) cause latency issues affecting NFR1 (60s ceiling). No story specifies whether batching means one call per run or chunked calls.
- **Impact:** Significant performance risk. LM Studio context windows vary; Qwen Coder may have a 32K-128K context. 200 emails at ~500 tokens each = ~100K tokens — potentially exceeding the limit.
- **Recommendation:** Add an AC to Story 3.2 or Story 3.4: "Given `email_batch` contains more than N emails (configurable via `LM_STUDIO_MAX_BATCH_SIZE`, default: 20), the provider splits the batch into chunks and aggregates results before returning a single `ExtractionResult`." Define N in the architecture or epics Additional Requirements.

---

#### 🟡 Minor Concerns

**Issue m1 — Story 2.2: No Error AC for Non-Rate-Limit Fetch Failures**

- **Where:** Story 2.2 AC
- **Problem:** Story 2.4 handles rate limits. Story 2.2 handles the happy path. But Story 2.2 has no AC for network timeouts, 500 errors, or authentication failures during the fetch (these raise GmailFetchError per Story 2.4 / Story 2.1). The orchestrator catches GmailAuthError and GmailRateLimitError in Story 4.2, but what about GmailFetchError? Story 4.2's AC doesn't include a GmailFetchError handler.
- **Impact:** If a network error occurs during fetch, the orchestrator hits the "unexpected exception" catch-all — not a specific user-friendly message.
- **Recommendation:** Add `GmailFetchError` to Story 4.2's orchestrator error ACs: "Given `GmailFetchError` is raised, return `['❌ Gmail fetch failed — check logs for details']`."

**Issue m2 — Story 1.2: "No other module defines exceptions" is a linting convention, not a testable AC**

- **Where:** Story 1.2 AC — "no other module in the project defines custom exception classes"
- **Problem:** This constraint cannot be verified by a unit test. It's a code review / linting rule.
- **Recommendation:** Add this to a ruff/flake8 rule or note in the README as a "coding convention." Minor — doesn't block implementation.

**Issue m3 — Story 5.3: Startup-only token expiry check may miss mid-day expiration**

- **Where:** Story 5.3 — check runs at startup only
- **Problem:** If the agent runs continuously from 7am and the token expires at 2pm, no alert fires mid-day. The PRD says "proactive alerting" with a 3-day window, which implies a startup check is usually sufficient (token expiry warning 3 days early means the token was valid 3 days ago). However, if a fresh `token.json` is written with a 1-hour access token and the refresh token isn't available, startup-only checking could miss it.
- **Impact:** Low — Google refresh tokens typically last 6 months to indefinitely. Access token refresh is automatic in google-auth-oauthlib. The startup check is for the refresh token, which is the only one that truly "expires." This is acceptable for MVP.
- **Recommendation:** Document in Story 5.3 or the operational runbook that the check covers the refresh token's long-term validity, not the short-lived access token.

**Issue m4 — `asyncio.get_event_loop()` deprecated in Python 3.10+**

- **Where:** Story 2.2 AC — "wrapped with `asyncio.get_event_loop().run_in_executor(None, ...)`"
- **Problem:** `asyncio.get_event_loop()` is deprecated in Python 3.10+ and may raise a DeprecationWarning. The correct call in an async context is `asyncio.get_running_loop().run_in_executor(None, ...)`.
- **Impact:** Works but generates deprecation warnings; may break in Python 3.12+.
- **Recommendation:** Update Story 2.2 AC to specify `asyncio.get_running_loop().run_in_executor(None, ...)`.

---

### Best Practices Compliance Checklist

| Epic | Delivers User Value | Functions Independently | Stories Sized Correctly | No Forward Dependencies | Clear ACs | FR Traceability |
|---|---|---|---|---|---|---|
| Epic 1 | ⚠️ Partial (technical) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Epic 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Epic 3 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Epic 4 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Epic 5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### Quality Review Summary

| Severity | Count | Items |
|---|---|---|
| 🔴 Critical | 0 | — |
| 🟠 Major | 2 | M1 (timeframe parsing), M2 (batch size) |
| 🟡 Minor | 4 | m1 (GmailFetchError handler), m2 (linting convention), m3 (startup-only check), m4 (asyncio deprecation) |

---

## Summary and Recommendations

### Overall Readiness Status

## ✅ READY — Proceed to Implementation

The open-fleet project planning artifacts are **implementation-ready**. All 33 Functional Requirements are traced to stories with clear, testable acceptance criteria. No critical violations were found. The 2 major issues identified are **early-implementation clarification points**, not blockers requiring artifact rework before development begins.

---

### Assessment Summary

| Category | Result |
|---|---|
| FR Coverage | ✅ 100% (33/33) |
| NFR Coverage | ✅ 100% addressed (88% with explicit story ACs) |
| UX Alignment | ✅ No UX document required (intentional Slack-only design) |
| Critical Epic Violations | ✅ 0 |
| Major Issues | ⚠️ 2 (address in first sprint) |
| Minor Concerns | ℹ️ 4 (address during relevant story implementation) |
| Forward Dependencies | ✅ None |
| Circular Dependencies | ✅ None |
| Epic Independence | ✅ Verified |

---

### Critical Issues Requiring Immediate Action

There are **no critical issues** blocking implementation. The two major issues must be resolved before (or at the start of) the stories that depend on them:

**Before implementing Story 2.2 (Gmail Fetch):**
> **M2 — Define batch size / chunking strategy for LLM calls.** Add a `LM_STUDIO_MAX_BATCH_SIZE` config value (suggested default: 20 emails per call) and specify that the LLM router chunks email batches and aggregates results. This prevents context window overflow and protects NFR1 (60-second ceiling).

**Before implementing Story 4.3 (Slack Handler):**
> **M1 — Specify timeframe parsing.** Decide: does the Slack handler or GmailClient own the conversion from "yesterday 5pm" to a UTC datetime? Add a `_parse_timeframe(text: str) -> datetime` helper (recommend using `dateparser` library) and specify where it lives. Add to `requirements.txt` if using dateparser.

---

### Recommended Next Steps

1. **Add `dateparser` to requirements.txt** and update Story 2.2 to specify `_parse_timeframe()` helper using it. Alternatively, define a simple mapping for the handful of supported timeframe patterns.

2. **Add `LM_STUDIO_MAX_BATCH_SIZE` to Story 3.2 or the epics Additional Requirements.** Specify chunking behavior so that 200 emails are split into chunks of N before LLM calls.

3. **Add `GmailFetchError` error handler to Story 4.2** — one AC: `❌ Gmail fetch failed — check logs for details`.

4. **Update Story 2.2 AC** to use `asyncio.get_running_loop().run_in_executor()` instead of `asyncio.get_event_loop()`.

5. **Begin implementation in story order:** Start with Epic 1 Story 1.1 (scaffold + dependencies) and follow the mandated implementation sequence. The architecture-enforced ordering in the epics document is correct and should be treated as the sprint sequencing guide.

---

### Final Note

This assessment reviewed **prd.md** (33 FRs, 17 NFRs), **architecture.md**, and **epics.md** (5 epics, 20 stories) for the open-fleet project. The planning artifacts are thorough, internally consistent, and well-traced. The epics document in particular is one of the most complete seen for a project of this scope — every story has precise Given/When/Then acceptance criteria, explicit NFR references, and clear import boundary checks.

The 6 issues identified (0 critical, 2 major, 4 minor) are **implementation clarifications**, not planning failures. This project is ready to build.

**Assessed by:** Claude Code (expert Product Manager + Scrum Master role)
**Assessment date:** 2026-02-28
**Report:** `_bmad-output/planning-artifacts/implementation-readiness-report-2026-02-28.md`
