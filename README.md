# open-fleet

**Lean, local-first AI agent for account managers drowning in email.**

## The Problem

Managing 200 emails/day across 18 clients while staying on top of deadlines, task delegation, and team coordination is overwhelming. Current solutions are expensive ($500+/month in API fees), cloud-based (privacy concerns), or superficial (chatbots that don't eliminate actual work).

## The Solution

open-fleet is an AI agent that extracts action items from your emails and delivers a prioritized briefing in Slack - saving 10-20 hours/week on email triage.

**MVP Features:**
- 📧 **Gmail integration** - scans emails for action items
- 🤖 **LLM extraction** - powered by LM Studio (local) or Gemini (cloud)
- 💬 **Slack interface** - simple commands, formatted responses
- 🎯 **Smart prioritization** - urgent, this week, needs response

**Example Output:**
```
📧 Scanned 187 emails from last 24 hours

Found 14 action items:

🔴 URGENT (Due today):
• Client Acme: Review proposal draft (Sarah, 9:42am)
• Client Beta: Approve Q2 budget (Mike, 11:15am)

🟡 THIS WEEK:
• Client Gamma: Schedule Q2 call (Jennifer, 2:34pm, Due: Friday)
• Client Delta: Send status update (Tom, 4:02pm, Due: Thursday)
[10 more items...]

💬 NEEDS RESPONSE (Frustrated tone):
• Client Echo: Frustrated about delay - recommend call (Lisa, 3:18pm)
```

## Status

📋 **Product Brief Complete** - See [`_bmad-output/planning-artifacts/product-brief-open-fleet-2026-02-16.md`](_bmad-output/planning-artifacts/product-brief-open-fleet-2026-02-16.md)

🚧 **MVP Development Starting** - Sprint 1 (Gmail API integration) begins soon

## Target Users

**Primary:** Account Managers managing 15+ clients, 150-200 emails/day, overwhelmed with manual triage

**Also valuable for:**
- Project Managers coordinating multiple projects
- Customer Success Managers managing large accounts
- Team Leads juggling email, tasks, and people coordination

## Why open-fleet?

- **💰 Zero token costs** - Local LM Studio (200 t/s) or Gemini free tier
- **🔒 Privacy-first** - Emails never leave your local network (with LM Studio)
- **⚡ Fast** - 30-second briefing vs. 2 hours of manual email reading
- **🎯 Work elimination** - Actually saves time, not just adds chat interface
- **📈 Proven ROI** - Built to solve real problem (drowning in 200 emails/day)

## Built With

- Python
- Slack Bolt framework
- Gmail API
- LM Studio / Google Gemini
- BMAD framework (AI-assisted product development)

## Documentation

- [**Product Brief**](_bmad-output/planning-artifacts/product-brief-open-fleet-2026-02-16.md) - Complete strategic foundation with:
  - Executive Summary & Core Vision
  - Target Users & User Journey
  - Success Metrics & KPIs
  - MVP Scope & Future Vision (Year 1-3 roadmap)

## Roadmap

**Phase 1: Email Action Item Extractor (4 weeks) - MVP**
- Week 1-2: Gmail API integration
- Week 2-3: LLM action item extraction
- Week 3-4: Polish & deploy
- Success criteria: Daily usage, 10+ hours/week saved, 85%+ accuracy

**Phase 2: Task Automation (Month 2-3)**
- Monday.com integration (auto-create tasks)
- Google Calendar sync
- Team capacity visibility

**Phase 3: Intelligence Layer (Month 4-6)**
- Budget tracking & alerts
- Client sentiment analysis
- Revenue intelligence (upsell recommendations)

## Installation

*Coming soon - MVP under development*

Setup will include:
1. Gmail API OAuth setup
2. Slack app creation
3. LM Studio or Gemini API configuration
4. Cloudflare tunnel (for local Slack webhook)

## Contributing

Not accepting contributions yet - MVP in active development. Check back after Phase 1 completion!

## License

*License TBD*

---

**Built to save my job. Now helping other account managers do the same.**

*If you're drowning in email, this is for you.*
