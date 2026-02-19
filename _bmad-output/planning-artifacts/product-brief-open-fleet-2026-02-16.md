---
stepsCompleted: [1, 2, 3, 4, 5]
inputDocuments: []
date: 2026-02-16
author: Jason
---

# Product Brief: open-fleet

## Executive Summary

**open-fleet** is a lean, local-first AI agent that enables tech-savvy business owners and consultants to automate real workflow tasks through Slack, powered by local LLM models (LM Studio) or cloud LLMs (Gemini). Unlike expensive cloud-based AI solutions or superficial chatbots, open-fleet eliminates actual work—Gmail email processing, Asana task management, Google Calendar scheduling, customer profiling, and data reporting—at zero or minimal token costs.

Built as both a **portfolio piece** demonstrating deep AI agent architecture expertise and a **consulting service foundation**, open-fleet proves what's possible with local models, positioning consultants as high-value, low-cost alternatives to premium AI agencies selling "AI theatre."

**Two-Pronged Strategy:**
1. **Phase 1 (Portfolio MVP):** Prove technical capability with working integrations (Gmail + Asana + Google Calendar), create demo videos and GitHub repo to land consulting opportunities or employment
2. **Phase 2 (Consulting Service):** Deploy and customize for clients as professional service ("I can implement this for you" or "I can teach you how"), not sold as SaaS

---

## Core Vision

### Problem Statement

Small businesses and solo consultants face three critical barriers to AI adoption:

1. **Prohibitive costs** - Hundreds of dollars monthly in API fees force users to free tiers or abandonment
2. **Trust and privacy concerns** - Cloud-based AI handling sensitive business data creates security risks
3. **Market saturation with "AI theatre"** - Expensive, superficial solutions (chatbots, voice agents) that add channels rather than eliminate work

Current AI agency offerings charge premium prices ($5k-$50k+) for glorified website chatbots and IVR systems, while real workflow automation remains out of reach for budget-constrained businesses.

### Problem Impact

**For Solo Consultants & Developers:**
- Forced to use limited free tiers or pay $500+/month in API costs
- Cannot compete with well-funded AI agencies
- Lack portfolio pieces demonstrating deep AI agent expertise
- Need practical solutions to launch consulting practices

**For Tech-Savvy Business Owners:**
- Drowning in repetitive manual tasks (20-60 minutes each) that could be automated
- Want AI workflow improvements but lack time to implement
- Willing to invest in hardware ($3k) to avoid recurring cloud costs
- Value privacy and local control over vendor lock-in
- Distrust expensive AI agencies selling hype over substance

**Market Gap:**
- Enterprise solutions priced beyond small business budgets
- No accessible path between free tiers and $50k custom builds
- Existing tools focused on external (customer) AI, not internal (workflow) AI

### Why Existing Solutions Fall Short

**ZeroClaw & Complex Platforms:**
- Feature-rich but overwhelmingly complex (7+ chat apps, 22+ AI providers, 4+ tunnel options)
- Choice paralysis and steep learning curve
- Over-engineered for small business needs
- Requires significant setup and configuration expertise

**Cloud AI Platforms (n8n, Make.com, Zapier AI):**
- Expensive recurring token fees ($100-$500+/month)
- Privacy concerns with sensitive business data in cloud
- Vendor lock-in and API dependencies
- Limited customization for specific workflows

**AI Agency Custom Solutions:**
- Premium pricing ($5k-$50k+) for superficial implementations
- Focus on customer-facing chatbots and lead generation
- "Business as usual with a new messaging service"
- Don't transform internal workflows or eliminate actual work

**Framework-Based Solutions (LangChain, CrewAI):**
- Heavy dependencies and complexity
- Over-abstraction for simple use cases
- Harder to debug and customize
- Learning curve reduces speed to value

### Proposed Solution

**open-fleet** is a deliberately lean, local-first AI agent built with custom Python scripts that integrate with Slack via Cloudflare tunnel. It maintains the sophisticated agent loop—memory recall, LLM reasoning, tool execution, response generation—from enterprise solutions while stripping unnecessary complexity and framework dependencies.

**Technical Architecture (MVP - Phase 1):**
- **Agent Loop:** Custom Python script (no framework dependencies)
- **LLM Options:** LM Studio (Qwen Coder, 200 t/s, local) or Google Gemini (cloud, free tier)
- **Interface:** Slack (single chat app, where businesses already work)
- **Tunnel:** Cloudflare (reliable, secure, free tier)
- **Integrations:** Gmail API, Asana API, Google Calendar API
- **Memory:** Keyword-based search with SQLite (simple, effective)
- **Security:** Basic sandbox and error handling

**Current Progress:**
- ✅ Proven: Slack → Python → Ollama → Slack response loop working
- ✅ Existing: Python agent script with tool calling (currently using Gemini)
- 🔄 Testing: Qwen Coder function calling reliability on LM Studio
- 📋 Next: Gmail and Asana integration

**Killer Use Cases (MVP):**
1. 📧 **Gmail Processing** - "Find all emails from acme@corp.com this month and summarize action items"
2. 📊 **Asana Task Management** - "Create Asana tasks from today's email action items"
3. 📅 **Calendar Coordination** - "Block time on my calendar for all Asana task deadlines"

**Future Enhancements (Phase 2):**
4. 👤 **Customer Profiling** - Aggregate customer interactions in Notion database
5. 📋 **SOP Documentation** - Generate and maintain standard operating procedures in Notion
6. 📈 **Data Reporting** - Compile business insights from local SQLite database

Each automation runs through natural language Slack commands, eliminating 20-60 minutes of manual work per task.

### Key Differentiators

**Technical Advantages:**
1. 💻 **Zero/Low Token Costs** - Local LM Studio (200 t/s) = unlimited automation after hardware, or Gemini free tier for cloud option
2. 🔒 **Privacy-First** - Business data can stay on local network with LM Studio option
3. ⚡ **Performance** - 200 tokens/second proves local models are production-capable
4. ✂️ **Lean by Design** - Single path (Slack + Cloudflare + LM Studio/Gemini) eliminates choice paralysis
5. 🛠️ **No Framework Lock-in** - Custom Python scripts, fully controllable and debuggable

**Business Advantages:**
6. 🎯 **Work Elimination Focus** - Automates real internal tasks, not just customer-facing chatbots
7. 💰 **High Value, Low Cost Model** - Consultant-friendly vs. premium AI agency pricing
8. 🤝 **Tech-Savvy Target** - Built for technical business owners who understand and appreciate the architecture
9. 📱 **Multiple Demo Formats** - Cell phone social proof, polished screen recordings, live Zoom demos

**Personal/Consulting Advantages:**
10. 📚 **Portfolio Proof** - Demonstrates deep AI agent architecture expertise to employers and clients
11. 🎓 **Learning Vehicle** - Master AI agent patterns, API integrations, LLM orchestration through building
12. 🚀 **Business Foundation** - Launchpad for AI consulting practice serving underserved market
13. 💼 **Dual Revenue Path** - "Implement for you" or "Teach you how" consulting services

**Market Timing:**
- Local models (Qwen Coder, Llama, Mistral) finally fast enough for production use (200 t/s)
- AI hype peaked, businesses demand ROI over theatre
- Small businesses frustrated with expensive agency solutions that don't deliver
- Tech-savvy founders looking for privacy-preserving, cost-effective AI automation
- Opportunity window before market floods with "me too" solutions

---

## Target Users

### Primary User: The Drowning Account Manager

**Persona: "Jordan" (Based on Real User Experience)**

**Role & Context:**
- Account Manager at agency/consultancy managing 18+ active clients
- Team: 2 remaining direct reports (recently lost 4 team members to turnover, no replacements)
- Daily volume: 150-200 emails, 30-50 tasks to update in Monday.com
- Responsibilities: Client communication, task delegation, calendar management, budget tracking (Google Sheets), team load balancing
- **Current state:** Weeks behind on deliverables, constantly firefighting, drowning in manual administrative work

**Problem Experience:**

*Current Daily Hell:*
- **7am-8am:** Wake up to 80+ unread emails from 18 clients
- **8am-5pm:** Triage 200 emails while trying to complete actual work
- **Manual overhead:** 2-3 hours/day copying email action items into Monday.com tasks (30-50 times/day)
- **Team coordination:** Constantly fielding "What should I work on?" questions while buried in email
- **Deadline chaos:** Missing deliverables because no time to proactively track approaching deadlines
- **Budget blindness:** Google Sheets time tracking neglected, leading to budget overruns and billing issues
- **Nights/Weekends:** Working overtime to catch up on admin work that should be automated

*Emotional Impact:*
- Constant anxiety about what's being forgotten or missed
- Guilt about being weeks behind on client deliverables
- Frustration that 60% of time is spent on admin work instead of strategic client value
- Stress from operating in permanent "firefighting mode" rather than proactive management
- Fear of client churn due to missed deadlines and slow response times
- Burnout from unsustainable workload with no relief in sight

*Current Workarounds (Barely Surviving):*
- Working nights and weekends to catch up on email backlog
- Triaging email by sender name (VIP clients get attention first, others get delayed)
- Letting lower-priority tasks fall through the cracks and hoping clients don't notice
- Manual task assignment without considering team capacity (leading to team member burnout)
- Reactive deadline management (only addressing deadlines when clients ask "Where is this?")
- Relying on team members to remind about forgotten commitments

**Success Vision (MVP - Email Extractor):**

*The "Aha!" Moment (Simplified for Phase 1):*

Jordan opens Slack Monday morning at 7am and types: **"Extract today's emails"**

The agent responds in 30 seconds:
```
📧 Scanned 187 emails from last 24 hours

Found 14 action items:

🔴 URGENT (Due today):
• Client Acme Corp: Review proposal draft before EOD
  From: Sarah Johnson, 9:42am
  Context: "Need your feedback by 5pm for board meeting tomorrow"

• Client Beta Inc: Approve Q2 budget allocation
  From: Mike Chen, 11:15am
  Context: "Finance needs approval today to process"

🟡 THIS WEEK:
• Client Gamma LLC: Schedule Q2 planning call
  From: Jennifer Martinez, 2:34pm, Due: Friday

• Client Delta Systems: Send weekly status update
  From: Tom Anderson, 4:02pm, Due: Thursday

• Client Echo Partners: Provide revised timeline for Phase 2
  From: Rebecca Kim, 3:45pm, Due: Wednesday

[9 more items with details...]

💬 NEEDS RESPONSE (Urgent tone detected):
• Client Echo Partners: Frustrated about 2-week delay
  From: Lisa Thompson, 3:18pm
  Tone: Escalated - recommend phone call before email response
  Key phrase: "This is the third time we've had to push this back"

• Client Zeta Corp: Requesting emergency meeting
  From: David Park, 5:02pm
  Tone: Urgent - needs immediate attention
```

**Result:**
- **Time saved:** 1.5-2 hours that would have been spent manually reading 187 emails
- **Nothing missed:** All 14 action items surfaced, prioritized by urgency
- **Emotional intelligence:** Flagged frustrated client for proactive call
- **Immediate action:** Can tackle urgent items first, delegate rest to team

**What Makes Them Convert:**
- **Day 1:** Agent finds 12 action items from 200 emails in 30 seconds - immediate "holy shit" moment
- **Week 1:** Saves 7-10 hours of email triage, can finally focus on strategic work
- **Week 2:** Agent alerts about approaching deadline that was completely forgotten - saves client relationship
- **Week 3:** Team notices Jordan is less stressed, more proactive, responding faster
- **Week 4:** Can't imagine starting the day without email extraction - "This tool saved my job"
- **Month 2:** Recommends to colleagues - "You NEED this"

**Demographics & Characteristics:**
- **Age:** 28-45 years old
- **Background:** Often has project management or technical background, understands tools and automation
- **Tech comfort:** Uses Slack daily, comfortable with Monday.com/Asana, willing to try new productivity tools
- **Pain threshold:** CRITICAL - actively drowning in work, needs solution urgently
- **Budget:** Will invest $3k in hardware if it saves 10+ hours/week, OR pay $500-$5000 for done-for-you setup
- **Privacy needs:** Moderate - client emails contain sensitive information but not HIPAA-level compliance required
- **Time availability:** Limited - needs quick wins, can't spend weeks learning complex tools

---

### Expanded Market: Beyond Account Managers

**Discovery from User Validation:**
> "Even my boss has to do things that are shaped like this, so I think if it works for me it could work up and down the company ladder."

While Account Managers are the primary persona, open-fleet serves **anyone managing email + tasks + people coordination:**

**Team Leads & Department Heads:**
- Managing 5-15 direct reports
- 100-150 emails/day
- Task delegation, deadline tracking, budget oversight
- Same pain: too much coordination overhead, not enough time for strategic work

**Project Managers:**
- Managing multiple concurrent projects across different clients/stakeholders
- Similar pain: email overload, task tracking across tools, deadline management
- Use case: Automated project status updates, resource allocation visibility, deadline alerting

**Customer Success Managers:**
- Managing 15-30 customer accounts, ensuring retention and growth
- Similar pain: customer communication volume, account health tracking, renewal deadline awareness
- Use case: Customer sentiment analysis, proactive outreach timing, engagement pattern recognition

**Executives (Directors, VPs):**
- High email volume, multiple team coordination, strategic decisions buried in tactical noise
- Need: Triage urgent decisions, delegate operational tasks, maintain visibility without drowning in details
- Use case: Executive briefing, priority decisions extraction, team capacity overview

**Characteristics Across All Segments:**
- Same core problem: Too many stakeholders, too much communication, not enough time
- Same manual overhead: Email → Task creation, calendar management, status tracking
- Same need: Automated triage, intelligent delegation, proactive alerting
- **Adoption path:** Discover through word-of-mouth from account managers who found success

---

### Secondary Users

**Implementation Partners (Consultants Installing for Clients):**
- Solo consultants or small agencies offering open-fleet as a service
- Use the DIY version for themselves, offer DWY/DFY to clients
- Value: Revenue stream, client retention, differentiation from competitors

**Developer Community (Open Source Contributors):**
- Developers who fork GitHub repo and extend functionality
- Add integrations (Asana, Outlook, Teams, etc.)
- Contribute features, fix bugs, improve documentation
- Value: Learning, portfolio, solving their own adjacent problems

---

### User Journey

**Phase 1: Discovery (Crisis Moment)**
- **Trigger:** Major deadline missed, client escalation, team burnout, or realization "I can't keep doing this"
- **Search behavior:**
  - "AI automation for account managers"
  - "automate email to Monday.com"
  - "AI assistant for project management"
  - "how to manage 200 emails per day"
- **Discovery channels:**
  - LinkedIn post from Jason showing real demo
  - GitHub repo via search (starred by others in similar pain)
  - Referral from colleague: "Try this tool, it saved my sanity"
  - Blog post/YouTube: "How I automated 10 hours/week of account management work"
  - Reddit/HackerNews: Discussion thread about productivity tools

**Phase 2: Evaluation (First Contact)**
- **Watches demo video:** Sees real Slack conversation → agent extracts 14 action items from 187 emails in 30 seconds
- **Key questions:**
  - "Can this work with MY tools?" (Monday.com? Asana? Gmail? Outlook?)
  - "Is this too technical for me to set up?"
  - "How much does it cost?"
  - "What if it breaks or makes mistakes?"
- **Decision drivers:**
  - Sees someone like them (account manager, PM) using it successfully
  - Clear ROI: 10 hours/week saved = $400-$1000/week value (at $40-$100/hour)
  - Multiple setup options (DIY free, DWY $500-$1500, DFY $2500-$5000)
  - "If they can do it, I can do it" confidence

**Phase 3: Onboarding (First Use)**

**Setup Path Options:**

*DIY (Do It Yourself) - Technical Users:*
- Watches 60-minute setup video
- Follows written documentation
- Connects: Gmail API → Monday.com API → Slack → Cloudflare tunnel → LM Studio
- Troubleshoots with community Discord/GitHub issues
- **Time investment:** 2-4 hours
- **Cost:** Free (hardware cost for LM Studio if local, or Gemini free tier)

*DWY (Done With You) - Semi-Technical Users:*
- Books 1-hour Zoom session with Jason (or consultant)
- Screen-share walkthrough of entire setup process
- Gets personalized help with API credentials, OAuth, configuration
- Receives 1-week of troubleshooting support
- **Time investment:** 1-2 hours (mostly watching)
- **Cost:** $500-$1500

*DFY (Done For You) - Busy Executives/Non-Technical:*
- Consultant does entire setup remotely
- Customizes to their specific tools (Monday vs. Asana, Gmail vs. Outlook)
- Trains user + team on how to use commands
- Provides 30-day support + maintenance
- **Time investment:** 30 minutes (onboarding call)
- **Cost:** $2500-$5000

**First Command:**
- Slacks: `extract today's emails` at 7am Monday morning
- Waits nervously for 30 seconds
- Agent responds with prioritized action items, flagged urgent emails, sentiment analysis

**"Aha!" Moment:**
- "Holy shit, it found 3 action items I would have completely missed"
- "This just saved me 2 hours of reading email"
- "It even noticed the frustrated client tone - I need to call them ASAP"
- **Emotional shift:** Relief → Hope → "This might actually work"

**Phase 4: Adoption (Daily Habit Formation)**
- **Week 1:** Uses email extraction daily, marvels at time savings
- **Week 2:** Starts trusting agent's action item detection, reduces manual email reading by 80%
- **Week 3:** Team members notice: "You're responding faster, seem less stressed, hitting deadlines"
- **Week 4:** Morning email extraction becomes non-negotiable ritual - "I can't start my day without this"
- **Habit formed:** Like morning coffee, email extraction is now part of daily routine

**Phase 5: Expansion (Power User Evolution)**
- **Month 2:** Requests additional features (Monday task creation, calendar sync - Phase 2)
- **Month 3:** Shares with colleagues: "You NEED to see this tool"
- **Month 4:** Explores customization: custom commands for specific clients ("summarize Acme Corp status")
- **Month 6:** Becomes advocate - writes LinkedIn post, refers other AMs, provides testimonial

**Phase 6: Long-term Value (Retention & Advocacy)**
- **Ongoing reliance:** Daily email extraction is foundational to workflow
- **Expansion:** As features add (task creation, calendar sync), dependency deepens
- **Team adoption:** Other team members request access
- **ROI calculation:** "I save 10 hours/week × $50/hour = $500/week value. Worth every penny."
- **Active advocacy:** Refers 3-5 other account managers/PMs over 6 months
- **Feature requests:** Provides feedback for Phase 2+ features (budget alerts, upsell recommendations)

**Success Metrics (User-Level):**
- **Time saved:** 10-15 hours/week on manual email triage (Week 1: 7-10 hours, expands with additional features)
- **Stress reduction:** Measurable decrease in overtime hours, weekend work, anxiety about missed items
- **Deadline performance:** 95%+ on-time delivery (up from 60-70% pre-automation)
- **Team health:** Better load balancing prevents team member burnout
- **Client satisfaction:** Faster response times, proactive communication, fewer escalations
- **Career impact:** Promotion or job security due to improved performance and capacity to take on more clients

---

## Success Metrics

### User Success Metrics (Primary User: Account Manager)

**Core Outcome: Time Savings**
- **Target:** Save 10-20 hours/week on email triage and task management
- **Measurement Method:**
  - **Before automation:** 2-3 hours/day manually reading 200 emails and creating Monday.com tasks = 10-15 hours/week
  - **After automation (MVP):** 15-30 minutes/day reviewing agent-extracted action items = 1.5-2.5 hours/week
  - **Net time savings:** 8-12.5 hours/week (conservative estimate)
- **Success threshold:** Achieving 10+ hours/week savings consistently
- **Validation:** Weekly time tracking comparison (before vs. after)

**Core Outcome: Deadline Performance**
- **Target:** 100% improvement in meeting deadlines
- **Measurement Method:**
  - **Baseline:** 60-70% on-time delivery (missing 3-4 deadlines/week out of 10 total)
  - **Post-automation:** 95%+ on-time delivery (missing 0-1 deadlines/week)
  - **Improvement calculation:** From 6-7 out of 10 deliverables on-time → 9.5-10 out of 10
- **Success threshold:** Achieving 95%+ on-time delivery for 4 consecutive weeks
- **Validation:** Weekly deadline tracking, client feedback

**Core Outcome: Stress Reduction & Confidence**
- **Target:** Feel confident going into client meetings and internal team meetings
- **Measurement Method:**
  - **Qualitative:** "I know what's urgent, what's handled, and what needs attention"
  - **Quantitative:** Reduce weekend/overtime work from 8-10 hours/week to 0-2 hours/week
  - **Behavioral:** Stop Sunday night "panic catch-up" sessions
- **Success threshold:** 2+ consecutive weeks without weekend work, positive feedback in meetings
- **Validation:** Weekly self-assessment, manager/client feedback

**Core Outcome: Team Efficiency**
- **Target:** Team members have what they need when they need it - no more waiting on AM/PM
- **Measurement Method:**
  - **Before:** Team asks "What should I work on?" 5-10 times/day, blocks workflow
  - **After:** Team asks 0-2 times/day, proactive task assignment and clarity
  - **Team capacity visibility:** Ali at 60% capacity, Mo at 85% capacity (data-driven assignment)
- **Success threshold:** Reduce "What should I work on?" interruptions by 80%+
- **Validation:** Team member feedback, task assignment tracking

**Behavioral Indicators (Value Realization):**
- ✅ Uses email extraction every morning (daily habit formed)
- ✅ Stops manually reading all 200 emails/day (trust in agent accuracy)
- ✅ Shares tool with colleagues ("You need to try this")
- ✅ Recommends to other account managers/PMs in network
- ✅ Requests additional features (indicating deep integration into workflow)

---

### Business Objectives

**Minimum Viable Success (12-Month Horizon):**

Jason has defined clear business success criteria that balance personal impact, professional growth, and market validation:

1. ✅ **Saved my job** - Open-fleet prevents drowning, ensures job security through improved performance
2. ✅ **Got 1 consulting client** - Proven business model, someone paid for implementation/training
3. ✅ **Got multiple job offers** - Portfolio piece demonstrates expertise, opens career opportunities

These objectives reflect a pragmatic approach: the tool must first solve the creator's immediate crisis (job security), then validate as a consulting service (market proof), and finally serve as a career accelerator (portfolio value).

**Phase 1: Save My Job (Week 1-8)**

*Objective: Stabilize current role through productivity gains*

**Success Criteria:**
- Email extraction used daily for 4+ consecutive weeks without skipping
- Zero missed deadlines for 2 consecutive weeks (first time in months)
- Manager or clients notice improvement ("You're really on top of things lately")
- Workload manageable without weekend/night work (8-10 hours/week reduction)

**Key Milestones:**
- Week 1-2: Email extractor working reliably, finding 80%+ of action items
- Week 3-4: Daily habit formed, first deadline hit that would have been missed
- Week 5-6: Manager feedback: "Performance has improved"
- Week 7-8: Job security achieved, stress measurably reduced

**Metric:** Job performance rated "meeting/exceeding expectations" vs. previous "struggling to keep up"

---

**Phase 2: Portfolio Validation (Month 2-3)**

*Objective: Demonstrate technical capability and generate interest*

**Success Criteria:**
- GitHub repo published with comprehensive README, demo video, setup documentation
- LinkedIn post about the tool generates engagement (50+ reactions, 10+ meaningful comments)
- Demo video reaches 100+ views (LinkedIn, YouTube, Twitter)
- 3-5 conversations with interested account managers, PMs, or potential clients
- First consulting inquiry (even if doesn't immediately convert)

**Key Deliverables:**
- GitHub repo: Clean code, documentation, setup guide, demo video embedded
- LinkedIn post: "How I automated 10 hours/week of account management work"
- Demo video: 2-3 minutes showing real Slack interaction → agent response → time saved
- Blog post or Twitter thread: Technical walkthrough and lessons learned

**Metric:** Portfolio piece generating measurable interest and conversation

---

**Phase 3: First Consulting Client (Month 3-6)**

*Objective: Validate business model and service delivery capability*

**Success Criteria:**
- 1 paid consulting engagement successfully delivered (DWY or DFY service tier)
- Target revenue: $500-$5,000 depending on service complexity (DWY vs. DFY)
- Client successfully using tool, reports time savings (testimonial obtained)
- Implementation completed within promised timeframe
- Client satisfaction: Would recommend to others

**Service Tiers Validated:**
- **DWY (Done With You):** $500-$1,500 - 1-hour setup session, personalized onboarding, 1-week support
- **DFY (Done For You):** $2,500-$5,000 - Full remote setup, customization, training, 30-day support

**Key Milestones:**
- Month 3: First consulting inquiry converted to paid engagement
- Month 4: Client setup completed, tool in daily use
- Month 5: Client reports 8+ hours/week time savings
- Month 6: Client testimonial obtained for future marketing

**Metric:** $500+ consulting revenue + successful client outcome

---

**Phase 4: Job Offers (Month 3-12)**

*Objective: Leverage portfolio piece to unlock better career opportunities*

**Success Criteria:**
- 3+ job interviews where open-fleet is mentioned as a key differentiator
- 2+ job offers at target salary range (indicating market value increase)
- Interviewers ask "Tell me more about this AI agent project you built"
- Portfolio piece demonstrates: AI/LLM expertise, systems thinking, API integration, product development

**Interview Talking Points:**
- "I built this to solve my own problem as an account manager drowning in 200 emails/day"
- "Demonstrates Python, LLM integration, API orchestration (Gmail, Monday.com, Slack)"
- "Validated as consulting service - already have paying clients"
- "Proves I can identify problems, build solutions, and deliver value"

**Key Outcomes:**
- Job offers with 10-20% salary increase over current role
- Roles highlighting AI/automation expertise
- Opportunities to build similar internal tools for new employer
- Option to continue consulting on the side

**Metric:** Multiple job offers leveraging open-fleet as portfolio proof

---

### Key Performance Indicators (KPIs)

**User Success KPIs (Own Usage - Primary Validation)**

| KPI | Baseline | Target | Timeline | Measurement |
|-----|----------|--------|----------|-------------|
| **Time saved per week** | 0 hours | 10-20 hours | Week 4+ | Weekly time tracking |
| **Emails manually read** | 200/day (100%) | 20-40/day (10-20%) | Week 2+ | Daily email volume |
| **Deadline hit rate** | 60-70% | 95%+ | Week 6+ | Weekly deadline tracking |
| **Weekend work hours** | 8-10 hours | 0-2 hours | Week 8+ | Weekly time log |
| **Team interruptions** | 5-10/day | 0-2/day | Week 4+ | Daily interruption count |
| **Daily usage (habit)** | N/A | 6-7 days/week | Week 2+ | Slack command logs |

**Business Success KPIs (Portfolio & Consulting)**

| KPI | Target | Timeline | Measurement |
|-----|--------|----------|-------------|
| **GitHub repo stars** | 25+ | Month 3 | GitHub analytics |
| **Demo video views** | 100+ | Month 3 | YouTube/LinkedIn analytics |
| **LinkedIn post engagement** | 50+ reactions, 10+ comments | Month 2 | LinkedIn analytics |
| **Consulting inquiries** | 3-5 | Month 3-6 | Conversation tracking |
| **Paid consulting clients** | 1+ | Month 6 | Revenue tracking |
| **Consulting revenue** | $500-$5,000 | Month 6 | Financial records |
| **Job interviews (mentioning project)** | 3+ | Month 6-12 | Interview tracking |
| **Job offers received** | 2+ | Month 12 | Offer tracking |

**Technical Performance KPIs (Product Quality)**

| KPI | Target | Timeline | Measurement |
|-----|--------|----------|-------------|
| **Email action item accuracy** | 85%+ | Week 2 | Manual validation sample |
| **Agent response time** | <60 seconds | Week 1 | Slack timestamp logs |
| **Daily uptime** | 95%+ | Week 4+ | Monitoring logs |
| **False positives (incorrect tasks)** | <10% | Week 4 | Manual review |
| **Missed urgent emails** | 0 per week | Week 2+ | Post-review verification |

---

### Leading Indicators (Early Success Signals)

Leading indicators predict future success and allow for early course correction:

**Week 1-2: Technical Validation**
- ✅ Agent successfully extracts action items from 80%+ of emails (accuracy threshold)
- ✅ Time savings: 1+ hour/day in email triage (immediate ROI)
- ✅ Zero critical emails missed (trust building)
- ✅ Agent response time consistently under 60 seconds (usability)
- 🚩 **Red flag:** <70% accuracy or >2 minutes response time (indicates LLM or API issues)

**Week 3-4: Habit Formation**
- ✅ Daily habit formed - use email extraction every morning without fail
- ✅ Team notices faster response times ("You're getting back to us quicker")
- ✅ First deadline hit that would have been missed without automation
- ✅ Reduction in "What should I work on?" interruptions
- 🚩 **Red flag:** Skipping days or reverting to manual email reading (indicates insufficient value)

**Month 2: Market Validation**
- ✅ Show demo to 3-5 colleagues
- ✅ At least 1 person says "I need this, can you help me set it up?"
- ✅ GitHub repo gets 10+ stars organically (without paid promotion)
- ✅ LinkedIn post generates engagement beyond immediate network
- 🚩 **Red flag:** Zero interest from others (indicates solution too specific or demo ineffective)

**Month 3: Business Traction**
- ✅ First consulting inquiry (even if doesn't convert immediately)
- ✅ Job application mentions open-fleet in cover letter as key project
- ✅ Tool becomes non-negotiable part of workflow (can't work without it)
- ✅ Colleagues asking for referrals or recommendations
- 🚩 **Red flag:** No consulting inquiries or interview interest (indicates weak positioning/marketing)

**Month 6: Sustainability Check**
- ✅ Still using tool daily (hasn't been abandoned)
- ✅ At least 1 consulting client successfully onboarded
- ✅ Portfolio generating interview opportunities
- ✅ Considering feature additions (Phase 2) based on real usage
- 🚩 **Red flag:** Tool abandoned, no consulting traction, no interview mentions (indicates pivot needed)

---

### Success Metric Alignment

**How User Success Drives Business Success:**

```
User Success (Jason saves 10-20 hours/week)
    ↓
Authentic Portfolio Story ("I built this to solve my own drowning")
    ↓
Credibility with Other AMs/PMs ("If it works for him, it'll work for me")
    ↓
Consulting Opportunities (DWY/DFY service engagements)
    ↓
Revenue + Testimonials
    ↓
Stronger Portfolio Piece
    ↓
Job Offers (Demonstrated AI expertise + business impact)
```

**Critical Dependency:** If the tool doesn't solve Jason's own problem first, the entire business model collapses. User success IS business success in this model.

**Validation Loop:**
1. Build MVP (Email Extractor)
2. Use daily and measure time savings
3. Achieve 10+ hours/week savings (user success)
4. Document results and create demo
5. Share publicly (portfolio validation)
6. Convert interest to consulting engagement (business success)
7. Use client success as testimonial (amplify credibility)
8. Leverage portfolio for job opportunities (career success)

Each phase builds on the previous, creating a compounding success effect.

---

## MVP Scope

### Core Features (Phase 1: Email Action Item Extractor)

**Timeline:** 4 weeks (nights/weekends, 10-15 hours/week)

**Primary Objective:** Prove the core value proposition by solving the most painful problem - drowning in 200 emails/day with no systematic way to extract action items.

---

**Feature 1: Slack Command Interface**

**Description:**
Simple, intuitive Slack-based command interface for triggering email extraction and receiving results.

**User Commands:**
- `extract today's emails` - Scans last 24 hours
- `what's urgent today?` - Scans and prioritizes by urgency
- `check emails since [timeframe]` - Custom timeframe (e.g., "since yesterday 5pm")

**Response Format:**
- Delivered as formatted Slack message in DM or designated channel
- Uses Slack markdown for visual hierarchy (bold, emoji, bullets)
- Clickable email links where possible (Gmail deep links)

**Technical Implementation:**
- Slack Bolt framework (Python)
- Slash commands or message parsing
- Response within 60 seconds of command
- Error handling with user-friendly messages

---

**Feature 2: Gmail Integration**

**Description:**
Connects to user's Gmail account via OAuth, reads emails from specified timeframe, extracts relevant data for LLM analysis.

**Scope:**
- **Included:**
  - OAuth 2.0 authentication (Google Cloud Console setup)
  - Read emails from inbox (last 24 hours default)
  - Filter by sender, date, labels (optional refinements)
  - Extract: subject, sender, timestamp, body text
  - Handle multi-part emails (HTML + plain text)

- **Not Included (MVP):**
  - Multiple email account support (single Gmail only)
  - Outlook/Exchange integration
  - Email sending/replying
  - Email filtering beyond timeframe
  - Attachment processing

**Technical Implementation:**
- Gmail API (`google-api-python-client`)
- OAuth token storage and refresh handling
- Pagination for large email volumes (>100 emails/day)
- Rate limit awareness (Gmail API quotas)

---

**Feature 3: LLM Action Item Extraction**

**Description:**
Uses local LLM (LM Studio with Qwen Coder) or cloud LLM (Gemini free tier) to analyze email content and extract structured action items.

**LLM Processing:**
- **Input:** Email subject + body + sender + timestamp
- **Output:** Structured action items with metadata

**Extraction Logic:**
1. Identify explicit action requests ("Please review...", "Can you send...", "Need approval for...")
2. Identify implicit action items (questions requiring response, pending decisions)
3. Extract deadlines (explicit: "by EOD Friday" or implicit: "urgent", "ASAP")
4. Determine priority (urgent vs. this week vs. no deadline)
5. Detect sentiment/tone (frustrated, escalated, neutral, positive)

**Structured Output Format:**
```json
{
  "action_items": [
    {
      "description": "Review proposal draft before EOD",
      "client": "Acme Corp",
      "sender": "Sarah Johnson",
      "email_timestamp": "2026-02-19 09:42:00",
      "deadline": "2026-02-19 17:00:00",
      "priority": "urgent",
      "sentiment": "neutral",
      "context": "Need your feedback by 5pm for board meeting tomorrow"
    }
  ]
}
```

**LLM Options:**
- **Primary:** LM Studio with Qwen Coder 2.5 (local, 200 t/s, zero cost after hardware)
- **Fallback:** Google Gemini 1.5 Flash (free tier, cloud, reliable function calling)
- **Decision criteria:** Test Qwen Coder function calling reliability; if <85% accuracy, use Gemini

**Technical Implementation:**
- Custom prompt engineering for action item extraction
- Function calling / structured output for consistent JSON responses
- Batch processing (analyze multiple emails in single LLM call for efficiency)
- Error handling for LLM failures (timeout, rate limits, malformed responses)

---

**Feature 4: Formatted Slack Response with Prioritization**

**Description:**
Transform LLM-extracted action items into human-readable, actionable Slack message with visual prioritization.

**Response Structure:**

```
📧 Scanned [N] emails from last [timeframe]

Found [X] action items:

🔴 URGENT (Due today):
• Client [Name]: [Action item description]
  From: [Sender], [Timestamp]
  Context: "[Key excerpt from email]"

🟡 THIS WEEK (Due this week):
• Client [Name]: [Action item description]
  From: [Sender], [Timestamp], Due: [Date]

🟢 NO DEADLINE:
• Client [Name]: [Action item description]
  From: [Sender], [Timestamp]

💬 NEEDS RESPONSE (Sentiment flagged):
• Client [Name]: [Frustrated/Escalated tone detected - recommend phone call]
  From: [Sender], [Timestamp]
  Key phrase: "[Excerpt showing frustration]"

⏰ APPROACHING DEADLINES (Next 48 hours):
• Client [Name]: [Action due in 36 hours]
```

**Prioritization Logic:**
1. **🔴 URGENT:** Due today or marked "urgent"/"ASAP" in email
2. **💬 NEEDS RESPONSE:** Frustrated/escalated sentiment detected (always surfaced first)
3. **⏰ APPROACHING DEADLINES:** Within next 48 hours
4. **🟡 THIS WEEK:** Due within 7 days
5. **🟢 NO DEADLINE:** Action items without explicit deadline

**Visual Formatting:**
- Emoji for quick visual scanning
- Bold for client names and key info
- Indented context excerpts for detail
- Consistent structure across all responses

**Technical Implementation:**
- Markdown formatting for Slack compatibility
- Truncate long context excerpts (max 100 characters)
- Sort action items by priority, then by deadline
- Include email count and timeframe at top for context

---

**MVP Exclusions (Explicitly Not Building in Phase 1):**

To maintain focus and ship quickly, the following are intentionally excluded from MVP:

❌ **No Monday.com integration** - Manual copy/paste from Slack to Monday if needed
❌ **No automatic task creation** - Agent extracts, user decides what to do
❌ **No calendar sync** - User manually schedules based on extracted items
❌ **No team capacity visibility** - No Ali/Mo workload tracking yet
❌ **No assignment suggestions** - User delegates manually
❌ **No budget tracking** - No Google Sheets integration
❌ **No client value analysis** - No revenue intelligence
❌ **No upsell recommendations** - No strategic insights
❌ **No email templates** - No suggested responses
❌ **No multi-user support** - Single user (Jason) only
❌ **No web interface** - Slack-only for MVP

**Rationale:** These features are valuable but not essential to prove the core hypothesis: "Can an LLM reliably extract action items from 200 emails/day and save 10+ hours/week?" Answer this question first, then expand.

---

### Out of Scope for MVP

**Deferred to Phase 2 (Month 2-3):**

Once MVP proves value (Week 4 success criteria met), these features become priorities:

1. **Monday.com Integration**
   - Auto-create tasks from extracted action items
   - Pre-populate task fields (title, description, deadline, client tag)
   - Assign to Jason for review before finalizing
   - Update task status based on email follow-ups

2. **Calendar Sync**
   - Create Google Calendar events for deadlines
   - Block time for tasks in calendar
   - Prevent double-booking with team meetings

3. **Team Capacity Visibility**
   - Query Google Calendar for Ali and Mo's availability
   - Show capacity: "Ali 60% full, Mo 85% full"
   - Suggest task assignments based on workload

**Deferred to Phase 3 (Month 4-6):**

Advanced features that add strategic value:

4. **Budget Tracking & Alerts**
   - Integrate with Google Sheets time tracking
   - Alert when spending too much time on low-value clients
   - Client profitability analysis

5. **Revenue Intelligence**
   - Upsell/cross-sell opportunity detection
   - Client sentiment trends over time
   - Strategic recommendations for account growth

6. **Email Response Assistance**
   - Suggested email templates for common responses
   - Tone matching (formal vs. casual based on client relationship)
   - Follow-up reminders for unanswered emails

**Future Considerations (Year 2+):**

7. **Additional Tool Integrations**
   - Asana (alternative to Monday.com)
   - ClickUp, Jira, Linear (other PM tools)
   - Outlook/Exchange (alternative to Gmail)
   - Microsoft Teams (alternative to Slack)

8. **Multi-User & Team Features**
   - Support multiple account managers using same instance
   - Shared team briefings
   - Delegation workflows across team members

9. **Platform Expansion**
   - Web dashboard (beyond Slack-only interface)
   - Mobile app for on-the-go briefings
   - API for custom integrations

10. **AI Insights Dashboard**
    - Client health scores
    - Risk detection (churn indicators)
    - Performance analytics (response times, deadline adherence)

---

### MVP Success Criteria

**How We Know MVP is Successful:**

---

**Week 4 Validation Checkpoint**

If ALL of the following criteria are met by Week 4, the MVP is validated and we proceed to Phase 2:

✅ **Daily Usage Habit Formed**
- Email extraction used every morning for 4+ consecutive weeks
- No skipped days (indicates non-negotiable value)
- First thing checked when starting workday

✅ **Measurable Time Savings**
- Saves 1-2 hours/day on email triage (7-10 hours/week minimum)
- Validated through time tracking (before: 2-3 hours/day, after: 15-30 minutes/day)
- Can quantify: "This saved me X hours this week"

✅ **Accuracy & Reliability**
- Finds 85%+ of action items accurately (minimal false negatives)
- <10% false positives (incorrect or irrelevant items flagged)
- Zero critical emails missed (urgent items always surfaced)

✅ **Performance**
- Agent response time <60 seconds consistently
- 95%+ uptime (agent available when needed)
- Handles 150-200 emails/day without degradation

✅ **Trust & Confidence**
- No longer manually reading all 200 emails
- Trust agent to surface what matters
- Feel confident walking into meetings: "I know what's urgent"

✅ **"Can't Live Without It" Test**
- Would be painful/impossible to go back to manual email triage
- Recommend to colleagues: "You NEED this"
- Actively thinking about Phase 2 features wanted

---

**Proceed to Phase 2 If:**

- ✅ All Week 4 validation criteria met
- ✅ Want to add Monday.com task creation (most requested next feature)
- ✅ At least 1 colleague expresses genuine interest in using it
- ✅ Considering offering as consulting service (DWY/DFY)

**Signal to Proceed:** "This works. Now I want it to do MORE."

---

**Pivot or Abandon If:**

🚩 **Technical Failure:**
- <70% accuracy (LLM not reliable enough for action item extraction)
- >2 minutes average response time (too slow, kills productivity)
- Frequent crashes or API failures (unreliable)

🚩 **User Behavior Failure:**
- Not using it daily by Week 2 (insufficient value to form habit)
- Still manually reading all 200 emails (no trust in agent)
- Skipping days frequently (not solving core problem)

🚩 **Business Failure:**
- No measurable time savings (<5 hours/week)
- No reduction in stress or deadline performance
- Zero external interest from colleagues or potential clients

**Signal to Pivot:** "This doesn't work as expected. What needs to change?"
**Signal to Abandon:** "This isn't solving my problem. Not worth continuing."

---

**Decision Point:** Week 4 review

- If **SUCCESS:** Commit to Phase 2 development (Monday.com integration)
- If **MIXED:** Iterate on MVP, extend validation to Week 6
- If **FAILURE:** Analyze root cause, pivot approach, or abandon gracefully

---

### Future Vision (2-3 Years)

**If open-fleet is wildly successful, what does it become?**

---

**Year 1: Proven Personal Tool + Early Consulting Traction**

**Personal Impact:**
- Used daily without fail - saved Jason's job through 10-20 hours/week time savings
- Deadline performance transformed: 95%+ on-time delivery (from 60-70%)
- Stress reduced: Confident in meetings, no weekend work, proactive vs. reactive
- Portfolio piece: GitHub repo, demo video, blog post documenting journey

**Market Validation:**
- 3-5 consulting clients successfully deployed (DWY or DFY service)
- $2,500-$15,000 total consulting revenue
- GitHub repo has 100+ stars organically
- LinkedIn post about the tool generated 500+ views, 50+ reactions
- First "competitor" or copycat appears (validation of market need)

**Career Impact:**
- Portfolio helped land 2-3 job interviews mentioning open-fleet
- Received at least 1 job offer at higher salary (10-20% increase)
- Established credibility as AI/automation expert

**Product Maturity:**
- Phase 2 features shipped: Monday.com integration, calendar sync, team capacity
- Proven with real users beyond just Jason
- Documentation, setup guides, troubleshooting resources established

---

**Year 2: Consulting Practice + Product Evolution**

**Option A: Consulting-First Path**

**Business Model:**
- 20-30 consulting clients deployed and actively using open-fleet
- Monthly recurring revenue from support/maintenance contracts ($50-$200/client/month)
- $10k-$20k/month consulting revenue (mix of new deployments + ongoing support)
- 2-3 clients per month (sustainable pipeline without overwhelming capacity)

**Service Offerings:**
- DIY: Free GitHub repo (community support)
- DWY (Done With You): $1,500-$2,500 (setup assistance + training)
- DFY (Done For You): $5,000-$10,000 (full deployment + customization + 60-day support)
- Maintenance: $100-$500/month (ongoing support, updates, troubleshooting)

**Market Presence:**
- Community of 50-100 account managers/PMs using open-fleet
- Regular blog posts, case studies, demo videos
- Speaking at PM/operations conferences or webinars
- Referral network established (clients refer other AMs)

**Product Evolution:**
- All Phase 2-3 features implemented (budget tracking, revenue intelligence, email templates)
- Multi-tool support: Asana, Outlook, Teams integrations added
- Customization options for different industries/workflows
- Setup wizard reduces deployment time from 4 hours to 1 hour

---

**Option B: Product/SaaS Path**

**Business Model:**
- Transition from consulting to self-service SaaS product
- Hosted version eliminates local setup complexity
- Subscription tiers: $50-$200/month per user
- 50-200 paying subscribers ($2,500-$40,000/month MRR)

**Product Features:**
- Web-based setup wizard (no technical knowledge required)
- Cloud-hosted (no local LM Studio needed)
- Multi-user support (teams can share instance)
- Pre-built integrations (Monday, Asana, Gmail, Outlook, Slack, Teams)
- Analytics dashboard (time saved, tasks created, deadlines met)

**Go-to-Market:**
- Product Hunt launch
- Content marketing (SEO for "automate email for account managers")
- Freemium tier (limited to 50 emails/day)
- Direct sales to agencies (10-50 account managers per agency)

**Risk:** Higher development cost, infrastructure costs, customer support overhead

---

**Option C: Acquisition/Partnership Path**

**Potential Acquirers:**
- **Monday.com** - Acquire open-fleet as official "AI Email Assistant" integration
- **Asana** - Partner to offer as premium add-on
- **Slack** - Integrate as featured app in Slack App Directory
- **Agency Software** - Sell to agency management platform (Function Point, Workamajig)

**Acquisition Scenario:**
- $100k-$500k acquisition (based on user base, revenue, strategic fit)
- Jason joins acquiring company as PM or integration lead
- Open-fleet becomes official product feature

**Partnership Scenario:**
- Revenue share agreement (20-40% of subscription revenue)
- Co-marketing with larger platform
- Jason maintains ownership, partner provides distribution

---

**Option D: Internal Tool at New Employer**

**Career Path:**
- Landed dream job at agency, consultancy, or SaaS company
- Open-fleet becomes internal productivity tool
- Jason leads AI/automation initiatives at new company
- Portfolio piece fulfilled its purpose (career acceleration)

**Company Adoption:**
- Entire account management team (10-50 people) uses open-fleet
- Company invests in improving it further
- Jason's expertise leveraged to build additional internal tools

---

**Year 3: Platform, Scale, or Exit**

Depending on chosen path from Year 2:

**Consulting Path (Option A):**
- 100+ active clients
- $30k-$50k/month revenue
- Team of 2-3 consultants helping with deployments
- Exploring acquisition offers or productization

**SaaS Path (Option B):**
- 500-1,000 paying subscribers
- $25k-$200k/month MRR
- Venture-backed or bootstrapped profitable
- Considering Series A funding or acquisition

**Acquisition Path (Option C):**
- Integrated into major platform
- Reaching 10,000+ users through distribution partnership
- Jason building new products at acquiring company
- Equity payout from acquisition vested

**Internal Tool Path (Option D):**
- Jason promoted to Director/VP of Operations or AI/Automation
- Open-fleet expanded to other departments (sales, support, engineering)
- Established reputation as AI implementation expert
- Speaking at conferences, writing book, consulting on the side

---

**Expanded Capabilities (Year 2-3):**

Regardless of business model path, the product evolves with these capabilities:

**Multi-Tool Integration:**
- Support for 5-10 different PM tools (Monday, Asana, ClickUp, Jira, Linear, Trello)
- Support for 3-5 email providers (Gmail, Outlook, Exchange, Yahoo, Custom IMAP)
- Support for 3-5 messaging platforms (Slack, Teams, Discord, Email, SMS)

**AI Insights Dashboard:**
- Client health scores (engagement, sentiment trends, risk indicators)
- Revenue opportunity detection (upsell timing, cross-sell suggestions)
- Performance analytics (response times, deadline adherence, time saved)
- Team productivity benchmarks (compare performance across team members)

**Team Collaboration Features:**
- Shared team briefings (morning standup automated)
- Delegation automation (assign tasks based on capacity + skillset)
- Workload balancing across team (prevent burnout, optimize utilization)
- Cross-team visibility (account managers see what PMs are working on)

**Advanced Automation:**
- Auto-respond to common email types (acknowledgments, confirmations)
- Auto-escalate urgent issues to manager or team lead
- Auto-schedule meetings based on calendar availability
- Auto-generate status reports for clients

**Platform/Ecosystem:**
- Mobile app (iOS/Android) for on-the-go briefings
- API for custom integrations
- Zapier/Make.com connectors
- White-label version for agencies to resell

---

**North Star Vision (5-10 Years):**

**"The AI Chief of Staff for every account manager, project manager, and team lead managing complexity at scale."**

**Market Size:**
- 1 million+ account managers, PMs, and team leads in US alone
- 10 million+ globally
- TAM: $500M-$1B+ (at $50-$100/month per user)

**Vision:**
- Every professional managing email + tasks + people uses an AI agent
- Open-fleet is the de facto standard for this category
- Expanded beyond email to full work orchestration
- Acquired by major platform (Microsoft, Google, Salesforce) or IPO as independent company

**Jason's Role:**
- Founder/CEO of open-fleet (if independent)
- Product Lead at acquiring company (if acquired)
- AI/Automation thought leader (speaking, writing, consulting)
- Financially successful from equity or acquisition proceeds

---

**Key Decision Points Along the Way:**

**Month 6:** Consulting vs. SaaS path decision
**Year 1:** Scale independently vs. seek acquisition/partnership
**Year 2:** Bootstrap vs. raise funding (if SaaS path)
**Year 3:** Continue building vs. exit (acquisition)

Each decision depends on: personal goals, market traction, financial needs, time/energy available, and strategic opportunities that emerge.

---
