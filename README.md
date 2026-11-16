# Scout // Autonomous Lead Discovery & Intelligence Matrix

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Discord](https://img.shields.io/discord/1467620600267931713?color=7289da&label=Discord&logo=discord&logoColor=white)](https://discord.gg/eneDNUbzcc)
[![Maintainer](https://img.shields.io/badge/Unofficial%20Maintainer-Harsh%20(@HarshKuro)-black?style=flat&logo=github)](https://github.com/HarshKuro)

> Autonomous, high-scale lead generation engine for appointment setters, sales developers, and agency owners. Discovers decision makers across 8+ platforms, sniffs client tech stacks, verifies emails & phone numbers, and dynamically generates custom cold pitches powered by an Agency Memory Knowledge Base.

---

## ⚡ Key Highlights & Extended Capabilities

* **Lead Discovery Engine (Google X-Ray Dorks & Direct Scraping)**: Zero manual username hunting. Automatically targets Founders, CEOs, and CTOs across **India**, **Pakistan**, and **International** markets.
* **Agency Memory Knowledge Base (`app/memory/agency_profile.json`)**: Ingests agency capabilities, case studies, delivery timelines, and tech stack to calculate 0–100 Agency Fit Scores and craft tailored cold pitches.
* **Website Tech-Stack & Opportunity Sniffer**: Inspects leads' domains for Shopify, WordPress, Next.js, and flags missing conversational AI/chat widgets or slow loading speeds for high-converting outreach hooks.
* **Multi-Channel Contact Intelligence**: Direct extraction of phone numbers, verified emails via SMTP handshake, LinkedIn profiles, and Instagram handles.
* **One-Click WhatsApp Dispatch**: Click-to-chat `wa.me` links pre-filled with tailored pitches for semi-automated sales follow-ups.
* **Interactive AI Leads Dashboard (`leads_dashboard.html`)**: Dynamic, ultra-clean black-and-white minimalist matrix interface with dotted accents, vertical capsule filters, drag-and-drop CSV ingestion, and 1-click clipboard copy.

---

## 📦 Installation

```bash
git clone https://github.com/HarshKuro/Scout.git
cd Scout
pip install -r requirements.txt
cp .env.example .env
```

---

## 🚀 Quickstart & Usage

### 1. High-Scale Autonomous Lead Generation (`find_leads.py`)

Run the dynamic discovery runner to automatically find, enrich, and score leads:

```bash
# Find and enrich 100+ decision makers across all regions (default)
python find_leads.py --target 100

# Target specific regional markets
python find_leads.py --target 50 --region india
python find_leads.py --target 50 --region pakistan
python find_leads.py --target 50 --region international

# Use custom agency profile & output path with controlled concurrency
python find_leads.py --profile app/memory/agency_profile.json --output my_leads.csv --concurrency 10
```

#### CLI Parameters:
* `--target`: Target number of validated leads to discover (e.g. `100`).
* `--region`: `all` | `india` | `pakistan` | `international`.
* `--profile`: Path to custom agency memory profile JSON.
* `--output`: CSV destination file path.
* `--concurrency`: Number of parallel scraping threads (default: `10`).

### 2. Interactive CLI Mode (`scout.py`)

```bash
python scout.py             # Interactive menu mode
python scout.py --verbose   # Enable debug logging
python scout.py --version
python scout.py --help
```

---

## 🖥️ Minimalist AI Leads Dashboard (`leads_dashboard.html`)

An ultra-clean, cyberpunk-inspired black and white dashboard to inspect, filter, and act on leads:

* **Dynamic File Ingestion**: Drop any export CSV into the header dropzone or open `leads_dashboard.html` directly in your browser.
* **Vertical Capsule Controls**: Real-time filtering by Region (India, Pakistan, International), Contact Availability (Email, Phone, WhatsApp, LinkedIn), Agency Fit Score (90%+, 80%+), and Tech Opportunities.
* **1-Click Copy**: Copy cold pitches, emails, or phone numbers directly to clipboard.
* **Instant WhatsApp Trigger**: Launch WhatsApp Web with pre-drafted personalized messages directly from each lead card.
* **Dual View**: Toggle between responsive Grid Cards and high-density Data Matrix Table.

To view: simply double-click [leads_dashboard.html](file:///c:/Users/harsh/OneDrive/Documents/SCOUT/Scout-Lead-Generation/leads_dashboard.html) in your browser.

---

## 🌐 Supported Platforms & Scrapers

| Platform | Auth Required | What It Scrapes |
| :--- | :--- | :--- |
| **LinkedIn** | Session cookie (`li_at`) | Profile, headline, bio, experience, verified emails |
| **GitHub** | None (HTML / API fallback) | Profile, bio, email, website, LinkedIn & Insta socials, repositories |
| **Instagram** | None | Bio, follower count, email, phone numbers, linktree/bio links |
| **TikTok** | None | Profile, bio, follower count, likes, contact email |
| **YouTube** | None | Channel description, subscriber count, business email, external links |
| **Twitch** | None | Profile, bio, followers, partner status, external socials |
| **Pinterest** | None | Profile, bio, follower counts, boards, target website |
| **Linktree / Bio-links** | None | Bio.link, Stan, Linkr, Linktree social aggregators |

---

## 🧠 Agency Memory & Tailored Pitching

Scout uses `app/memory/agency_profile.json` as its persistent knowledge base. You can customize this file with your own agency or business profile:

* **Services & Capabilities**: Web Apps, SaaS Platforms, Mobile Development, AI Agents, Enterprise ERP/CRM.
* **Core Strengths**: RAG pipelines, LLMs, systems programming, modern frontend stacks.
* **Target Audience Adaptations**:
  * **India**: WhatsApp-first outreach, rapid 2–3 week MVP delivery, local cost efficiency.
  * **Pakistan**: Agile software engineering, white-label scaling, direct founder-to-founder synergy.
  * **International (US/UK/EU/UAE)**: Enterprise-grade architecture, peer-reviewed research, open-source pedigree, SOC-compliant reliability.

---

## ⚙️ Configuration & Setup

### LinkedIn Authentication (Optional for Deep InMail)
1. Log into LinkedIn in Google Chrome.
2. Open DevTools (`F12`) > **Application** > **Cookies** > `linkedin.com`.
3. Copy the value of `li_at`.
4. Add to `.env`:
   ```env
   LINKEDIN_COOKIE=your_li_at_cookie_value
   ```

### Proxy Configuration (Optional)
```env
# Single proxy
SCOUT_PROXY=http://user:pass@host:port

# Rotating proxies from file (one per line)
SCOUT_PROXY_FILE=proxies.txt

# Free anonymous proxy pool
SCOUT_FREE_PROXY=true
```

---

## 🔬 How Lead Enrichment Works

```mermaid
flowchart TD
    A["Discovery Engine (Google X-Ray / Platform Queries)"] --> B["Profile Scraper (GitHub / LinkedIn / Insta)"]
    B --> C["Website Deep Sniffer (Meta, Headers, Tech Stack, Latency)"]
    C --> D["Multi-Channel Contact Resolver (Regex & MX SMTP Handshake)"]
    D --> E["Agency Memory Matcher (Profile Fit & Regional Adaptation)"]
    E --> F["CSV Intelligence Export & AI Dashboard"]
```

1. **Discovery**: Extracts target profiles matching niche keywords, location, and seniority.
2. **Contact Resolution**: Resolves emails, phone numbers, and WhatsApp handles directly from profiles and websites.
3. **SMTP Verification**: Performs direct port 25 MX handshake validation without paid third-party APIs.
4. **Tech-Stack Sniffing**: Flags missing conversational AI, unoptimized platforms, or modern frameworks.
5. **Pitch Generation**: Pairs identified pain points with corresponding agency case studies and delivery guarantees.

---

## 👥 Authors & Maintainers

* **Original Project**: [kiryano/Scout](https://github.com/kiryano/Scout)
* **Unofficial Maintainer**: **Harsh** ([@HarshKuro](https://github.com/HarshKuro) - `https://github.com/HarshKuro`)
  * *Lead Discovery Engine (Google X-Ray Dorks)*
  * *Website Tech-Stack & Opportunity Sniffer*
  * *Agency Memory Knowledge Base & Matching System*
  * *Automated One-Click WhatsApp Web Dispatcher*
  * *Black & White Minimalist AI Leads Matrix Dashboard*

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
