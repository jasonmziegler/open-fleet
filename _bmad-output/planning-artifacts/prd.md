---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-02b-vision', 'step-02c-executive-summary', 'step-03-success', 'step-04-journeys', 'step-05-domain', 'step-06-innovation', 'step-07-project-type', 'step-08-scoping', 'step-09-functional', 'step-10-nonfunctional', 'step-11-polish', 'step-12-complete']
workflowStatus: complete
completedAt: '2026-02-21'
inputDocuments: ['planning-artifacts/product-brief-open-fleet-2026-02-16.md']
workflowType: 'prd'
briefCount: 1
researchCount: 0
brainstormingCount: 0
projectDocsCount: 0
classification:
  projectType: api_backend
  domain: general
  complexity: medium
  projectContext: greenfield
---

# Product Requirements Document - open-fleet

**Author:** Jason
**Date:** 2026-02-21

## Executive Summary

**open-fleet** is a local-first AI agent that runs as a Python backend service, receives natural language commands via Slack, and executes real internal business workflows — starting with Gmail email triage. It is built for a single user (Jason) to use daily, with the explicit success criterion: be measurably ahead of work within one week of deployment.

The product operates on a dual-LLM strategy — LM Studio with Qwen Coder (local, ~200 t/s, zero marginal cost) as primary, Google Gemini free tier as cloud fallback — connected to Slack via Socket Mode (persistent outbound WebSocket, no public URL or tunnel required). Phase 1 delivers one workflow: scan 150-200 Gmail messages, extract action items with priority and sentiment classification, and return a structured Slack response in under 60 seconds. No task management integrations, no multi-user support, no UI — Slack is the only interface.

The problem being solved is straightforward: an account manager managing 18+ clients and 150-200 emails per day spends 2-3 hours daily on manual triage that produces no strategic value. open-fleet eliminates that overhead. Success is not a feature list — it is the user clocking out early on a Friday.

### What Makes This Special

Three properties that no existing solution combines:

1. **Near-zero marginal cost** — Local LM Studio inference after hardware means unlimited automation runs with no per-token fees. Gemini free tier provides a zero-cost cloud path. Neither n8n, Make.com, nor AI agency custom builds can match this cost floor.
2. **Lean by design, no framework lock-in** — Custom Python with no LangChain, CrewAI, or abstraction layers. Single integration path (Slack + Cloudflare). Fully debuggable, fully controllable. Complexity that can be explained in one README.
3. **Internal work elimination, not external AI theatre** — The product automates the user's own workflow (email → action items), not a customer-facing chatbot. It removes actual hours from the workday, not just a messaging channel.

The core timing insight: local models crossed a production-viability threshold (200 t/s on consumer hardware). That shift, combined with market saturation of overpriced AI chatbot solutions, creates a narrow window for a lean, honest, local-first alternative.

## Project Classification

- **Project Type:** API Backend — Python service with Slack Socket Mode (outbound WebSocket) and REST API integrations (outbound: Gmail, future Asana/Calendar)
- **Domain:** General / Productivity Automation — no regulated industry constraints
- **Complexity:** Medium — multiple OAuth-based API integrations, dual-LLM provider routing, structured output requirements, reliability targets (95% uptime, <60s response)
- **Project Context:** Greenfield — development environment bootstrapped, no existing production system

## Success Criteria

### User Success

The singular measure of user success: **after one week of use, Jason is ahead of his work rather than behind it** — clocking out on time or early, with zero missed action items from 150-200 daily emails.

Supporting indicators that confirm this is happening:

- **Time saved:** 1-2 hours/day recovered from manual email triage (7-10 hours/week minimum). Baseline: 2-3 hours/day reading 200 emails. Target: 15-30 minutes reviewing agent output.
- **Accuracy:** Agent surfaces 85%+ of real action items. Zero urgent emails missed in any given day.
- **False positives:** <10% of flagged items are irrelevant or incorrect.
- **Response time:** Agent responds to Slack command in <60 seconds consistently.
- **Habit formed:** Used every working day by end of Week 2 without prompting.
- **Trust signal:** User stops manually reading all 200 emails — agent output is the primary triage mechanism.
- **Stress signal:** No weekend catch-up work by Week 4. Confident walking into client meetings.

### Business Success

Jason has defined three business outcomes in priority order:

1. **Save my job** (Weeks 1-8) — Stabilize performance through productivity gains. Measurable: manager or client notices improvement. Zero missed deadlines for 2 consecutive weeks.
2. **Land one consulting client** (Months 3-6) — Validate the tool as a deployable service. Target: $500-$5,000 paid engagement (DWY or DFY service tier). Client reports 8+ hours/week time savings.
3. **Generate job offers** (Months 3-12) — Portfolio piece drives interview interest. Target: 2+ offers where open-fleet is cited as a differentiator.

### Technical Success

- **Uptime:** 95%+ daily availability during working hours (agent running, Slack Socket Mode connection stable)
- **Accuracy floor:** 85%+ action item detection rate, validated by manual spot-check of 10% of emails weekly for first month
- **Latency ceiling:** <60 seconds end-to-end (Slack command received → response delivered) for batches up to 200 emails
- **Error handling:** Graceful degradation when Gmail API rate limits hit or LLM call fails — user notified, no silent failure
- **LLM fallback:** Automatic routing from LM Studio to Gemini if local model unavailable, with no user intervention required

### Measurable Outcomes

| Outcome | Baseline | Target | Timeline |
|---|---|---|---|
| Daily email triage time | 2-3 hours | 15-30 minutes | Week 2 |
| Missed urgent emails | Unknown | 0/week | Week 2 |
| Deadline hit rate | 60-70% | 95%+ | Week 6 |
| Weekend/overtime work | 8-10 hrs/week | 0-2 hrs/week | Week 8 |
| Agent daily usage | N/A | 6-7 days/week | Week 2 |
| Consulting revenue | $0 | $500+ | Month 6 |


## User Journeys

### Journey 1: Jason — Monday Morning Triage (Happy Path)

**Opening Scene:** It's 7:02am. Jason's phone lit up overnight. He knows there are 80+ unread emails from Friday afternoon and the weekend — clients in different time zones, a project that may have gone sideways, someone who needed a decision he didn't make. He opens his laptop with the same low-grade dread he's had every Monday for months.

Instead of opening Gmail, he opens Slack and types: `extract today's emails`

**Rising Action:** Thirty seconds pass. The agent is querying Gmail, chunking 187 emails, running them through Qwen Coder, assembling the priority structure. Jason gets a cup of coffee.

**Climax:** The response lands. 14 action items, sorted by urgency. Two are flagged 🔴 URGENT — due today. One has a 💬 frustrated sentiment tag: a client named Lisa Thompson wrote "This is the third time we've had to push this back." The agent surfaced it before Jason would have gotten to it in his normal inbox scroll.

**Resolution:** By 7:45am, Jason has responded to the two urgent items, added a calendar reminder to call Lisa before noon, and delegated three tasks to his team via Slack. He's already operating proactively. By 5pm, he closes his laptop on time — first time in three weeks.

*Capabilities revealed:* Slack command parsing, Gmail OAuth + inbox fetch, LLM extraction with priority/sentiment classification, formatted Slack response delivery.

---

### Journey 2: Jason — The Agent Returns Garbage (Edge Case)

**Opening Scene:** Wednesday, 8:15am. Jason runs his usual `extract today's emails`. The response comes back in 45 seconds — but something's off. The "action items" are vague: "Email about project" with no sender, no deadline, no context. The LLM has clearly hallucinated structure without real content. Three genuinely urgent emails are missing entirely.

**Rising Action:** Jason types `check emails since yesterday 5pm` to try again. Same garbled output. He checks the terminal — Qwen Coder hit a timeout. The agent silently fell back to nothing, returning a partial response with no error message.

**Climax:** Jason has no idea what's real and has to manually open Gmail anyway — the exact thing he was trying to avoid. Worse, he doesn't know if this happened yesterday too.

**Resolution:** He checks the logs, sees the LLM timeout, manually triggers Gemini fallback by setting an env var, and re-runs. The response is accurate. He adds a GitHub issue: "Silent LLM failure must surface an error message and auto-retry with Gemini fallback."

*Capabilities revealed:* LLM fallback routing (LM Studio → Gemini), structured error responses in Slack ("⚠️ LM Studio unavailable — retrying with Gemini..."), retry logic, logging for debugging.

---

### Journey 3: Jason as Operator — Keeping It Running

**Opening Scene:** It's Sunday night. Jason goes to run a test command before the week starts and gets no response from the Slack bot. The agent isn't running. He has no idea how long it's been down.

**Rising Action:** He checks his machine — the Python process crashed overnight. He restarts it manually from the terminal. Then he realizes his Gmail OAuth token expired three days ago and needs to be refreshed. He goes through the OAuth flow again, copies the new token into the `.env` file.

**Climax:** He gets it running again, but it took 25 minutes and he's not confident it won't happen again tomorrow morning when he actually needs it.

**Resolution:** He adds a startup script to his Windows Task Scheduler so the agent auto-starts on boot. He adds token expiry logging so the agent tells him via Slack "⚠️ OAuth token expires in 3 days — please refresh" rather than silently failing.

*Capabilities revealed:* Process resilience and startup behavior, OAuth token expiry monitoring and Slack alerts, `.env`-based configuration, clear operational runbook/README.

---

### Journey 4: Future Consulting Client — First Deployment

**Opening Scene:** Marcus is a project manager at a mid-size agency. He saw Jason's LinkedIn post about open-fleet, watched the 3-minute demo, and booked a DWY session. He's not a developer but he's technically literate — he's used to setting up SaaS tools.

**Rising Action:** Jason screen-shares and walks Marcus through the setup: Google Cloud Console OAuth setup, Slack app creation (Socket Mode — no tunnel required), `.env` file population. Marcus follows along but needs three clarifications on the Google Cloud Console steps. The whole session takes 75 minutes instead of the promised 60.

**Climax:** Marcus types `extract today's emails` in his Slack for the first time. 23 action items from 156 emails. He says "oh my god" out loud. He didn't realize how many things he was dropping.

**Resolution:** Marcus is live. But the next day he messages Jason: "It stopped working, something about an env var." The setup was too manual — one wrong `.env` value breaks everything silently.

*Capabilities revealed:* Clear setup documentation, `.env` validation on startup (fail fast with specific error messages), setup guide that a non-developer can follow, error messages that tell the user *exactly* what to fix.

---

### Journey Requirements Summary

| Journey | Key Capabilities Required | Covering FRs |
|---|---|---|
| Morning triage (happy path) | Slack command parsing, Gmail OAuth fetch, LLM extraction, structured Slack response | FR1-3, FR4-7, FR9-16, FR20-23 |
| Agent failure (edge case) | LLM fallback routing, Slack error messages, retry logic, debug logging | FR16-19, FR24, FR28 |
| Operator maintenance | OAuth token expiry alerts, process auto-restart, `.env`-based config, operational docs | FR25-28, FR30-31 |
| Client deployment | Setup validation, informative error messages, non-developer-friendly setup guide | FR24-25, FR30 |

## Domain-Specific Requirements

### Integration Constraints

- **Gmail OAuth token lifecycle** — Access tokens expire; the agent must detect expired/invalid tokens and surface a clear Slack notification ("⚠️ Gmail OAuth token expired — re-authentication required at [instructions URL]") rather than failing silently. Refresh token storage must be handled securely in `.env` or local token file, not hardcoded.
- **Gmail API rate limits** — Gmail API enforces per-user quotas (250 quota units/second, 1B units/day). Batch requests should be used where possible. Rate limit errors (HTTP 429) must be caught and retried with exponential backoff; user must be notified if extraction is delayed as a result.
- **Slack API constraints** — Slack message size limit is 4,000 characters per block. Responses exceeding this must be paginated across multiple messages or truncated with a "show more" indicator. Slack Bolt Socket Mode maintains a persistent outbound WebSocket connection; the agent process must be daemonized or auto-started.

### Data Privacy

- **Email content and LLM routing** — Email body text is sensitive business data. When routing to LM Studio (local), data stays on the user's machine — no external exposure. When routing to Gemini (cloud fallback), email content is transmitted to Google's API. Users must be aware of this distinction. The agent should log which LLM provider handled each request.
- **No persistent email storage** — The agent must not store raw email content beyond the duration of a single extraction run. Extracted action items (structured JSON) may be logged for debugging, but raw email bodies must not be written to disk.

### LLM Reliability Constraints

- **Local model availability is non-deterministic** — LM Studio may be offline, slow, or returning degraded output. The agent must implement: (1) timeout detection (<30s response threshold), (2) automatic fallback to Gemini with Slack notification, (3) structured output validation — if LLM response fails JSON schema check, retry once before failing gracefully.
- **Structured output compliance** — Both LLM providers must be prompted with explicit JSON schema instructions and output validated against expected structure before being used to generate a Slack response. Malformed output must never reach the user as a garbled response.

### Risk Mitigations

| Risk | Mitigation |
|---|---|
| Gmail OAuth token expiry breaks morning triage | Token expiry monitoring with 3-day advance Slack alert |
| LM Studio offline during use | Auto-fallback to Gemini with user notification |
| LLM returns garbled/incomplete JSON | Schema validation + retry before graceful failure |
| Gmail rate limit during large inbox scan | Exponential backoff + user notification of delay |
| Email content exposed via cloud LLM | Log LLM provider per run; user controls fallback preference via config |

## Innovation & Novel Patterns

### Detected Innovation Areas

**1. Dual-LLM Provider Routing in a Personal Productivity Agent**
No mainstream personal productivity tool combines a local inference provider (LM Studio) with a cloud fallback (Gemini) in a single, transparent agent loop. The innovation is the *routing logic itself* — the agent selects its LLM provider dynamically based on availability and response quality, logs the provider used, and degrades gracefully. This is API composition applied to LLM orchestration, not to external services.

**2. Zero-Marginal-Cost Automation as a Design Constraint**
Most automation tools (n8n, Make.com, Zapier AI) treat token cost as a runtime expense passed to the user. open-fleet treats it as a *design constraint* — the architecture is specifically chosen to minimize or eliminate marginal cost. Local LM Studio = effectively $0/run after hardware. This cost model is genuinely unusual for a tool that performs real LLM-backed analysis on 150-200 emails per day.

**3. Internal Workflow Elimination vs. External AI Augmentation**
The dominant paradigm in the AI agent market is customer-facing: chatbots, voice agents, lead generation. open-fleet is explicitly positioned against this — it automates the *builder's own internal work*, not external interactions. This isn't a marketing differentiator; it shapes the entire architecture (no customer auth, no web UI, no multi-tenancy, single-user Slack DM as the only interface).

### Market Context & Competitive Landscape

Existing personal productivity AI tools fall into two failure modes for this use case:
- **Over-engineered** (ZeroClaw, n8n): Feature sets that create choice paralysis and setup overhead disproportionate to the problem being solved
- **Under-powered** (Zapier AI, Make.com): Cloud-dependent token costs that make daily high-volume email processing economically impractical on free or low tiers

The window for a lean, local-first, single-purpose agent is narrow: local models just became fast enough (200 t/s), but the market hasn't yet flooded with "me too" solutions targeting this specific use case.

### Validation Approach

- **Dual-LLM routing:** Validated by Week 1 — does LM Studio handle structured JSON output reliably at 85%+ accuracy? If not, Gemini becomes primary with LM Studio as optional. This is a go/no-go test, not a preference.
- **Cost model:** Validated at Week 4 — if LM Studio is primary, track actual token cost = $0 for extraction runs. If Gemini is primary, track free tier quota consumption against 5x daily runs of 200-email batches.
- **Work elimination claim:** Validated at Week 4 — 7-10 hours/week saved, measurably ahead of work on Fridays. No savings = no innovation claim to make.

### Risk Mitigation

| Innovation Risk | Mitigation |
|---|---|
| Qwen Coder structured output reliability <85% | Gemini becomes primary; LM Studio deferred to future testing |
| Gemini free tier quota exhausted by daily use | Add quota tracking; alert when approaching limit; document paid tier threshold |
| "Lean by design" becomes "too limited to use" | Scope MVP to one workflow only; validate before expanding; resist feature creep |
| Local-first positioning undermined by constant Gemini fallback | Track fallback frequency; if >20% of runs use Gemini, investigate LM Studio stability |

## API Backend Specific Requirements

### Project-Type Overview

open-fleet is a Python backend agent service with no public-facing HTTP endpoints. It uses Slack Socket Mode for inbound communication (outbound WebSocket to Slack) and makes outbound REST API calls to Gmail, LM Studio, and Gemini. The architecture is deliberately interface-agnostic — Slack is a thin adapter over a core that has no Slack dependency.

### Technical Architecture Considerations

**Interface-Agnostic Core Principle:**
All business logic (LLM routing, Gmail integration, action item extraction, response formatting) must be implemented in a core layer with no dependency on Slack. The Slack Bolt handler is a thin adapter that calls core functions and formats the result for Slack delivery. This enables future interfaces (Teams, Discord, web UI) to be added without rewriting the agent core.

```
Slack Bolt (adapter)
        ↓
Agent Core (LLM router, tool executor, response builder)
        ↓
Tools: Gmail API | LM Studio API | Gemini API
```

**Connection Model:**
- Inbound: Slack Socket Mode — persistent outbound WebSocket to Slack, no public URL, no Cloudflare tunnel required
- Outbound: Standard HTTPS REST calls to Gmail API, Gemini API, and LM Studio local HTTP server

### Authentication Model

| Service | Method | Storage | Notes |
|---|---|---|---|
| Slack (bot) | `SLACK_BOT_TOKEN` | `.env` | Bot user token for posting messages |
| Slack (socket) | `SLACK_APP_TOKEN` | `.env` | App-level token for Socket Mode connection |
| Gmail | OAuth 2.0 (refresh token) | `token.json` local file | google-auth-oauthlib flow; refresh token persisted locally |
| Gemini | `GEMINI_API_KEY` | `.env` | Google AI Studio key |
| LM Studio | None | N/A | Local HTTP, no authentication |

All secrets via `.env` file. `.env` and `token.json` in `.gitignore`. Startup validation checks all required env vars present and fails fast with specific error message if any are missing.

### Data Schemas

**Inbound — Slack event payload (simplified):**
```json
{ "type": "message", "text": "extract today's emails", "user": "U123", "channel": "D456" }
```

**Outbound — LLM structured output (required schema):**
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

All LLM responses validated against this schema before use. Invalid responses trigger one retry, then graceful failure with Slack error message.

### Rate Limits

| Service | Limit | Handling Strategy |
|---|---|---|
| Gmail API | 250 quota units/sec, 1B units/day | Batch `messages.get` calls; exponential backoff on HTTP 429 |
| Gemini free tier | 15 RPM, 1M tokens/day | Token usage logging; alert at 80% daily quota |
| LM Studio | Unlimited (local) | Timeout at 30s; treat timeout as unavailability signal |
| Slack | 1 message/sec per channel | Response buffering; split large responses across messages |

### Error Codes & Response Standards

All Slack error responses follow a consistent format:
- `⚠️` prefix for warnings (degraded operation, fallback active)
- `❌` prefix for failures (operation could not complete)
- Always include: what failed, why (if known), what the user should do next

Examples:
- `⚠️ LM Studio unavailable — retrying with Gemini...`
- `❌ Gmail authentication expired — run /refresh-auth to reconnect`
- `❌ Gmail API rate limit hit — extraction will retry in 60 seconds`

### Implementation Considerations

- **No framework lock-in** — Slack Bolt and google-api-python-client are the only significant dependencies. No LangChain, CrewAI, or agent orchestration frameworks.
- **Process management** — Single Python process. Auto-start via Windows Task Scheduler on boot. Crash recovery via scheduler restart policy.
- **Logging** — Structured logs to local file: timestamp, LLM provider used, email count, extraction duration, any errors. Minimum retention: 7 days.
- **Config validation on startup** — Check all required `.env` vars present; check LM Studio reachable; check Gmail token valid. Fail fast with actionable error before accepting any Slack commands.
- **Versioning** — Internal semver for the agent (`v0.1.0` at MVP). Pin all dependency versions in `requirements.txt`. No public API versioning needed.

## Product Scope

### MVP Strategy & Philosophy

**MVP Approach:** Problem-solving MVP — prove one workflow works reliably enough to use every day before adding anything else. The MVP is not a demo or a prototype; it is the tool Jason uses to do his actual job starting Week 1.

**Resource Requirements:** Solo developer (Jason). Nights and weekends. Target: 10-15 hours/week over 4 weeks. No external dependencies, no team coordination overhead.

**Guiding constraint:** If a feature cannot be validated by "did Jason clock out early this Friday?", it doesn't belong in Phase 1.

### MVP Feature Set (Phase 1)

**Core feature descriptions:**

- **Slack command interface** — Natural language commands (`extract today's emails`, `what's urgent today?`, `check emails since [timeframe]`). Slack Bolt Socket Mode. Response in DM within 60 seconds.
- **Gmail integration** — OAuth 2.0, read inbox for configurable timeframe (default: last 24 hours), extract subject/sender/timestamp/body. Handle multi-part emails. Pagination for 150-200 email volumes. Single Gmail account only.
- **LLM action item extraction** — Structured JSON output: action description, sender, deadline, priority (urgent/this-week/no-deadline), sentiment (neutral/frustrated/escalated). Batch processing for efficiency. Primary: LM Studio (Qwen Coder 2.5). Fallback: Gemini 1.5 Flash.
- **Formatted Slack response** — Prioritized output: 🔴 Urgent → 💬 Needs Response → ⏰ Approaching deadlines → 🟡 This week → 🟢 No deadline. Context excerpts truncated to 100 chars. Email count and timeframe in header.

**Explicitly excluded from MVP:** Asana/Monday.com integration, calendar sync, task auto-creation, team capacity, multi-user support, web UI, email sending/replying, attachment processing.

**Core User Journeys Supported:**
- Journey 1: Morning email triage (happy path) — full end-to-end
- Journey 2: Agent failure recovery (edge case) — graceful degradation with informative Slack errors
- Journey 3: Operator maintenance — startup script, OAuth token expiry alerts, `.env` validation

**Must-Have Capabilities:**

| Capability | Justification |
|---|---|
| Slack Socket Mode listener | Without this, no interface exists |
| Natural language command parsing | `extract today's emails`, `what's urgent?`, `check emails since [timeframe]` |
| Gmail OAuth 2.0 integration | Without this, no data source |
| Email fetch + pagination (150-200 emails) | Without this, the core problem isn't solved |
| LM Studio structured JSON extraction | Primary LLM path |
| Gemini fallback with auto-routing | Without this, a single LM Studio outage kills the tool |
| JSON schema validation + retry | Without this, garbled output reaches the user |
| Formatted Slack response (priority + sentiment) | Without this, output isn't actionable |
| Startup config validation (fail fast) | Without this, debugging takes 25 minutes instead of 2 |
| OAuth token expiry Slack alert | Without this, Journey 3 fails silently |
| Structured error messages (`⚠️`/`❌`) | Without this, failures are invisible |
| `.env`-based config + `.gitignore` | Without this, secrets leak to GitHub |
| Local structured logging (7-day retention) | Without this, debugging is guesswork |
| Interface-agnostic core architecture | Low-cost now, prevents expensive refactor later |

**Explicitly excluded from MVP:**
Asana/Monday.com, Google Calendar, task auto-creation, team capacity, multi-user support, web UI, email sending/replying, attachment processing, budget tracking, web dashboard.

### Post-MVP Features

**Phase 2 — Growth (Month 2-3, after Week 4 validation):**
- Asana task creation from extracted action items (pre-populated fields, assigned for review)
- Google Calendar event creation for deadlines
- Team capacity visibility via Calendar API
- Timeframe customization beyond defaults

**Phase 3 — Expansion (Month 4-6):**
- Budget tracking via Google Sheets integration
- Revenue intelligence: upsell detection, sentiment trend analysis
- Email response assistance: suggested templates, tone matching
- Multi-user deployment support (consulting client instances)

**Future Vision:**
- Multi-tool support (ClickUp, Jira, Outlook, Teams)
- Additional interface adapters (Teams, Discord, web UI)
- Web dashboard, mobile briefings

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Likelihood | Mitigation |
|---|---|---|
| Qwen Coder <85% structured output accuracy | Medium | Week 1 go/no-go test; Gemini becomes primary if fails |
| Gmail OAuth setup complexity delays Week 1 | Medium | Tackle OAuth first, before any other feature work |
| LM Studio instability on Windows | Low-Medium | Track fallback frequency; >20% Gemini use triggers investigation |
| Slack Socket Mode connection drops | Low | Slack Bolt handles reconnection automatically |

**Market Risks:**

| Risk | Mitigation |
|---|---|
| Tool saves <5 hours/week (insufficient for habit formation) | Week 2 honest assessment; pivot prompt engineering approach before Week 4 |
| Accuracy too low to trust (missing urgent emails) | Manual spot-check 10% of emails weekly for first month |

**Resource Risks:**

| Risk | Mitigation |
|---|---|
| Nights/weekends pace slower than 4 weeks | Gmail + Slack core in Week 1-2; LLM extraction in Week 2-3; polish + testing Week 4 |
| Scope creep kills MVP timeline | Hard rule: no Phase 2 features until Week 4 validation checkpoint passed |

## Functional Requirements

### Command Interface

- **FR1:** User can trigger email extraction using natural language Slack messages (e.g., `extract today's emails`, `what's urgent today?`)
- **FR2:** User can specify a custom timeframe for email extraction (e.g., `check emails since yesterday 5pm`)
- **FR3:** User can receive all agent responses directly in a Slack DM

### Email Processing

- **FR4:** Agent can authenticate with Gmail using OAuth 2.0 and maintain a persistent refresh token
- **FR5:** Agent can fetch emails from the user's Gmail inbox for a specified timeframe (default: last 24 hours)
- **FR6:** Agent can paginate Gmail results to process batches of 150-200+ emails in a single extraction run
- **FR7:** Agent can extract subject, sender, timestamp, and body text from multi-part emails (HTML and plain text)
- **FR8:** Agent can handle Gmail API rate limit errors by retrying with exponential backoff and notifying the user of any resulting delay

### Action Item Extraction

- **FR9:** Agent can identify explicit action requests within email content (requests, approvals, deliverables)
- **FR10:** Agent can identify implicit action items (questions requiring response, pending decisions)
- **FR11:** Agent can extract deadlines from email content, both explicit ("by EOD Friday") and implied ("urgent", "ASAP")
- **FR12:** Agent can classify each action item by priority tier (urgent, this week, no deadline)
- **FR13:** Agent can detect and classify email sender sentiment (neutral, frustrated, escalated)
- **FR14:** Agent can batch-process multiple emails in a single LLM inference call

### LLM Routing & Reliability

- **FR15:** Agent can route extraction requests to LM Studio as the primary LLM provider
- **FR16:** Agent can automatically fall back to Gemini when LM Studio is unavailable or exceeds the response timeout
- **FR17:** Agent can validate LLM output against a required JSON schema before use
- **FR18:** Agent can retry a failed or invalid LLM response once before escalating to graceful failure
- **FR19:** Agent can log which LLM provider handled each extraction run

### Response Delivery

- **FR20:** Agent can deliver a formatted Slack response with action items grouped by priority tier (🔴 Urgent → 💬 Needs Response → ⏰ Approaching deadline → 🟡 This week → 🟢 No deadline)
- **FR21:** Agent can include sender, timestamp, and a context excerpt (max 100 characters) for each action item
- **FR22:** Agent can report the total email count and timeframe scanned in the response header
- **FR23:** Agent can split responses that exceed Slack's message size limit across multiple sequential messages
- **FR24:** Agent can deliver structured error notifications to the user when any operation fails, using consistent `⚠️`/`❌` formatting with actionable next steps

### System Health & Operations

- **FR25:** Agent can validate all required configuration values at startup and halt with specific, actionable error messages if any are missing or invalid
- **FR26:** Agent can detect Gmail OAuth token expiry and notify the user via Slack at least 3 days before the token expires
- **FR27:** Agent can start automatically on system boot without manual terminal intervention
- **FR28:** Agent can write structured logs for each extraction run (provider used, email count, duration, errors)
- **FR29:** Agent can monitor Gemini free tier quota usage and alert the user when approaching the daily limit

### Security & Configuration

- **FR30:** User can configure all credentials and service settings via a `.env` file without modifying source code
- **FR31:** Agent can store Gmail OAuth refresh tokens in a local file, outside of source code and version control
- **FR32:** Agent can process email content through the local LLM provider without transmitting data externally when LM Studio is active
- **FR33:** Agent can discard raw email body content after each extraction run without writing it to persistent storage

## Non-Functional Requirements

### Performance

- **NFR1:** End-to-end extraction response time (Slack command received → Slack response delivered) must not exceed 60 seconds for batches of up to 200 emails under normal operating conditions.
- **NFR2:** LM Studio inference requests must complete within 30 seconds; requests exceeding this threshold are treated as a timeout and trigger the Gemini fallback path.
- **NFR3:** Gmail fetch and parse operations must complete within 20 seconds to preserve the overall 60-second response budget.
- **NFR4:** Response time must not exceed the 60-second ceiling defined in NFR1 regardless of batch size — processing 200 emails must complete within the same budget as 50 emails.

### Security

- **NFR5:** All credentials (Slack tokens, Gmail OAuth tokens, Gemini API key) must be stored in `.env` and excluded from version control via `.gitignore`. No credentials may appear in source code.
- **NFR6:** Gmail OAuth refresh tokens must be stored in a local `token.json` file outside the source tree and excluded from version control.
- **NFR7:** Raw email body content must not be written to disk at any point during or after an extraction run.
- **NFR8:** When LM Studio is the active provider, email content must not leave the local machine. When Gemini is active, email content must be transmitted only over HTTPS to Google's API endpoints.
- **NFR9:** The agent must not expose any inbound network ports. All external communication is outbound-only (Slack Socket Mode WebSocket, Gmail HTTPS, Gemini HTTPS, LM Studio localhost).

### Reliability

- **NFR10:** The agent must achieve 95%+ availability during the user's working hours (Monday–Friday, 7am–6pm local time), measured as the proportion of days the agent is responsive to Slack commands at start of business.
- **NFR11:** The agent process must restart automatically after a crash within 60 seconds, without manual intervention, via the OS-level task scheduler.
- **NFR12:** LLM provider failover from LM Studio to Gemini must be automatic and require no user action. The user must be notified via Slack when failover occurs.
- **NFR13:** A failed extraction must never deliver a partial or malformed response to the user. The outcome of any extraction run is either a complete valid response or a clearly formatted error message — no silent partial results.
- **NFR14:** The agent must maintain 7 days of structured local logs sufficient to diagnose any failure without requiring reproduction of the failure condition.

### Architecture

- **NFR15:** The Slack Bolt framework must not be imported or referenced in any module outside the interface adapter layer. Agent core, LLM routing, Gmail integration, and response formatting modules must have zero Slack dependency.
- **NFR16:** All core extraction functions must accept and return interface-agnostic data types — primitive values and plain collections — with no Slack-specific, framework-specific, or interface-specific objects.
- **NFR17:** Adding a new interface adapter (e.g., Teams, Discord) must require no modifications to any existing core, LLM, or tool module — only the creation of a new adapter module.
