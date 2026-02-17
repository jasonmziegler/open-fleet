---
stepsCompleted: [1, 2]
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
