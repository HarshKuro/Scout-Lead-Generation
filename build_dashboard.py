import csv
import json
from pathlib import Path

csv_path = Path("pragtify_leads_latest.csv")
leads = []
with open(csv_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        leads.append(r)

leads_json = json.dumps(leads, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pragtify Leads Explorer & Dispatcher</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #050507;
      --card-bg: #0d0d12;
      --card-hover: #13131a;
      --card-border: #1f1f2a;
      --card-border-hover: #323244;
      --text-main: #f4f4f7;
      --text-muted: #8e8ea0;
      --text-dim: #5c5c6e;
      --accent-white: #ffffff;
      
      /* Semantic Accents */
      --color-india: #10b981;
      --color-india-bg: rgba(16, 185, 129, 0.12);
      --color-pk: #06b6d4;
      --color-pk-bg: rgba(6, 182, 212, 0.12);
      --color-intl: #a855f7;
      --color-intl-bg: rgba(168, 85, 247, 0.12);
      
      --color-wa: #25d366;
      --color-wa-bg: rgba(37, 211, 102, 0.14);
      --color-email: #3b82f6;
      --color-email-bg: rgba(59, 130, 246, 0.14);
      --color-li: #0a66c2;
      --color-li-bg: rgba(10, 102, 194, 0.14);
      --color-ig: #e1306c;
      --color-ig-bg: rgba(225, 48, 108, 0.14);
      --color-opp: #f59e0b;
      --color-opp-bg: rgba(245, 158, 11, 0.12);
      
      --radius-capsule: 9999px;
      --radius-card: 16px;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      line-height: 1.5;
    }}

    /* Top Navigation Header */
    header {{
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(5, 5, 7, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--card-border);
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-logo {{
      width: 32px;
      height: 32px;
      background: #ffffff;
      color: #000000;
      font-weight: 900;
      font-size: 17px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      letter-spacing: -1px;
    }}

    .brand-title {{
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.3px;
      color: #ffffff;
    }}

    .brand-tagline {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .stats-bar {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .stat-capsule {{
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 5px 14px;
      border-radius: var(--radius-capsule);
      background: #111116;
      border: 1px solid var(--card-border);
      font-size: 12px;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .stat-capsule strong {{
      color: #ffffff;
      font-weight: 700;
    }}

    .stat-capsule.green strong {{ color: var(--color-india); }}
    .stat-capsule.cyan strong {{ color: var(--color-pk); }}
    .stat-capsule.blue strong {{ color: var(--color-email); }}

    /* Layout: Sidebar Capsules + Main Area */
    .app-container {{
      display: grid;
      grid-template-columns: 290px 1fr;
      min-height: calc(100vh - 65px);
    }}

    /* Left Vertical Capsule Dock */
    aside.capsule-dock {{
      position: sticky;
      top: 65px;
      height: calc(100vh - 65px);
      overflow-y: auto;
      padding: 24px 18px;
      border-right: 1px solid var(--card-border);
      background: #08080c;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }}

    aside.capsule-dock::-webkit-scrollbar {{
      width: 5px;
    }}
    aside.capsule-dock::-webkit-scrollbar-thumb {{
      background: #22222d;
      border-radius: 10px;
    }}

    .capsule-group {{
      display: flex;
      flex-direction: column;
      gap: 7px;
    }}

    .group-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-dim);
      padding: 0 8px;
      margin-bottom: 2px;
    }}

    /* Capsule Button (Vertical) */
    .capsule-btn {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 9px 14px;
      border-radius: var(--radius-capsule);
      background: #111117;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      text-align: left;
      user-select: none;
    }}

    .capsule-btn:hover {{
      background: #171720;
      color: #ffffff;
      border-color: var(--card-border-hover);
      transform: translateX(2px);
    }}

    .capsule-btn.active {{
      background: #ffffff;
      color: #000000;
      border-color: #ffffff;
      font-weight: 700;
      box-shadow: 0 2px 12px rgba(255, 255, 255, 0.15);
    }}

    .capsule-btn .count {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      font-weight: 600;
      font-family: var(--font-mono);
    }}

    .capsule-btn.active .count {{
      background: rgba(0, 0, 0, 0.12);
      color: #000000;
    }}

    .search-input-wrap {{
      position: relative;
    }}

    .search-input {{
      width: 100%;
      padding: 10px 14px 10px 36px;
      background: #101016;
      border: 1px solid var(--card-border);
      border-radius: var(--radius-capsule);
      color: #ffffff;
      font-size: 13px;
      outline: none;
      font-family: var(--font-sans);
      transition: border-color 0.15s ease;
    }}

    .search-input:focus {{
      border-color: #ffffff;
    }}

    .search-icon {{
      position: absolute;
      left: 13px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      font-size: 14px;
      pointer-events: none;
    }}

    .clear-search-btn {{
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 12px;
      display: none;
    }}

    /* Main Content Area */
    main.leads-viewport {{
      padding: 24px 32px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    .top-controls {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .results-info {{
      font-size: 14px;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .results-info strong {{
      color: #ffffff;
    }}

    .view-toggles {{
      display: inline-flex;
      background: #111117;
      border: 1px solid var(--card-border);
      border-radius: var(--radius-capsule);
      padding: 3px;
      gap: 2px;
    }}

    .view-toggle-btn {{
      padding: 5px 14px;
      border-radius: var(--radius-capsule);
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .view-toggle-btn.active {{
      background: #ffffff;
      color: #000000;
    }}

    /* Leads Grid */
    .leads-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 18px;
    }}

    /* Lead Card */
    .lead-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--card-card, 16px);
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 15px;
      transition: all 0.2s ease;
      position: relative;
    }}

    .lead-card:hover {{
      border-color: var(--card-border-hover);
      background: var(--card-hover);
      transform: translateY(-2px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }}

    .card-header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}

    .lead-meta {{
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .lead-name {{
      font-size: 17px;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.2px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .lead-company {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-muted);
    }}

    .lead-location {{
      font-size: 12px;
      color: var(--text-dim);
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    .score-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 4px 10px;
      border-radius: var(--radius-capsule);
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 700;
      border: 1px solid transparent;
    }}

    .score-badge.high {{
      background: rgba(34, 197, 94, 0.15);
      border-color: rgba(34, 197, 94, 0.35);
      color: #4ade80;
    }}

    .score-badge.mid {{
      background: rgba(245, 158, 11, 0.15);
      border-color: rgba(245, 158, 11, 0.35);
      color: #fbbf24;
    }}

    .score-badge.low {{
      background: rgba(148, 163, 184, 0.12);
      border-color: rgba(148, 163, 184, 0.25);
      color: #94a3b8;
    }}

    .badges-row {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .tag-badge {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: var(--radius-capsule);
      background: #15151e;
      border: 1px solid var(--card-border);
      color: var(--text-muted);
    }}

    .tag-badge.india {{
      background: var(--color-india-bg);
      border-color: rgba(16, 185, 129, 0.3);
      color: #34d399;
    }}

    .tag-badge.pakistan {{
      background: var(--color-pk-bg);
      border-color: rgba(6, 182, 212, 0.3);
      color: #22d3ee;
    }}

    .tag-badge.intl {{
      background: var(--color-intl-bg);
      border-color: rgba(168, 85, 247, 0.3);
      color: #c084fc;
    }}

    .tag-badge.opportunity {{
      background: var(--color-opp-bg);
      border-color: rgba(245, 158, 11, 0.3);
      color: #fbbf24;
    }}

    /* Contact Actions Row */
    .contact-actions {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      padding-top: 6px;
      border-top: 1px solid var(--card-border);
    }}

    .action-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
      border: 1px solid var(--card-border);
      background: #12121a;
      color: var(--text-main);
    }}

    .action-btn:hover {{
      background: #1a1a24;
      border-color: var(--card-border-hover);
      color: #ffffff;
    }}

    .action-btn.wa {{
      background: var(--color-wa-bg);
      border-color: rgba(37, 211, 102, 0.3);
      color: #4ade80;
    }}
    .action-btn.wa:hover {{
      background: rgba(37, 211, 102, 0.25);
      border-color: rgba(37, 211, 102, 0.5);
    }}

    .action-btn.pitch {{
      background: #ffffff;
      color: #000000;
      font-weight: 700;
      border-color: #ffffff;
    }}
    .action-btn.pitch:hover {{
      background: #e4e4e7;
    }}

    .action-btn.disabled {{
      opacity: 0.35;
      cursor: not-allowed;
      pointer-events: none;
    }}

    /* Social Links Row */
    .social-links {{
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .social-pill {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: var(--radius-capsule);
      border: 1px solid var(--card-border);
      background: #111116;
      color: var(--text-muted);
      text-decoration: none;
      transition: all 0.15s ease;
    }}

    .social-pill:hover {{
      color: #ffffff;
      border-color: var(--card-border-hover);
    }}

    .social-pill.li:hover {{ border-color: var(--color-li); color: #38bdf8; }}
    .social-pill.ig:hover {{ border-color: var(--color-ig); color: #f472b6; }}
    .social-pill.gh:hover {{ border-color: #ffffff; color: #ffffff; }}

    /* Pitch Box Accordion */
    .pitch-drawer {{
      background: #09090e;
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 12px;
      color: #d4d4d8;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}

    .pitch-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-dim);
    }}

    .copy-inline-btn {{
      background: #1a1a24;
      border: 1px solid var(--card-border);
      color: var(--text-main);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-family: var(--font-sans);
      transition: all 0.12s ease;
    }}

    .copy-inline-btn:hover {{
      background: #ffffff;
      color: #000000;
    }}

    .pitch-text {{
      line-height: 1.45;
      font-size: 12px;
      color: #e4e4e7;
      max-height: 85px;
      overflow-y: auto;
      white-space: pre-wrap;
    }}

    /* Table View */
    .table-container {{
      display: none;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow-x: auto;
    }}

    table.leads-table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 13px;
    }}

    table.leads-table th {{
      background: #0a0a0f;
      padding: 12px 16px;
      font-weight: 700;
      color: var(--text-muted);
      border-bottom: 1px solid var(--card-border);
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.5px;
    }}

    table.leads-table td {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--card-border);
      vertical-align: middle;
    }}

    table.leads-table tr:hover td {{
      background: #12121a;
    }}

    /* Floating Toast */
    .toast-bubble {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #ffffff;
      color: #000000;
      padding: 10px 18px;
      border-radius: var(--radius-capsule);
      font-size: 13px;
      font-weight: 700;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      z-index: 100;
      opacity: 0;
      pointer-events: none;
      transform: translateY(10px);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .toast-bubble.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    @media (max-width: 900px) {{
      .app-container {{
        grid-template-columns: 1fr;
      }}
      aside.capsule-dock {{
        position: static;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--card-border);
      }}
    }}
  </style>
</head>
<body>

  <!-- Top Navigation Bar -->
  <header>
    <div class="brand-group">
      <div class="brand-logo">P</div>
      <div>
        <div class="brand-title">Pragtify Leads Explorer</div>
        <div class="brand-tagline">AI & Automation Outreach Dispatcher</div>
      </div>
    </div>

    <!-- Live Counter Stats -->
    <div class="stats-bar">
      <div class="stat-capsule">Total: <strong id="stat-total">110</strong></div>
      <div class="stat-capsule green">Emails: <strong id="stat-emails">58</strong></div>
      <div class="stat-capsule cyan">WhatsApp: <strong id="stat-phones">63</strong></div>
      <div class="stat-capsule blue">LinkedIn: <strong id="stat-li">51</strong></div>
      <div class="stat-capsule">Instagram: <strong id="stat-ig">17</strong></div>
    </div>
  </header>

  <!-- App Body -->
  <div class="app-container">

    <!-- Left Capsule Navigation Dock -->
    <aside class="capsule-dock">

      <!-- Live Search Box -->
      <div class="capsule-group">
        <div class="group-label">Instant Search</div>
        <div class="search-input-wrap">
          <span class="search-icon">🔍</span>
          <input type="text" id="searchInput" class="search-input" placeholder="Search name, tech, role..." autocomplete="off">
          <button id="clearSearch" class="clear-search-btn">✕</button>
        </div>
      </div>

      <!-- Market Regions (Capsules) -->
      <div class="capsule-group">
        <div class="group-label">Market Region</div>
        <button class="capsule-btn active" data-filter="region" data-val="all">
          <span>🌐 All Markets</span>
          <span class="count" id="count-all">110</span>
        </button>
        <button class="capsule-btn" data-filter="region" data-val="India">
          <span>🇮🇳 India</span>
          <span class="count" id="count-india">78</span>
        </button>
        <button class="capsule-btn" data-filter="region" data-val="Pakistan">
          <span>🇵🇰 Pakistan</span>
          <span class="count" id="count-pakistan">14</span>
        </button>
        <button class="capsule-btn" data-filter="region" data-val="International">
          <span>🌍 International</span>
          <span class="count" id="count-intl">18</span>
        </button>
      </div>

      <!-- Contact Availability (Capsules) -->
      <div class="capsule-group">
        <div class="group-label">Contact Channel</div>
        <button class="capsule-btn" data-filter="contact" data-val="wa">
          <span>☎ WhatsApp / Phone</span>
          <span class="count" id="count-wa">63</span>
        </button>
        <button class="capsule-btn" data-filter="contact" data-val="email">
          <span>✉ Direct Email</span>
          <span class="count" id="count-email">58</span>
        </button>
        <button class="capsule-btn" data-filter="contact" data-val="linkedin">
          <span>💼 LinkedIn Profile</span>
          <span class="count" id="count-linkedin">51</span>
        </button>
        <button class="capsule-btn" data-filter="contact" data-val="instagram">
          <span>📸 Instagram Profile</span>
          <span class="count" id="count-instagram">17</span>
        </button>
      </div>

      <!-- Fit Score (Capsules) -->
      <div class="capsule-group">
        <div class="group-label">Fit Score</div>
        <button class="capsule-btn" data-filter="score" data-val="100">
          <span>★ 100/100 Top Fit</span>
          <span class="count" id="count-score-100">35</span>
        </button>
        <button class="capsule-btn" data-filter="score" data-val="80">
          <span>★ 80+ High Priority</span>
          <span class="count" id="count-score-80">65</span>
        </button>
      </div>

      <!-- Tech Stack / Weakness Hook (Capsules) -->
      <div class="capsule-group">
        <div class="group-label">Outreach Opportunity Hook</div>
        <button class="capsule-btn" data-filter="hook" data-val="no-chat">
          <span>🤖 Pitch: No Chat Widget</span>
          <span class="count" id="count-hook-chat">52</span>
        </button>
        <button class="capsule-btn" data-filter="hook" data-val="seo">
          <span>⚡ Pitch: Missing SEO</span>
          <span class="count" id="count-hook-seo">28</span>
        </button>
        <button class="capsule-btn" data-filter="hook" data-val="nextjs">
          <span>⚛ Next.js / React Stack</span>
          <span class="count" id="count-hook-next">34</span>
        </button>
      </div>

      <!-- Sort Order (Capsules) -->
      <div class="capsule-group">
        <div class="group-label">Sort By</div>
        <button class="capsule-btn active" data-sort="fit-desc">
          <span>↕ Fit Score (High → Low)</span>
        </button>
        <button class="capsule-btn" data-sort="name-asc">
          <span>↕ Name (A → Z)</span>
        </button>
        <button class="capsule-btn" data-sort="market">
          <span>↕ Market Region</span>
        </button>
      </div>

      <div style="margin-top: auto; padding-top: 15px;">
        <button id="resetFiltersBtn" class="capsule-btn" style="justify-content: center; background: #1a1a24; border-color: #272736;">
          ↺ Reset All Filters
        </button>
      </div>

    </aside>

    <!-- Main Results Viewport -->
    <main class="leads-viewport">
      
      <div class="top-controls">
        <div class="results-info">
          Showing <strong id="visibleCount">110</strong> of <strong id="totalCount">110</strong> decision-makers
        </div>

        <div class="view-toggles">
          <button id="btnViewGrid" class="view-toggle-btn active">Grid Cards</button>
          <button id="btnViewTable" class="view-toggle-btn">Dense Table</button>
        </div>
      </div>

      <!-- Grid Cards Container -->
      <div id="leadsGrid" class="leads-grid"></div>

      <!-- Dense Table Container -->
      <div id="tableContainer" class="table-container">
        <table class="leads-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Lead Name & Venture</th>
              <th>Market</th>
              <th>Fit Score</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Socials</th>
              <th>Quick Actions</th>
            </tr>
          </thead>
          <tbody id="leadsTableBody"></tbody>
        </table>
      </div>

    </main>
  </div>

  <!-- Toast Notification -->
  <div id="toastBubble" class="toast-bubble">✓ Copied to clipboard!</div>

  <script>
    // Embedded Leads Data
    const RAW_LEADS = {leads_json};

    let currentFilters = {{
      region: 'all',
      contact: null,
      score: null,
      hook: null,
      search: ''
    }};

    let currentSort = 'fit-desc';
    let currentView = 'grid';

    // UI Elements
    const searchInput = document.getElementById('searchInput');
    const clearSearch = document.getElementById('clearSearch');
    const leadsGrid = document.getElementById('leadsGrid');
    const tableContainer = document.getElementById('tableContainer');
    const leadsTableBody = document.getElementById('leadsTableBody');
    const visibleCount = document.getElementById('visibleCount');
    const totalCount = document.getElementById('totalCount');
    const toastBubble = document.getElementById('toastBubble');

    // Clipboard copy with visual toast feedback
    function copyText(text, label = 'Copied to clipboard!') {{
      if (!text) return;
      navigator.clipboard.writeText(text).then(() => {{
        showToast(`✓ ${{label}}`);
      }}).catch(() => {{
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        showToast(`✓ ${{label}}`);
      }});
    }}

    let toastTimer;
    function showToast(msg) {{
      toastBubble.textContent = msg;
      toastBubble.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => {{
        toastBubble.classList.remove('show');
      }}, 2200);
    }}

    // Filter Logic
    function getFilteredLeads() {{
      return RAW_LEADS.filter(lead => {{
        // Region
        if (currentFilters.region !== 'all' && lead.market_region !== currentFilters.region) {{
          return false;
        }}

        // Contact
        if (currentFilters.contact === 'wa' && !lead.phone) return false;
        if (currentFilters.contact === 'email' && !lead.email) return false;
        if (currentFilters.contact === 'linkedin' && !lead.linkedin_url) return false;
        if (currentFilters.contact === 'instagram' && !lead.instagram_url) return false;

        // Score
        const score = parseInt(lead.agency_fit_score || '0');
        if (currentFilters.score === '100' && score < 100) return false;
        if (currentFilters.score === '80' && score < 80) return false;

        // Hook
        if (currentFilters.hook === 'no-chat') {{
          const opp = (lead.tech_opportunities || '').toLowerCase();
          if (!opp.includes('chat') && !opp.includes('conversational')) return false;
        }}
        if (currentFilters.hook === 'seo') {{
          const opp = (lead.tech_opportunities || '').toLowerCase();
          if (!opp.includes('seo') && !opp.includes('preview')) return false;
        }}
        if (currentFilters.hook === 'nextjs') {{
          const tech = (lead.detected_technologies || '').toLowerCase();
          if (!tech.includes('next.js') && !tech.includes('react')) return false;
        }}

        // Search text
        if (currentFilters.search) {{
          const q = currentFilters.search.toLowerCase();
          const haystack = `${{lead.full_name}} ${{lead.company}} ${{lead.email}} ${{lead.phone}} ${{lead.location}} ${{lead.bio}} ${{lead.detected_technologies}}`.toLowerCase();
          if (!haystack.includes(q)) return false;
        }}

        return true;
      }}).sort((a, b) => {{
        if (currentSort === 'fit-desc') {{
          return parseInt(b.agency_fit_score || '0') - parseInt(a.agency_fit_score || '0');
        }}
        if (currentSort === 'name-asc') {{
          return (a.full_name || a.username || '').localeCompare(b.full_name || b.username || '');
        }}
        if (currentSort === 'market') {{
          return (a.market_region || '').localeCompare(b.market_region || '');
        }}
        return 0;
      }});
    }}

    // Render Cards View
    function renderGrid(leads) {{
      leadsGrid.innerHTML = '';
      if (!leads.length) {{
        leadsGrid.innerHTML = `<div style="grid-column: 1/-1; padding: 60px 20px; text-align: center; color: var(--text-dim);">
          <div style="font-size: 32px; margin-bottom: 12px;">🔍</div>
          <div style="font-size: 16px; font-weight: 700; color: #ffffff;">No leads match this filter criteria</div>
          <div style="font-size: 13px; margin-top: 4px;">Try clearing filters or search terms.</div>
        </div>`;
        return;
      }}

      leads.forEach((l, idx) => {{
        const score = parseInt(l.agency_fit_score || '0');
        const scoreClass = score >= 90 ? 'high' : score >= 70 ? 'mid' : 'low';
        const regionClass = (l.market_region || '').toLowerCase();
        
        const card = document.createElement('div');
        card.className = 'lead-card';

        // Tech Opp badges
        let oppBadge = '';
        if ((l.tech_opportunities || '').toLowerCase().includes('chat')) {{
          oppBadge = `<span class="tag-badge opportunity">🤖 Opportunity: No Chat Widget</span>`;
        }} else if ((l.tech_opportunities || '').toLowerCase().includes('seo')) {{
          oppBadge = `<span class="tag-badge opportunity">⚡ Opportunity: Missing SEO</span>`;
        }}

        // Tech Stack
        const techStr = l.detected_technologies ? l.detected_technologies.split('|').slice(0, 3).map(t => `<span class="tag-badge">${{t.trim()}}</span>`).join('') : '';

        // Social links
        let socialLinks = '';
        if (l.linkedin_url) socialLinks += `<a href="${{l.linkedin_url}}" target="_blank" class="social-pill li">💼 LinkedIn</a>`;
        if (l.instagram_url) socialLinks += `<a href="${{l.instagram_url}}" target="_blank" class="social-pill ig">📸 Instagram</a>`;
        if (l.website) socialLinks += `<a href="${{l.website}}" target="_blank" class="social-pill">🌐 Website</a>`;
        if (l.github_url) socialLinks += `<a href="${{l.github_url}}" target="_blank" class="social-pill gh">🐙 GitHub</a>`;

        // Action Buttons
        const waLink = l.whatsapp_chat_link;
        const waBtn = waLink ? `<a href="${{waLink}}" target="_blank" class="action-btn wa">💬 WhatsApp Chat</a>` : `<span class="action-btn disabled">💬 No WhatsApp</span>`;

        card.innerHTML = `
          <div class="card-header">
            <div class="lead-meta">
              <div class="lead-name">
                ${{l.full_name || l.username}}
              </div>
              <div class="lead-company">${{l.company || 'Founder / Indie Hacker'}}</div>
              <div class="lead-location">📍 ${{l.location || l.market_region}}</div>
            </div>
            <div class="score-badge ${{scoreClass}}">${{score}}/100</div>
          </div>

          <div class="badges-row">
            <span class="tag-badge ${{regionClass}}">${{l.market_region}}</span>
            ${{oppBadge}}
            ${{techStr}}
          </div>

          <div class="social-links">
            ${{socialLinks}}
          </div>

          <!-- Pitch Box -->
          <div class="pitch-drawer">
            <div class="pitch-header">
              <span>Personalized Pitch Hook</span>
              <button class="copy-inline-btn" data-copy="pitch" data-idx="${{idx}}">📋 Copy Pitch</button>
            </div>
            <div class="pitch-text">${{l.recommended_pitch || 'No pitch generated.'}}</div>
          </div>

          <!-- Contact Quick Actions -->
          <div class="contact-actions">
            ${{waBtn}}
            <button class="action-btn pitch" data-copy="contact" data-idx="${{idx}}">
              ${{l.email ? '✉ Copy Email' : (l.phone ? '☎ Copy Phone' : '📋 Copy Pitch')}}
            </button>
          </div>
        `;

        leadsGrid.appendChild(card);
      }});
    }}

    // Render Table View
    function renderTable(leads) {{
      leadsTableBody.innerHTML = '';
      leads.forEach((l, idx) => {{
        const score = parseInt(l.agency_fit_score || '0');
        const scoreClass = score >= 90 ? 'high' : score >= 70 ? 'mid' : 'low';
        
        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="color: var(--text-dim); font-family: var(--font-mono);">${{idx + 1}}</td>
          <td>
            <div style="font-weight: 700; color: #ffffff;">${{l.full_name || l.username}}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${{l.company || 'Founder'}}</div>
          </td>
          <td><span class="tag-badge ${{(l.market_region || '').toLowerCase()}}">${{l.market_region}}</span></td>
          <td><span class="score-badge ${{scoreClass}}">${{score}}</span></td>
          <td>${{l.email ? `<span style="color: #4ade80; cursor:pointer;" data-copy="text" data-val="${{l.email}}">✉ ${{l.email}}</span>` : '<span style="color:var(--text-dim)">—</span>'}}</td>
          <td>${{l.phone ? `<span style="color: #22d3ee; cursor:pointer;" data-copy="text" data-val="${{l.phone}}">☎ ${{l.phone}}</span>` : '<span style="color:var(--text-dim)">—</span>'}}</td>
          <td>
            <div style="display:flex; gap:4px;">
              ${{l.linkedin_url ? `<a href="${{l.linkedin_url}}" target="_blank" class="social-pill li">LI</a>` : ''}}
              ${{l.instagram_url ? `<a href="${{l.instagram_url}}" target="_blank" class="social-pill ig">IG</a>` : ''}}
              ${{l.website ? `<a href="${{l.website}}" target="_blank" class="social-pill">Web</a>` : ''}}
            </div>
          </td>
          <td>
            <div style="display:flex; gap:6px;">
              ${{l.whatsapp_chat_link ? `<a href="${{l.whatsapp_chat_link}}" target="_blank" class="action-btn wa" style="padding:4px 8px; font-size:11px;">WA</a>` : ''}}
              <button class="action-btn pitch" data-copy="pitch" data-idx="${{idx}}" style="padding:4px 8px; font-size:11px;">Copy Pitch</button>
            </div>
          </td>
        `;
        leadsTableBody.appendChild(row);
      }});
    }}

    // Update Counts and View
    function refreshView() {{
      const filtered = getFilteredLeads();
      visibleCount.textContent = filtered.length;
      totalCount.textContent = RAW_LEADS.length;

      if (currentView === 'grid') {{
        leadsGrid.style.display = 'grid';
        tableContainer.style.display = 'none';
        renderGrid(filtered);
      }} else {{
        leadsGrid.style.display = 'none';
        tableContainer.style.display = 'block';
        renderTable(filtered);
      }}
    }}

    // Global Click Delegation for Copying
    document.addEventListener('click', (e) => {{
      const btn = e.target.closest('[data-copy]');
      if (!btn) return;
      const copyType = btn.dataset.copy;
      const idx = btn.dataset.idx;
      const filtered = getFilteredLeads();
      const lead = filtered[idx];

      if (copyType === 'pitch' && lead) {{
        copyText(lead.recommended_pitch, 'Pitch copied to clipboard!');
      }} else if (copyType === 'contact' && lead) {{
        if (lead.email) {{
          copyText(lead.email, `Copied email: ${{lead.email}}`);
        }} else if (lead.phone) {{
          copyText(lead.phone, `Copied phone: ${{lead.phone}}`);
        }} else {{
          copyText(lead.recommended_pitch, 'Pitch copied to clipboard!');
        }}
      }} else if (copyType === 'text') {{
        copyText(btn.dataset.val, 'Copied to clipboard!');
      }}
    }});

    // Setup Capsule Filter Clicks
    document.querySelectorAll('.capsule-btn[data-filter]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const filterType = btn.dataset.filter;
        const filterVal = btn.dataset.val;

        // Toggle behavior for same group
        document.querySelectorAll(`.capsule-btn[data-filter="${{filterType}}"]`).forEach(b => b.classList.remove('active'));

        if (filterType === 'region') {{
          currentFilters.region = filterVal;
          btn.classList.add('active');
        }} else if (currentFilters[filterType] === filterVal) {{
          // Toggle off
          currentFilters[filterType] = null;
        }} else {{
          currentFilters[filterType] = filterVal;
          btn.classList.add('active');
        }}
        refreshView();
      }});
    }});

    // Setup Sort Clicks
    document.querySelectorAll('.capsule-btn[data-sort]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.capsule-btn[data-sort]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentSort = btn.dataset.sort;
        refreshView();
      }});
    }});

    // Reset Filters
    document.getElementById('resetFiltersBtn').addEventListener('click', () => {{
      currentFilters = {{ region: 'all', contact: null, score: null, hook: null, search: '' }};
      currentSort = 'fit-desc';
      searchInput.value = '';
      clearSearch.style.display = 'none';

      document.querySelectorAll('.capsule-btn').forEach(b => b.classList.remove('active'));
      document.querySelector('.capsule-btn[data-val="all"]').classList.add('active');
      document.querySelector('.capsule-btn[data-sort="fit-desc"]').classList.add('active');
      refreshView();
    }});

    // Search Input Handling
    searchInput.addEventListener('input', (e) => {{
      currentFilters.search = e.target.value.trim();
      clearSearch.style.display = currentFilters.search ? 'block' : 'none';
      refreshView();
    }});

    clearSearch.addEventListener('click', () => {{
      searchInput.value = '';
      currentFilters.search = '';
      clearSearch.style.display = 'none';
      refreshView();
    }});

    // View Toggles
    const btnViewGrid = document.getElementById('btnViewGrid');
    const btnViewTable = document.getElementById('btnViewTable');

    btnViewGrid.addEventListener('click', () => {{
      currentView = 'grid';
      btnViewGrid.classList.add('active');
      btnViewTable.classList.remove('active');
      refreshView();
    }});

    btnViewTable.addEventListener('click', () => {{
      currentView = 'table';
      btnViewTable.classList.add('active');
      btnViewGrid.classList.remove('active');
      refreshView();
    }});

    // Compute Dynamic Counts on Load
    function updateCounts() {{
      const total = RAW_LEADS.length;
      document.getElementById('count-all').textContent = total;
      document.getElementById('count-india').textContent = RAW_LEADS.filter(l => l.market_region === 'India').length;
      document.getElementById('count-pakistan').textContent = RAW_LEADS.filter(l => l.market_region === 'Pakistan').length;
      document.getElementById('count-intl').textContent = RAW_LEADS.filter(l => l.market_region === 'International').length;

      document.getElementById('count-wa').textContent = RAW_LEADS.filter(l => !!l.phone).length;
      document.getElementById('count-email').textContent = RAW_LEADS.filter(l => !!l.email).length;
      document.getElementById('count-linkedin').textContent = RAW_LEADS.filter(l => !!l.linkedin_url).length;
      document.getElementById('count-instagram').textContent = RAW_LEADS.filter(l => !!l.instagram_url).length;

      document.getElementById('count-score-100').textContent = RAW_LEADS.filter(l => parseInt(l.agency_fit_score || '0') === 100).length;
      document.getElementById('count-score-80').textContent = RAW_LEADS.filter(l => parseInt(l.agency_fit_score || '0') >= 80).length;

      document.getElementById('count-hook-chat').textContent = RAW_LEADS.filter(l => (l.tech_opportunities || '').toLowerCase().includes('chat')).length;
      document.getElementById('count-hook-seo').textContent = RAW_LEADS.filter(l => (l.tech_opportunities || '').toLowerCase().includes('seo')).length;
      document.getElementById('count-hook-next').textContent = RAW_LEADS.filter(l => (l.detected_technologies || '').toLowerCase().includes('next.js') || (l.detected_technologies || '').toLowerCase().includes('react')).length;
    }}

    // Initial Load
    updateCounts();
    refreshView();
  </script>
</body>
</html>
'''

output_path = Path("leads_dashboard.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✓ Created {output_path} with {len(leads)} leads embedded.")
