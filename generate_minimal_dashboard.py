import csv
import json
from pathlib import Path

csv_path = Path("pragtify_leads_latest.csv")
leads = []
if csv_path.exists():
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            leads.append(r)

leads_json = json.dumps(leads, ensure_ascii=False)

html_code = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SCOUT // AI LEADS MATRIX</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #000000;
      --surface: #070709;
      --surface-hover: #0d0d12;
      --border-dotted: #2a2a32;
      --border-dotted-light: #444452;
      --text: #ffffff;
      --text-muted: #888892;
      --text-dim: #555560;
      
      --accent-in: #10b981;
      --accent-pk: #06b6d4;
      --accent-intl: #a855f7;
      --accent-opp: #f59e0b;
      --accent-wa: #25d366;
      
      --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
      --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg);
      background-image: radial-gradient(#18181f 1px, transparent 1px);
      background-size: 20px 20px;
      color: var(--text);
      font-family: var(--font-sans);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
    }}

    /* Dotted Header */
    header.ai-header {{
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(0, 0, 0, 0.92);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px dotted var(--border-dotted);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .ai-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted-light);
      background: #08080a;
      color: #ffffff;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .ai-badge .pulse-dot {{
      width: 6px;
      height: 6px;
      background: var(--accent-in);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--accent-in);
      animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.4; transform: scale(0.85); }}
    }}

    .system-title {{
      font-size: 15px;
      font-weight: 800;
      letter-spacing: -0.2px;
      font-family: var(--font-mono);
      color: #ffffff;
    }}

    .system-title span {{
      color: var(--text-dim);
      font-weight: 400;
    }}

    .top-actions {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}

    .ai-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted);
      background: #09090c;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      font-family: var(--font-mono);
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s ease;
      user-select: none;
    }}

    .ai-btn:hover {{
      background: #15151c;
      color: #ffffff;
      border-color: #ffffff;
    }}

    .ai-btn.primary {{
      background: #ffffff;
      color: #000000;
      border-color: #ffffff;
      font-weight: 700;
    }}

    .ai-btn.primary:hover {{
      background: #e4e4e7;
    }}

    /* Main Container */
    .dashboard-layout {{
      display: grid;
      grid-template-columns: 290px 1fr;
      min-height: calc(100vh - 61px);
    }}

    /* Vertical Capsule Sidebar Dock */
    aside.capsule-dock {{
      position: sticky;
      top: 61px;
      height: calc(100vh - 61px);
      overflow-y: auto;
      padding: 20px 16px;
      border-right: 1px dotted var(--border-dotted);
      background: rgba(4, 4, 6, 0.75);
      backdrop-filter: blur(8px);
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    aside.capsule-dock::-webkit-scrollbar {{
      width: 4px;
    }}
    aside.capsule-dock::-webkit-scrollbar-thumb {{
      background: #22222b;
      border-radius: 4px;
    }}

    .dock-group {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .dock-title {{
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: var(--text-dim);
      font-family: var(--font-mono);
      padding: 0 8px;
      margin-bottom: 2px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    /* Capsule Pill Control */
    .capsule-pill {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      width: 100%;
      padding: 8px 14px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted);
      background: #09090c;
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: var(--font-sans);
      text-align: left;
    }}

    .capsule-pill:hover {{
      background: #14141b;
      border-color: var(--border-dotted-light);
      color: #ffffff;
      transform: translateX(2px);
    }}

    .capsule-pill.active {{
      background: #ffffff;
      color: #000000;
      border: 1px solid #ffffff;
      font-weight: 700;
      box-shadow: 0 0 16px rgba(255, 255, 255, 0.12);
    }}

    .capsule-pill .pill-count {{
      font-size: 11px;
      font-family: var(--font-mono);
      padding: 2px 7px;
      border-radius: 9999px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      font-weight: 500;
    }}

    .capsule-pill.active .pill-count {{
      background: rgba(0, 0, 0, 0.14);
      color: #000000;
      font-weight: 700;
    }}

    /* Search Box */
    .search-pill-wrap {{
      position: relative;
    }}

    .search-pill {{
      width: 100%;
      padding: 8px 12px 8px 32px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted-light);
      background: #08080a;
      color: #ffffff;
      font-size: 12px;
      font-family: var(--font-mono);
      outline: none;
      transition: border-color 0.15s ease;
    }}

    .search-pill:focus {{
      border-color: #ffffff;
    }}

    .search-pill-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 11px;
      color: var(--text-dim);
      pointer-events: none;
    }}

    /* File Drop Area */
    .drop-zone {{
      border: 1px dashed var(--border-dotted-light);
      border-radius: 12px;
      padding: 12px;
      text-align: center;
      background: rgba(255, 255, 255, 0.02);
      cursor: pointer;
      transition: all 0.2s ease;
    }}

    .drop-zone:hover, .drop-zone.dragover {{
      border-color: #ffffff;
      background: rgba(255, 255, 255, 0.05);
    }}

    .drop-zone-text {{
      font-size: 11px;
      font-family: var(--font-mono);
      color: var(--text-muted);
    }}

    /* Main Viewport */
    main.viewport {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }}

    .dashboard-toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      padding-bottom: 12px;
      border-bottom: 1px dotted var(--border-dotted);
    }}

    .metric-tags {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}

    .metric-tag {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      font-family: var(--font-mono);
      color: var(--text-muted);
      padding: 4px 10px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted);
      background: #07070a;
    }}

    .metric-tag strong {{
      color: #ffffff;
    }}

    .view-switchers {{
      display: inline-flex;
      border: 1px dotted var(--border-dotted);
      border-radius: 9999px;
      padding: 2px;
      background: #08080a;
      gap: 2px;
    }}

    .view-btn {{
      padding: 4px 12px;
      border-radius: 9999px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 11px;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all 0.15s ease;
    }}

    .view-btn.active {{
      background: #ffffff;
      color: #000000;
      font-weight: 700;
    }}

    /* Cards Grid */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 16px;
    }}

    /* Single Minimal Card */
    .lead-card {{
      background: var(--surface);
      border: 1px dotted var(--border-dotted);
      border-radius: 12px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      transition: all 0.15s ease;
      position: relative;
    }}

    .lead-card:hover {{
      border-color: #ffffff;
      background: var(--surface-hover);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
    }}

    .card-top {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
    }}

    .card-identity {{
      display: flex;
      flex-direction: column;
      gap: 2px;
    }}

    .card-name {{
      font-size: 16px;
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.2px;
    }}

    .card-role {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .card-location {{
      font-size: 11px;
      color: var(--text-dim);
      font-family: var(--font-mono);
    }}

    .fit-score {{
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted-light);
      background: #0c0c10;
      color: #ffffff;
    }}

    .fit-score.top {{
      border-color: var(--accent-in);
      color: var(--accent-in);
      background: rgba(16, 185, 129, 0.08);
    }}

    .badges-matrix {{
      display: flex;
      align-items: center;
      gap: 5px;
      flex-wrap: wrap;
    }}

    .badge-dotted {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 10px;
      font-family: var(--font-mono);
      padding: 3px 8px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted);
      background: #09090c;
      color: var(--text-muted);
    }}

    .badge-dotted.region-in {{
      border-color: rgba(16, 185, 129, 0.4);
      color: #34d399;
    }}
    .badge-dotted.region-pk {{
      border-color: rgba(6, 182, 212, 0.4);
      color: #22d3ee;
    }}
    .badge-dotted.region-intl {{
      border-color: rgba(168, 85, 247, 0.4);
      color: #c084fc;
    }}
    .badge-dotted.opp {{
      border-color: rgba(245, 158, 11, 0.4);
      color: #fbbf24;
    }}

    /* Pitch Container with Dotted Outline */
    .pitch-box {{
      border: 1px dotted var(--border-dotted);
      background: #040406;
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}

    .pitch-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 10px;
      font-family: var(--font-mono);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-dim);
    }}

    .pitch-body {{
      font-size: 11.5px;
      color: #d1d1d8;
      line-height: 1.45;
      max-height: 75px;
      overflow-y: auto;
      white-space: pre-wrap;
    }}

    /* Dotted Buttons */
    .card-footer {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      padding-top: 6px;
      border-top: 1px dotted var(--border-dotted);
    }}

    .copy-btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      padding: 7px 10px;
      border-radius: 6px;
      border: 1px dotted var(--border-dotted-light);
      background: #09090c;
      color: #ffffff;
      font-size: 11px;
      font-family: var(--font-mono);
      cursor: pointer;
      transition: all 0.12s ease;
      text-decoration: none;
    }}

    .copy-btn:hover {{
      background: #ffffff;
      color: #000000;
      border-color: #ffffff;
    }}

    .copy-btn.wa {{
      border-color: rgba(37, 211, 102, 0.4);
      color: #4ade80;
    }}
    .copy-btn.wa:hover {{
      background: #4ade80;
      color: #000000;
      border-color: #4ade80;
    }}

    .copy-btn.disabled {{
      opacity: 0.25;
      cursor: not-allowed;
      pointer-events: none;
    }}

    .social-pills-row {{
      display: flex;
      align-items: center;
      gap: 5px;
      flex-wrap: wrap;
    }}

    .social-tag {{
      font-size: 10px;
      font-family: var(--font-mono);
      padding: 2px 7px;
      border-radius: 9999px;
      border: 1px dotted var(--border-dotted);
      color: var(--text-dim);
      text-decoration: none;
      transition: all 0.12s ease;
    }}

    .social-tag:hover {{
      border-color: #ffffff;
      color: #ffffff;
    }}

    /* Table View */
    .table-viewport {{
      display: none;
      border: 1px dotted var(--border-dotted);
      border-radius: 10px;
      background: var(--surface);
      overflow-x: auto;
    }}

    table.ai-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: left;
    }}

    table.ai-table th {{
      background: #050508;
      border-bottom: 1px dotted var(--border-dotted);
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-dim);
    }}

    table.ai-table td {{
      padding: 12px 14px;
      border-bottom: 1px dotted var(--border-dotted);
      vertical-align: middle;
    }}

    table.ai-table tr:hover td {{
      background: #0d0d14;
    }}

    /* Floating Copied Toast */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #ffffff;
      color: #000000;
      border-radius: 9999px;
      padding: 8px 16px;
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 700;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
      z-index: 100;
      opacity: 0;
      pointer-events: none;
      transform: translateY(8px);
      transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .toast.show {{
      opacity: 1;
      transform: translateY(0);
    }}

    @media (max-width: 900px) {{
      .dashboard-layout {{
        grid-template-columns: 1fr;
      }}
      aside.capsule-dock {{
        position: static;
        height: auto;
        border-right: none;
        border-bottom: 1px dotted var(--border-dotted);
      }}
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header class="ai-header">
    <div class="brand-section">
      <div class="ai-badge">
        <span class="pulse-dot"></span>
        <span>SCOUT // MATRIX</span>
      </div>
      <div class="system-title">LEAD INTELLIGENCE <span>[AI ENGINE v2.4]</span></div>
    </div>

    <div class="top-actions">
      <!-- Hidden file input for dynamic CSV loading -->
      <input type="file" id="csvFileInput" accept=".csv" style="display: none;">
      <button id="importCsvBtn" class="ai-btn">
        <span>+ IMPORT CSV</span>
      </button>
      <button id="exportCsvBtn" class="ai-btn">
        <span>↓ EXPORT FILTERED</span>
      </button>
    </div>
  </header>

  <div class="dashboard-layout">

    <!-- Left Capsule Navigation Dock -->
    <aside class="capsule-dock">

      <!-- Dynamic Drag & Drop Target -->
      <div id="dropZone" class="drop-zone">
        <div class="drop-zone-text">📂 DROP ANY CSV HERE</div>
      </div>

      <!-- Instant Live Search -->
      <div class="dock-group">
        <div class="dock-title">
          <span>// INSTANT QUERY</span>
        </div>
        <div class="search-pill-wrap">
          <span class="search-pill-icon">⌕</span>
          <input type="text" id="searchInput" class="search-pill" placeholder="Filter text, tech, names..." autocomplete="off">
        </div>
      </div>

      <!-- Dynamic Market Region Capsules -->
      <div class="dock-group">
        <div class="dock-title">
          <span>// MARKET REGION</span>
        </div>
        <div id="regionCapsulesGroup" style="display:flex; flex-direction:column; gap:5px;">
          <button class="capsule-pill active" data-filter="region" data-val="all">
            <span>🌐 All Markets</span>
            <span class="pill-count" id="count-all">0</span>
          </button>
        </div>
      </div>

      <!-- Contact Availability Capsules -->
      <div class="dock-group">
        <div class="dock-title">
          <span>// CONTACT CHANNELS</span>
        </div>
        <button class="capsule-pill" data-filter="contact" data-val="wa">
          <span>☎ WhatsApp / Phone</span>
          <span class="pill-count" id="count-wa">0</span>
        </button>
        <button class="capsule-pill" data-filter="contact" data-val="email">
          <span>✉ Verified Email</span>
          <span class="pill-count" id="count-email">0</span>
        </button>
        <button class="capsule-pill" data-filter="contact" data-val="linkedin">
          <span>💼 LinkedIn Profile</span>
          <span class="pill-count" id="count-linkedin">0</span>
        </button>
        <button class="capsule-pill" data-filter="contact" data-val="instagram">
          <span>📸 Instagram Profile</span>
          <span class="pill-count" id="count-instagram">0</span>
        </button>
      </div>

      <!-- Fit Score Capsules -->
      <div class="dock-group">
        <div class="dock-title">
          <span>// FIT SCORE</span>
        </div>
        <button class="capsule-pill" data-filter="score" data-val="100">
          <span>★ 100/100 Top Fit</span>
          <span class="pill-count" id="count-score-100">0</span>
        </button>
        <button class="capsule-pill" data-filter="score" data-val="80">
          <span>★ 80+ High Priority</span>
          <span class="pill-count" id="count-score-80">0</span>
        </button>
      </div>

      <!-- Opportunity Weakness Hooks -->
      <div class="dock-group">
        <div class="dock-title">
          <span>// OPPORTUNITY HOOKS</span>
        </div>
        <button class="capsule-pill" data-filter="hook" data-val="no-chat">
          <span>🤖 Pitch: No Chat Widget</span>
          <span class="pill-count" id="count-hook-chat">0</span>
        </button>
        <button class="capsule-pill" data-filter="hook" data-val="seo">
          <span>⚡ Pitch: Missing SEO</span>
          <span class="pill-count" id="count-hook-seo">0</span>
        </button>
        <button class="capsule-pill" data-filter="hook" data-val="nextjs">
          <span>⚛ Next.js / React Stack</span>
          <span class="pill-count" id="count-hook-next">0</span>
        </button>
      </div>

      <!-- Sort Capsules -->
      <div class="dock-group">
        <div class="dock-title">
          <span>// SORT ORDER</span>
        </div>
        <button class="capsule-pill active" data-sort="fit-desc">
          <span>↕ Fit Score (High → Low)</span>
        </button>
        <button class="capsule-pill" data-sort="name-asc">
          <span>↕ Lead Name (A → Z)</span>
        </button>
        <button class="capsule-pill" data-sort="market">
          <span>↕ Market Region</span>
        </button>
      </div>

      <!-- Reset -->
      <div style="margin-top: auto; padding-top: 10px;">
        <button id="resetFiltersBtn" class="capsule-pill" style="justify-content: center; border-color: var(--border-dotted-light);">
          <span>↺ RESET FILTERS</span>
        </button>
      </div>

    </aside>

    <!-- Main Viewport -->
    <main class="viewport">

      <div class="dashboard-toolbar">
        <div class="metric-tags">
          <div class="metric-tag">MATCHED: <strong id="statVisible">0</strong> / <strong id="statTotal">0</strong></div>
          <div class="metric-tag">EMAILS: <strong id="statEmails">0</strong></div>
          <div class="metric-tag">PHONES: <strong id="statPhones">0</strong></div>
          <div class="metric-tag">LINKEDIN: <strong id="statLinkedin">0</strong></div>
        </div>

        <div class="view-switchers">
          <button id="btnViewGrid" class="view-btn active">GRID</button>
          <button id="btnViewTable" class="view-btn">TABLE</button>
        </div>
      </div>

      <!-- Grid Cards -->
      <div id="cardsGrid" class="cards-grid"></div>

      <!-- Table View -->
      <div id="tableView" class="table-viewport">
        <table class="ai-table">
          <thead>
            <tr>
              <th>#</th>
              <th>NAME & VENTURE</th>
              <th>REGION</th>
              <th>SCORE</th>
              <th>EMAIL</th>
              <th>PHONE</th>
              <th>CHANNELS</th>
              <th>ACTIONS</th>
            </tr>
          </thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>

    </main>
  </div>

  <div id="toast" class="toast">[ ✓ COPIED ]</div>

  <script>
    // Embedded Default Leads (Falls back gracefully when opened offline via file://)
    const DEFAULT_LEADS = {leads_json};

    let activeLeads = [];
    let currentFilters = {{
      region: 'all',
      contact: null,
      score: null,
      hook: null,
      search: ''
    }};
    let currentSort = 'fit-desc';
    let currentView = 'grid';

    // UI elements
    const cardsGrid = document.getElementById('cardsGrid');
    const tableView = document.getElementById('tableView');
    const tableBody = document.getElementById('tableBody');
    const searchInput = document.getElementById('searchInput');
    const statVisible = document.getElementById('statVisible');
    const statTotal = document.getElementById('statTotal');
    const statEmails = document.getElementById('statEmails');
    const statPhones = document.getElementById('statPhones');
    const statLinkedin = document.getElementById('statLinkedin');
    const toast = document.getElementById('toast');
    const csvFileInput = document.getElementById('csvFileInput');
    const importCsvBtn = document.getElementById('importCsvBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const dropZone = document.getElementById('dropZone');
    const regionCapsulesGroup = document.getElementById('regionCapsulesGroup');

    // Clipboard Copy Helper
    function copyText(text, label = 'COPIED TO CLIPBOARD') {{
      if (!text) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(() => showToast(label)).catch(() => fallbackCopy(text, label));
      }} else {{
        fallbackCopy(text, label);
      }}
    }}

    function fallbackCopy(text, label) {{
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast(label);
    }}

    let toastTimer;
    function showToast(msg) {{
      toast.textContent = `[ ✓ ${{msg}} ]`;
      toast.classList.add('show');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove('show'), 2000);
    }}

    // Robust RFC-4180 CSV Parser
    function parseCSV(text) {{
      const rows = [];
      let currentRow = [];
      let currentVal = '';
      let insideQuote = false;

      for (let i = 0; i < text.length; i++) {{
        const c = text[i];
        const next = text[i + 1];

        if (c === '"') {{
          if (insideQuote && next === '"') {{
            currentVal += '"';
            i++;
          }} else {{
            insideQuote = !insideQuote;
          }}
        }} else if (c === ',' && !insideQuote) {{
          currentRow.push(currentVal.trim());
          currentVal = '';
        }} else if ((c === '\\r' || c === '\\n') && !insideQuote) {{
          if (c === '\\r' && next === '\\n') i++;
          currentRow.push(currentVal.trim());
          if (currentRow.some(val => val.length > 0)) rows.push(currentRow);
          currentRow = [];
          currentVal = '';
        }} else {{
          currentVal += c;
        }}
      }}
      if (currentVal || currentRow.length) {{
        currentRow.push(currentVal.trim());
        if (currentRow.some(val => val.length > 0)) rows.push(currentRow);
      }}

      if (rows.length < 2) return [];

      const headers = rows[0].map(h => h.replace(/^["']|["']$/g, '').trim());
      const parsed = [];

      for (let r = 1; r < rows.length; r++) {{
        const row = rows[r];
        const obj = {{}};
        headers.forEach((h, idx) => {{
          obj[h] = row[idx] || '';
        }});

        // Column normalizer
        obj.full_name = obj.full_name || obj.name || obj.lead_name || obj.username || '';
        obj.market_region = obj.market_region || obj.region || obj.country || 'Global';
        obj.agency_fit_score = obj.agency_fit_score || obj.fit_score || obj.score || '50';
        obj.recommended_pitch = obj.recommended_pitch || obj.pitch || obj.message || '';
        parsed.push(obj);
      }}

      return parsed;
    }}

    // Load CSV file
    function handleFile(file) {{
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (e) => {{
        const csvText = e.target.result;
        const parsed = parseCSV(csvText);
        if (parsed.length > 0) {{
          activeLeads = parsed;
          showToast(`LOADED ${{parsed.length}} LEADS FROM ${{file.name.toUpperCase()}}`);
          setupRegionCapsules();
          updateStats();
          refresh();
        }} else {{
          alert('Could not parse any rows from this CSV file.');
        }}
      }};
      reader.readAsText(file, 'UTF-8');
    }}

    // Drag and Drop
    dropZone.addEventListener('dragover', (e) => {{
      e.preventDefault();
      dropZone.classList.add('dragover');
    }});
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {{
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    }});
    dropZone.addEventListener('click', () => csvFileInput.click());
    importCsvBtn.addEventListener('click', () => csvFileInput.click());
    csvFileInput.addEventListener('change', (e) => {{
      if (e.target.files.length) handleFile(e.target.files[0]);
    }});

    // Export Filtered CSV
    exportCsvBtn.addEventListener('click', () => {{
      const filtered = getFilteredLeads();
      if (!filtered.length) return alert('No leads match the current filter to export.');
      const headers = Object.keys(filtered[0]);
      let csvContent = headers.join(',') + '\\n';
      filtered.forEach(row => {{
        const values = headers.map(h => {{
          let val = (row[h] || '').toString().replace(/"/g, '""');
          return `"${{val}}"`;
        }});
        csvContent += values.join(',') + '\\n';
      }});

      const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `scout_filtered_${{Date.now()}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast('EXPORTED FILTERED CSV');
    }});

    // Build Dynamic Region Capsules
    function setupRegionCapsules() {{
      const regions = new Set();
      activeLeads.forEach(l => {{
        if (l.market_region) regions.add(l.market_region);
      }});

      regionCapsulesGroup.innerHTML = `
        <button class="capsule-pill ${{currentFilters.region === 'all' ? 'active' : ''}}" data-filter="region" data-val="all">
          <span>🌐 All Markets</span>
          <span class="pill-count" id="count-all">${{activeLeads.length}}</span>
        </button>
      `;

      regions.forEach(reg => {{
        const count = activeLeads.filter(l => l.market_region === reg).length;
        const icon = reg.toLowerCase() === 'india' ? '🇮🇳' : (reg.toLowerCase() === 'pakistan' ? '🇵🇰' : '🌍');
        const btn = document.createElement('button');
        btn.className = `capsule-pill ${{currentFilters.region === reg ? 'active' : ''}}`;
        btn.dataset.filter = 'region';
        btn.dataset.val = reg;
        btn.innerHTML = `<span>${{icon}} ${{reg}}</span><span class="pill-count">${{count}}</span>`;
        btn.addEventListener('click', () => {{
          document.querySelectorAll('.capsule-pill[data-filter="region"]').forEach(b => b.classList.remove('active'));
          currentFilters.region = reg;
          btn.classList.add('active');
          refresh();
        }});
        regionCapsulesGroup.appendChild(btn);
      }});

      regionCapsulesGroup.querySelector('[data-val="all"]').addEventListener('click', (e) => {{
        document.querySelectorAll('.capsule-pill[data-filter="region"]').forEach(b => b.classList.remove('active'));
        currentFilters.region = 'all';
        e.currentTarget.classList.add('active');
        refresh();
      }});
    }}

    // Filter Logic
    function getFilteredLeads() {{
      return activeLeads.filter(l => {{
        if (currentFilters.region !== 'all' && l.market_region !== currentFilters.region) return false;
        if (currentFilters.contact === 'wa' && !l.phone) return false;
        if (currentFilters.contact === 'email' && !l.email) return false;
        if (currentFilters.contact === 'linkedin' && !l.linkedin_url) return false;
        if (currentFilters.contact === 'instagram' && !l.instagram_url) return false;

        const score = parseInt(l.agency_fit_score || '0');
        if (currentFilters.score === '100' && score < 100) return false;
        if (currentFilters.score === '80' && score < 80) return false;

        const opp = (l.tech_opportunities || '').toLowerCase();
        if (currentFilters.hook === 'no-chat' && !opp.includes('chat') && !opp.includes('conversational')) return false;
        if (currentFilters.hook === 'seo' && !opp.includes('seo') && !opp.includes('preview')) return false;
        if (currentFilters.hook === 'nextjs') {{
          const tech = (l.detected_technologies || '').toLowerCase();
          if (!tech.includes('next.js') && !tech.includes('react')) return false;
        }}

        if (currentFilters.search) {{
          const q = currentFilters.search.toLowerCase();
          const haystack = `${{l.full_name}} ${{l.company}} ${{l.email}} ${{l.phone}} ${{l.location}} ${{l.bio}} ${{l.detected_technologies}}`.toLowerCase();
          if (!haystack.includes(q)) return false;
        }}
        return true;
      }}).sort((a, b) => {{
        if (currentSort === 'fit-desc') return parseInt(b.agency_fit_score || '0') - parseInt(a.agency_fit_score || '0');
        if (currentSort === 'name-asc') return (a.full_name || a.username || '').localeCompare(b.full_name || b.username || '');
        if (currentSort === 'market') return (a.market_region || '').localeCompare(b.market_region || '');
        return 0;
      }});
    }}

    // Render Cards
    function renderCards(leads) {{
      cardsGrid.innerHTML = '';
      if (!leads.length) {{
        cardsGrid.innerHTML = `
          <div style="grid-column: 1/-1; padding: 60px 20px; text-align: center; border: 1px dotted var(--border-dotted); border-radius: 12px; background: #040406;">
            <div style="font-family: var(--font-mono); font-size: 13px; color: var(--text-dim); margin-bottom: 6px;">[ EMPTY QUERY RESULT ]</div>
            <div style="font-size: 15px; font-weight: 700; color: #ffffff;">No leads match this criteria</div>
          </div>
        `;
        return;
      }}

      leads.forEach((l, idx) => {{
        const score = parseInt(l.agency_fit_score || '0');
        const scoreClass = score >= 90 ? 'top' : '';
        const regLower = (l.market_region || '').toLowerCase();
        const regClass = regLower.includes('india') ? 'region-in' : (regLower.includes('pakistan') ? 'region-pk' : 'region-intl');

        let oppBadge = '';
        if ((l.tech_opportunities || '').toLowerCase().includes('chat')) {{
          oppBadge = `<span class="badge-dotted opp">🤖 NO CHAT WIDGET</span>`;
        }} else if ((l.tech_opportunities || '').toLowerCase().includes('seo')) {{
          oppBadge = `<span class="badge-dotted opp">⚡ MISSING SEO TAGS</span>`;
        }}

        const techPills = l.detected_technologies ? l.detected_technologies.split('|').slice(0, 3).map(t => `<span class="badge-dotted">${{t.trim()}}</span>`).join('') : '';

        let socialTags = '';
        if (l.linkedin_url) socialTags += `<a href="${{l.linkedin_url}}" target="_blank" class="social-tag">LINKEDIN</a>`;
        if (l.instagram_url) socialTags += `<a href="${{l.instagram_url}}" target="_blank" class="social-tag">INSTA</a>`;
        if (l.website) socialTags += `<a href="${{l.website}}" target="_blank" class="social-tag">SITE</a>`;
        if (l.github_url) socialTags += `<a href="${{l.github_url}}" target="_blank" class="social-tag">GITHUB</a>`;

        const waBtn = l.whatsapp_chat_link
          ? `<a href="${{l.whatsapp_chat_link}}" target="_blank" class="copy-btn wa">💬 WHATSAPP</a>`
          : `<span class="copy-btn disabled">💬 NO PHONE</span>`;

        const card = document.createElement('div');
        card.className = 'lead-card';
        card.innerHTML = `
          <div class="card-top">
            <div class="card-identity">
              <div class="card-name">${{l.full_name || l.username}}</div>
              <div class="card-role">${{l.company || 'Founder / Builder'}}</div>
              <div class="card-location">📍 ${{l.location || l.market_region}}</div>
            </div>
            <div class="fit-score ${{scoreClass}}">${{score}}/100</div>
          </div>

          <div class="badges-matrix">
            <span class="badge-dotted ${{regClass}}">${{l.market_region}}</span>
            ${{oppBadge}}
            ${{techPills}}
          </div>

          <div class="social-pills-row">
            ${{socialTags}}
          </div>

          <div class="pitch-box">
            <div class="pitch-bar">
              <span>// TAILORED OUTREACH HOOK</span>
              <button class="copy-btn" style="padding: 2px 7px; font-size: 10px;" data-copy="pitch" data-idx="${{idx}}">⎘ COPY</button>
            </div>
            <div class="pitch-body">${{l.recommended_pitch || 'No pitch generated.'}}</div>
          </div>

          <div class="card-footer">
            ${{waBtn}}
            <button class="copy-btn" data-copy="contact" data-idx="${{idx}}">
              ${{l.email ? '✉ COPY EMAIL' : (l.phone ? '☎ COPY PHONE' : '⎘ COPY PITCH')}}
            </button>
          </div>
        `;
        cardsGrid.appendChild(card);
      }});
    }}

    // Render Table
    function renderTable(leads) {{
      tableBody.innerHTML = '';
      leads.forEach((l, idx) => {{
        const score = parseInt(l.agency_fit_score || '0');
        const scoreClass = score >= 90 ? 'top' : '';
        const regLower = (l.market_region || '').toLowerCase();
        const regClass = regLower.includes('india') ? 'region-in' : (regLower.includes('pakistan') ? 'region-pk' : 'region-intl');

        const row = document.createElement('tr');
        row.innerHTML = `
          <td style="font-family: var(--font-mono); color: var(--text-dim);">${{idx + 1}}</td>
          <td>
            <div style="font-weight: 700; color: #ffffff;">${{l.full_name || l.username}}</div>
            <div style="font-size: 11px; color: var(--text-muted);">${{l.company || 'Founder'}}</div>
          </td>
          <td><span class="badge-dotted ${{regClass}}">${{l.market_region}}</span></td>
          <td><span class="fit-score ${{scoreClass}}">${{score}}</span></td>
          <td>${{l.email ? `<span style="font-family:var(--font-mono); color:#4ade80; cursor:pointer;" data-copy="val" data-val="${{l.email}}">✉ ${{l.email}}</span>` : '<span style="color:var(--text-dim)">—</span>'}}</td>
          <td>${{l.phone ? `<span style="font-family:var(--font-mono); color:#22d3ee; cursor:pointer;" data-copy="val" data-val="${{l.phone}}">☎ ${{l.phone}}</span>` : '<span style="color:var(--text-dim)">—</span>'}}</td>
          <td>
            <div style="display:flex; gap:4px;">
              ${{l.linkedin_url ? `<a href="${{l.linkedin_url}}" target="_blank" class="social-tag">LI</a>` : ''}}
              ${{l.instagram_url ? `<a href="${{l.instagram_url}}" target="_blank" class="social-tag">IG</a>` : ''}}
              ${{l.website ? `<a href="${{l.website}}" target="_blank" class="social-tag">WEB</a>` : ''}}
            </div>
          </td>
          <td>
            <div style="display:flex; gap:4px;">
              ${{l.whatsapp_chat_link ? `<a href="${{l.whatsapp_chat_link}}" target="_blank" class="copy-btn wa" style="padding:3px 7px;">WA</a>` : ''}}
              <button class="copy-btn" data-copy="pitch" data-idx="${{idx}}" style="padding:3px 7px;">PITCH</button>
            </div>
          </td>
        `;
        tableBody.appendChild(row);
      }});
    }}

    // Update Live Metrics Counters
    function updateStats() {{
      statTotal.textContent = activeLeads.length;
      statEmails.textContent = activeLeads.filter(l => !!l.email).length;
      statPhones.textContent = activeLeads.filter(l => !!l.phone).length;
      statLinkedin.textContent = activeLeads.filter(l => !!l.linkedin_url).length;

      document.getElementById('count-wa').textContent = activeLeads.filter(l => !!l.phone).length;
      document.getElementById('count-email').textContent = activeLeads.filter(l => !!l.email).length;
      document.getElementById('count-linkedin').textContent = activeLeads.filter(l => !!l.linkedin_url).length;
      document.getElementById('count-instagram').textContent = activeLeads.filter(l => !!l.instagram_url).length;
      document.getElementById('count-score-100').textContent = activeLeads.filter(l => parseInt(l.agency_fit_score || '0') === 100).length;
      document.getElementById('count-score-80').textContent = activeLeads.filter(l => parseInt(l.agency_fit_score || '0') >= 80).length;
      document.getElementById('count-hook-chat').textContent = activeLeads.filter(l => (l.tech_opportunities || '').toLowerCase().includes('chat')).length;
      document.getElementById('count-hook-seo').textContent = activeLeads.filter(l => (l.tech_opportunities || '').toLowerCase().includes('seo')).length;
      document.getElementById('count-hook-next').textContent = activeLeads.filter(l => (l.detected_technologies || '').toLowerCase().includes('next.js') || (l.detected_technologies || '').toLowerCase().includes('react')).length;
    }}

    // Refresh View
    function refresh() {{
      const filtered = getFilteredLeads();
      statVisible.textContent = filtered.length;
      if (currentView === 'grid') {{
        cardsGrid.style.display = 'grid';
        tableView.style.display = 'none';
        renderCards(filtered);
      }} else {{
        cardsGrid.style.display = 'none';
        tableView.style.display = 'block';
        renderTable(filtered);
      }}
    }}

    // Event Delegation for Copy Buttons
    document.addEventListener('click', (e) => {{
      const btn = e.target.closest('[data-copy]');
      if (!btn) return;
      const copyType = btn.dataset.copy;
      const idx = btn.dataset.idx;
      const filtered = getFilteredLeads();
      const lead = filtered[idx];

      if (copyType === 'pitch' && lead) {{
        copyText(lead.recommended_pitch, 'PITCH COPIED');
      }} else if (copyType === 'contact' && lead) {{
        if (lead.email) copyText(lead.email, `COPIED: ${{lead.email}}`);
        else if (lead.phone) copyText(lead.phone, `COPIED: ${{lead.phone}}`);
        else copyText(lead.recommended_pitch, 'PITCH COPIED');
      }} else if (copyType === 'val') {{
        copyText(btn.dataset.val, 'COPIED TO CLIPBOARD');
      }}
    }});

    // Filter Capsule Clicks
    document.querySelectorAll('.capsule-pill[data-filter]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const filterType = btn.dataset.filter;
        const filterVal = btn.dataset.val;

        if (filterType === 'region') return; // Handled dynamically in setupRegionCapsules

        document.querySelectorAll(`.capsule-pill[data-filter="${{filterType}}"]`).forEach(b => b.classList.remove('active'));

        if (currentFilters[filterType] === filterVal) {{
          currentFilters[filterType] = null;
        }} else {{
          currentFilters[filterType] = filterVal;
          btn.classList.add('active');
        }}
        refresh();
      }});
    }});

    // Sort Capsule Clicks
    document.querySelectorAll('.capsule-pill[data-sort]').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.capsule-pill[data-sort]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentSort = btn.dataset.sort;
        refresh();
      }});
    }});

    // Reset Filters
    document.getElementById('resetFiltersBtn').addEventListener('click', () => {{
      currentFilters = {{ region: 'all', contact: null, score: null, hook: null, search: '' }};
      currentSort = 'fit-desc';
      searchInput.value = '';
      document.querySelectorAll('.capsule-pill').forEach(b => b.classList.remove('active'));
      const allBtn = document.querySelector('.capsule-pill[data-val="all"]');
      if (allBtn) allBtn.classList.add('active');
      const sortBtn = document.querySelector('.capsule-pill[data-sort="fit-desc"]');
      if (sortBtn) sortBtn.classList.add('active');
      refresh();
      showToast('FILTERS RESET');
    }});

    // Search Input
    searchInput.addEventListener('input', (e) => {{
      currentFilters.search = e.target.value.trim();
      refresh();
    }});

    // View Switcher
    const btnViewGrid = document.getElementById('btnViewGrid');
    const btnViewTable = document.getElementById('btnViewTable');
    btnViewGrid.addEventListener('click', () => {{
      currentView = 'grid';
      btnViewGrid.classList.add('active');
      btnViewTable.classList.remove('active');
      refresh();
    }});
    btnViewTable.addEventListener('click', () => {{
      currentView = 'table';
      btnViewTable.classList.add('active');
      btnViewGrid.classList.remove('active');
      refresh();
    }});

    // Initialize: Try to fetch latest CSV or fallback to embedded default data
    function init() {{
      fetch('pragtify_leads_latest.csv')
        .then(res => {{
          if (res.ok) return res.text();
          throw new Error('Local fetch not supported or file not found');
        }})
        .then(text => {{
          const parsed = parseCSV(text);
          if (parsed.length > 0) {{
            activeLeads = parsed;
          }} else {{
            activeLeads = DEFAULT_LEADS;
          }}
          setupRegionCapsules();
          updateStats();
          refresh();
        }})
        .catch(() => {{
          // Fallback to embedded data when running under strict local file:// protocol
          activeLeads = DEFAULT_LEADS;
          setupRegionCapsules();
          updateStats();
          refresh();
        }});
    }}

    init();
  </script>
</body>
</html>
'''

output_path = Path("leads_dashboard.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print(f"✓ Successfully generated minimal AI leads dashboard at {output_path}")
