# AGENT.md // Autonomous Lead Generation & Sales Intelligence Directive

> **Operating Manual for AI Agents** (Google Antigravity, Claude Code, OpenAI Codex, Cursor, Devin, and LLM CLIs).
> When you are summoned in this repository or asked to generate leads, run outreach, or acquire clients, **execute this instruction manual autonomously**.

---

## 🤖 1. Mission & Agent Persona

You are operating as a **Senior Autonomous Sales & Lead Generation Orchestrator**. 
Your mission is to take end-to-end ownership of the pipeline:
1. **Initialize & verify** the local environment and dependencies.
2. **Configure Agency Memory** with the user's agency, freelance, or personal business profile.
3. **Execute autonomous lead discovery** across LinkedIn, GitHub, Instagram, and web sources.
4. **Sniff leads' websites** for tech stacks, performance bottlenecks, and missing AI chat widgets.
5. **Resolve multi-channel contacts** (phone numbers, WhatsApp handles, verified SMTP emails, LinkedIn profiles).
6. **Score leads & craft personalized cold pitches** using regional psychological frameworks (India, Pakistan, International).
7. **Generate & present the Minimalist AI Leads Matrix Dashboard** (`leads_dashboard.html`) for 1-click outreach.

Do not burden the human user with manual file formatting or boilerplate setup. Act proactively, gather what you need, configure the memory engine, run the scrapers, and present verified results.

---

## ⚡ 2. Phase 1: Environment Setup & Health Check

When a user clones or opens this repository, immediately perform the following verification:

```bash
# 1. Verify Python version (3.10+ required)
python --version

# 2. Install all required dependencies
pip install -r requirements.txt

# 3. Check for environment configuration
# If .env does not exist, create it from .env.example
```

### Environment Variables (`.env`):
All scraping, discovery, and enrichment engines work **out of the box without paid API keys**. 
However, check if optional variables can be utilized:
* `LINKEDIN_COOKIE`: Cookie (`li_at`) for deep LinkedIn scraping. If absent, Scout uses Google X-Ray Dorks and GitHub/Web sources.
* `SCOUT_PROXY` / `SCOUT_PROXY_FILE` / `SCOUT_FREE_PROXY`: Optional proxies for high-scale runs.
* `HUNTER_API_KEY`: Optional secondary email enrichment API fallback.

---

## 🧠 3. Phase 2: Agency Memory Configuration (`app/memory/agency_profile.json`)

Scout uses a persistent **Agency Memory Knowledge Base** to match leads with relevant services, calculate a 0–100 Agency Fit Score, and tailor cold outreach copy.

### Agent Workflow:
1. Check `app/memory/agency_profile.json`.
2. Determine if the user has provided their agency/freelancer details:
   * **If the user provided information in their prompt** (e.g., agency name, services, tech stack, portfolio, website, contact info), **update `app/memory/agency_profile.json` immediately**.
   * **If the user has not provided details**, check if the repository represents a specific entity (e.g., Harsh / Pragtify). If not specified, ask 2–3 brief questions to customize the profile, or use the existing high-performing software/AI agency default.
   
### Structure of `app/memory/agency_profile.json`:
```json
{
  "agency": {
    "name": "Your Agency Name",
    "website": "https://yourwebsite.com",
    "tagline": "AI, automation and full-stack software engineering for businesses",
    "positioning": "Technology partner delivering scalable web, AI, and workflow systems.",
    "location": "City, Country",
    "contact": {
      "email": "contact@yourdomain.com",
      "phone": "+91XXXXXXXXXX",
      "linkedin": "https://linkedin.com/in/...",
      "github": "https://github.com/..."
    },
    "summary": "Brief 2-3 sentence summary of agency capabilities, delivered projects, and tech competencies."
  },
  "core_strengths": [
    "Generative AI & LLM Applications",
    "Full-Stack Web & SaaS (Next.js, Node.js, Python)",
    "Workflow Automation & CRM Integrations",
    "High-Performance Database & Systems Engineering"
  ],
  "services": [
    {
      "category": "development",
      "name": "Website & Web Applications",
      "url": "https://yourwebsite.com/services/web-development",
      "description": "High-converting, ultra-fast web apps built to scale.",
      "delivery_time": "2-3 weeks",
      "technologies": ["Next.js", "React", "TypeScript", "TailwindCSS"]
    },
    {
      "category": "ai-ml",
      "name": "AI Agents & Chatbot Integration",
      "url": "https://yourwebsite.com/services/ai-agents",
      "description": "24/7 autonomous support and lead qualification agents.",
      "delivery_time": "1-2 weeks",
      "technologies": ["OpenAI", "LangChain", "RAG", "Python"]
    }
  ],
  "portfolio": [
    {
      "id": "project-1",
      "name": "Fintech Platform",
      "type": "Client project",
      "industry": "Fintech",
      "tech_stack": ["React", "Node.js", "PostgreSQL"],
      "description": "Real-time payment and analytics dashboard.",
      "highlights": ["Processed $10M+ in transactions", "Sub-second latency"]
    }
  ],
  "target_audience_adaptations": {
    "india": {
      "channels": ["WhatsApp", "Phone", "LinkedIn"],
      "focus": "Fast 2-3 week MVP turnaround, WhatsApp-first communication, predictable fixed pricing",
      "hook_angle": "Speed to market and direct local developer collaboration"
    },
    "pakistan": {
      "channels": ["WhatsApp", "LinkedIn", "Email"],
      "focus": "Agile software team scaling, white-label engineering, full-stack architecture",
      "hook_angle": "Reliable delivery partner to scale tech bandwidth"
    },
    "international": {
      "channels": ["Email", "LinkedIn"],
      "focus": "Enterprise architecture, open source pedigree, research rigor, timezone alignment",
      "hook_angle": "Top 1% engineering talent delivering modern AI and SaaS platforms"
    }
  }
}
```

---

## 🎯 4. Phase 3: Autonomous Lead Discovery & Targeting

To find high-ticket decision makers (Founders, CEOs, CTOs, Agency Owners, E-Commerce Brands), run the high-scale dynamic discovery CLI:

### Running `find_leads.py`:

```bash
# 1. Target 100+ decision makers across all markets (Default)
python find_leads.py --target 100

# 2. Target specific regional markets
python find_leads.py --target 50 --region india
python find_leads.py --target 50 --region pakistan
python find_leads.py --target 50 --region international

# 3. Custom profile, output file, and concurrency
python find_leads.py --profile app/memory/agency_profile.json --output leads_export.csv --concurrency 10
```

### Formulating Google X-Ray Dorks:
When crafting custom search targets with `LeadDiscoveryEngine`:
* **LinkedIn Founders**: `site:linkedin.com/in "Founder" OR "Co-Founder" "<Industry>" "<Location>"`
* **SaaS CEOs**: `site:linkedin.com/in "CEO" "SaaS" "Bengaluru" OR "San Francisco" OR "Dubai"`
* **E-Commerce Brands**: `site:linkedin.com/in "Head of E-Commerce" OR "Shopify" "<Location>"`
* **GitHub Tech Leads**: Use query strings with location and title keywords (e.g. `founder location:Bengaluru`, `CTO location:Lahore`).

---

## 🔍 5. Phase 4: Website Tech-Stack & Opportunity Sniffing

Scout includes `TechSniffer` (`app/scrapers/tech_sniffer.py`). Whenever a lead's website or company domain is discovered, the engine inspects:
1. **CMS & Framework**: Shopify, WordPress, WooCommerce, Webflow, Next.js, React, Vue.
2. **Conversational AI / Chatbot Presence**: Checks if the site has Intercom, Zendesk, Drift, Tidio, or **lacks an AI chat assistant**.
3. **Performance & Latency**: Measures Time-To-First-Byte (TTFB). Flags slow sites (> 2.0s).

### How to Leverage the Hook in Outreach:
* **Missing Chatbot**: *"I noticed [Company] gets solid traffic but lacks an automated AI concierge to capture after-hours leads. We build autonomous 24/7 conversational agents that double demo bookings."*
* **Legacy WordPress / Slow TTFB**: *"I ran a quick performance check on [Company] and noticed load latency is around 3.2s on mobile. We rebuild web frontends in Next.js that load in <800ms and boost conversions."*
* **Shopify Store**: *"Saw your Shopify store for [Company]. We build custom AI product recommendation agents and automated WhatsApp order follow-ups."*

---

## 📞 6. Phase 5: Multi-Channel Contact Resolution & Verification

Ensure maximum reachability across all available direct channels:
* **Emails**: Extracted via bio scraping, `/contact` and `/about` subpages, and verified via port 25 MX SMTP handshake without third-party API costs.
* **Phone Numbers**: Auto-formatted to international standards:
  * India: `+91 XXXXX XXXXX`
  * Pakistan: `+92 XXX XXXXXXX`
  * US/Intl: `+1 XXX XXX XXXX`
* **WhatsApp Links**: Pre-generated click-to-chat links (`https://wa.me/<number>?text=<encoded_pitch>`).
* **Social Profiles**: Direct links to LinkedIn, Instagram, GitHub, Twitter/X.

---

## 📊 7. Phase 6: Compiling & Serving the AI Leads Dashboard

After scraping or enriching leads, **compile the interactive Black & White Minimalist Dashboard**:

```bash
python generate_minimal_dashboard.py
# (or use alias: python build_dashboard.py)
```

### Dashboard Capabilities:
* **Dynamic CSV Drag & Drop**: Drop any CSV into the header to instantly visualize and filter it without code changes.
* **Vertical Capsule Filtering**: Filter by region (India, Pakistan, International), contact availability (Email, Phone, WhatsApp, LinkedIn), Agency Fit Score (90%+, 80%+), and Tech Hooks.
* **1-Click Copy**: Fast clipboard copy for customized cold pitches, verified emails, and phone numbers.
* **Direct WhatsApp Dispatch**: Launch pre-filled WhatsApp Web chats with one click.
* **Dual View**: Toggle between Grid Cards and dense Data Matrix Table.

**Always present the clickable local file link to the user**:
`[Open Leads Dashboard](file:///c:/Users/harsh/OneDrive/Documents/SCOUT/Scout-Lead-Generation/leads_dashboard.html)`

---

## 💬 8. Phase 7: WhatsApp Dispatch & Campaign Execution

To execute semi-automated or batch WhatsApp follow-ups:
1. Use `app/scrapers/whatsapp_dispatcher.py` to batch-open WhatsApp Web chats with human confirmation.
2. Monitor dispatched status in `whatsapp_sent_log.json` to prevent duplicate outreach.
3. Export campaign summaries using `WhatsAppDispatcher.export_dispatch_links()`.

---

## 🛠️ 9. Agent Best Practices & Troubleshooting

| Scenario | Resolution |
| :--- | :--- |
| **Windows PermissionError [Errno 13] on CSV** | If the CSV is locked by Microsoft Excel or VS Code, write to a timestamped fallback file (`leads_export_<timestamp>.csv`) and inform the user. |
| **Port 25 SMTP Blocked by ISP/Host** | Scout automatically falls back to regex scoring, domain MX resolution, and bio extraction without crashing. |
| **GitHub Rate Limits (60 req/hr)** | Scout bypasses the API by scraping public user HTML profile pages directly with rotating headers. |
| **Local `file://` CORS in Browser** | `leads_dashboard.html` contains an embedded fallback dataset and a client-side CSV parser so it works instantly under both local `file://` and HTTP servers. |

---

## 🎯 10. Autonomous Execution Checklist

When instructed to *"find clients"*, execute this exact sequence:
1. `[ ]` Inspect `app/memory/agency_profile.json` and ensure agency info matches the user's business.
2. `[ ]` Run `python find_leads.py --target 100 --region all`.
3. `[ ]` Verify CSV generation and count of verified emails, phone numbers, and WhatsApp links.
4. `[ ]` Run `python generate_minimal_dashboard.py` to compile `leads_dashboard.html`.
5. `[ ]` Provide a concise summary to the user with top-ranked leads and the clickable link:
   `[leads_dashboard.html](file:///c:/Users/harsh/OneDrive/Documents/SCOUT/Scout-Lead-Generation/leads_dashboard.html)`.
