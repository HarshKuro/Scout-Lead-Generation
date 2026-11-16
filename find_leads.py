import csv
import time
import os
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich import box

from app.memory import AgencyMemory, LeadMatcher
from app.scrapers.discovery import LeadDiscoveryEngine
from app.scrapers.github import scrape_profile as scrape_github
from app.scrapers.enrichment import LeadEnricher
from app.scrapers.whatsapp_dispatcher import WhatsAppDispatcher

console = Console()

TARGET_QUERIES = [
    # --- INDIA (Founders, CEOs, CTOs, Agencies, AI & SaaS) ---
    {"region": "India", "query": "founder location:Bengaluru"},
    {"region": "India", "query": "CEO location:Bengaluru"},
    {"region": "India", "query": "CTO location:Bengaluru"},
    {"region": "India", "query": "founder location:Mumbai"},
    {"region": "India", "query": "CEO location:Mumbai"},
    {"region": "India", "query": "CTO location:Mumbai"},
    {"region": "India", "query": "founder location:Delhi"},
    {"region": "India", "query": "CEO location:Delhi"},
    {"region": "India", "query": "founder location:Gurgaon"},
    {"region": "India", "query": "founder location:Noida"},
    {"region": "India", "query": "founder location:Hyderabad"},
    {"region": "India", "query": "CEO location:Hyderabad"},
    {"region": "India", "query": "founder location:Pune"},
    {"region": "India", "query": "founder location:Chennai"},
    {"region": "India", "query": "founder location:Ahmedabad"},
    {"region": "India", "query": "founder location:Kolkata"},
    {"region": "India", "query": "agency location:India"},
    {"region": "India", "query": "fintech founder location:India"},
    {"region": "India", "query": "AI founder location:India"},

    # --- PAKISTAN (Founders, Software Houses, AI & CRM) ---
    {"region": "Pakistan", "query": "founder location:Lahore"},
    {"region": "Pakistan", "query": "CEO location:Lahore"},
    {"region": "Pakistan", "query": "CTO location:Lahore"},
    {"region": "Pakistan", "query": "founder location:Karachi"},
    {"region": "Pakistan", "query": "CEO location:Karachi"},
    {"region": "Pakistan", "query": "CTO location:Karachi"},
    {"region": "Pakistan", "query": "founder location:Islamabad"},
    {"region": "Pakistan", "query": "CEO location:Islamabad"},
    {"region": "Pakistan", "query": "software agency location:Pakistan"},
    {"region": "Pakistan", "query": "AI founder location:Pakistan"},

    # --- INTERNATIONAL (US, UK, UAE, Singapore, Canada, EU, Australia) ---
    {"region": "International", "query": 'founder location:"San Francisco"'},
    {"region": "International", "query": 'CEO location:"San Francisco"'},
    {"region": "International", "query": 'CTO location:"San Francisco"'},
    {"region": "International", "query": 'founder location:"New York"'},
    {"region": "International", "query": 'CEO location:"New York"'},
    {"region": "International", "query": "founder location:London"},
    {"region": "International", "query": "CEO location:London"},
    {"region": "International", "query": "founder location:Dubai"},
    {"region": "International", "query": "CEO location:Dubai"},
    {"region": "International", "query": "founder location:Singapore"},
    {"region": "International", "query": "founder location:Toronto"},
    {"region": "International", "query": "founder location:Berlin"},
    {"region": "International", "query": "founder location:Sydney"},
    {"region": "International", "query": "founder location:Austin"},
]

def run_lead_generation(target_count: int = 100):
    console.print("\n[bold cyan]=== Pragtify High-Scale Lead Discovery & Enrichment Engine ===[/bold cyan]\n")

    memory = AgencyMemory()
    matcher = LeadMatcher(memory)
    discovery = LeadDiscoveryEngine()
    enricher = LeadEnricher()

    console.print(f"[white]Agency Memory:[/white] [bold green]{memory.agency_name}[/bold green] | Services: [green]{len(memory.services)}[/green] | Case Studies: [green]{len(memory.portfolio)}[/green]")
    console.print(f"[white]Goal:[/white] Discover & enrich at least [bold yellow]{target_count}[/bold yellow] high-fit leads across India, Pakistan & International.\n")

    # Step 1: Discover candidate usernames across all regions
    console.print("[bold yellow][1/3] Searching & Discovering Profiles Across Target Hubs...[/bold yellow]")
    discovered = []
    seen = set()

    for item in TARGET_QUERIES:
        reg = item["region"]
        q = item["query"]
        results = discovery._search_github_html(q, max_results=20)
        for r in results:
            u = r.get("username")
            if u and u.lower() not in seen:
                seen.add(u.lower())
                discovered.append({"username": u, "region": reg})

        if len(discovered) >= target_count * 3:
            break

    console.print(f"[green]✓ Discovered {len(discovered)} potential decision-maker profiles across India, Pakistan & Global.[/green]\n")

    # Step 2: Concurrently scrape and enrich profiles
    console.print(f"[bold yellow][2/3] Extracting Profiles, Socials (LinkedIn/Insta), Tech Stacks & Contacts...[/bold yellow]")

    processed_leads = []
    batch_targets = discovered

    def _worker(item):
        u = item["username"]
        reg = item["region"]
        try:
            profile = scrape_github(u)
            if not profile or not any([profile.get("full_name"), profile.get("bio"), profile.get("company"), profile.get("website")]):
                return None

            if not profile.get("location"):
                profile["location"] = reg

            enriched = enricher.enrich_lead(profile)
            matched = matcher.match_lead(enriched)
            return matched
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(_worker, it): it for it in batch_targets}
        for future in as_completed(futures):
            res = future.result()
            if res:
                processed_leads.append(res)
                name = res.get("full_name") or res.get("username")
                reg = res.get("market_region")
                has_email = bool(res.get("email"))
                has_phone = bool(res.get("phone"))
                has_li = bool(res.get("linkedin_url"))
                has_ig = bool(res.get("instagram_url"))

                status_parts = []
                if has_email:
                    status_parts.append(f"[green]✉ {res['email']}[/green]")
                if has_phone:
                    status_parts.append(f"[bold cyan]☎ {res['phone']}[/bold cyan]")
                if has_li:
                    status_parts.append("[blue]LI[/blue]")
                if has_ig:
                    status_parts.append("[magenta]IG[/magenta]")

                status_str = " | ".join(status_parts) if status_parts else "[dim]InMail/DM[/dim]"
                console.print(f"  [green]✓[/green] [{len(processed_leads):03d}/{target_count}] [{reg}] [bold white]{name[:20]}[/bold white] -> {status_str}")

                if len(processed_leads) >= target_count:
                    for f in futures:
                        f.cancel()
                    break

    console.print(f"\n[green]✓ Successfully enriched {len(processed_leads)} high-quality leads![/green]\n")

    # Step 3: Sort by Fit Score & Export
    console.print("[bold yellow][3/3] Ranking by Agency Fit Score & Generating Export Files...[/bold yellow]\n")
    processed_leads.sort(key=lambda x: x.get("agency_fit_score", 0), reverse=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    csv_timestamped = f"pragtify_leads_{timestamp}.csv"
    csv_latest = "pragtify_leads_latest.csv"
    wa_timestamped = f"whatsapp_campaign_{timestamp}.csv"
    wa_latest = "whatsapp_campaign_latest.csv"

    export_columns = [
        "full_name",
        "market_region",
        "agency_fit_score",
        "matched_services",
        "matched_portfolio",
        "email",
        "phone",
        "whatsapp_chat_link",
        "recommended_pitch",
        "company",
        "website",
        "linkedin_url",
        "instagram_url",
        "twitter_url",
        "detected_technologies",
        "cms_platform",
        "has_chat_widget",
        "tech_opportunities",
        "location",
        "bio",
        "username",
        "followers",
        "public_repos",
        "github_url"
    ]

    saved_csv_files = []
    for fname in [csv_timestamped, csv_latest]:
        try:
            with open(fname, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=export_columns, extrasaction="ignore")
                writer.writeheader()
                for row in processed_leads:
                    clean_row = row.copy()
                    if isinstance(clean_row.get("detected_technologies"), list):
                        clean_row["detected_technologies"] = " | ".join(clean_row["detected_technologies"])
                    if isinstance(clean_row.get("tech_opportunities"), list):
                        clean_row["tech_opportunities"] = " | ".join(clean_row["tech_opportunities"])
                    if not clean_row.get("github_url"):
                        clean_row["github_url"] = f"https://github.com/{clean_row.get('username', '')}"
                    writer.writerow(clean_row)
            saved_csv_files.append(fname)
        except PermissionError:
            alt_fname = f"pragtify_leads_100_{timestamp}.csv"
            try:
                with open(alt_fname, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=export_columns, extrasaction="ignore")
                    writer.writeheader()
                    for row in processed_leads:
                        clean_row = row.copy()
                        if isinstance(clean_row.get("detected_technologies"), list):
                            clean_row["detected_technologies"] = " | ".join(clean_row["detected_technologies"])
                        if isinstance(clean_row.get("tech_opportunities"), list):
                            clean_row["tech_opportunities"] = " | ".join(clean_row["tech_opportunities"])
                        if not clean_row.get("github_url"):
                            clean_row["github_url"] = f"https://github.com/{clean_row.get('username', '')}"
                        writer.writerow(clean_row)
                saved_csv_files.append(alt_fname)
            except Exception:
                pass

    # Export WhatsApp campaign for all leads with phones
    dispatcher = WhatsAppDispatcher()
    ready_leads = dispatcher.get_ready_leads(processed_leads, filter_sent=False)
    if ready_leads:
        for wfname in [wa_timestamped, wa_latest]:
            try:
                dispatcher.export_campaign_csv(ready_leads, wfname)
            except PermissionError:
                try:
                    dispatcher.export_campaign_csv(ready_leads, f"whatsapp_campaign_100_{timestamp}.csv")
                except Exception:
                    pass

    # Count stats
    total_leads = len(processed_leads)
    leads_with_email = sum(1 for l in processed_leads if l.get("email"))
    leads_with_phone = sum(1 for l in processed_leads if l.get("phone"))
    leads_with_li = sum(1 for l in processed_leads if l.get("linkedin_url"))
    leads_with_ig = sum(1 for l in processed_leads if l.get("instagram_url"))

    console.print(f"[bold green]✓ Master Lead Export saved to:[/bold green] [white]{csv_latest}[/white]")
    if ready_leads:
        console.print(f"[bold green]✓ WhatsApp Campaign Export saved to:[/bold green] [white]{wa_latest}[/white]")

    console.print(f"\n[bold cyan]=== Campaign Summary Stats ===[/bold cyan]")
    console.print(f"• Total Leads: [bold white]{total_leads}[/bold white]")
    console.print(f"• Leads with Direct Email: [bold green]{leads_with_email}[/bold green] ({(leads_with_email/total_leads)*100:.1f}%)")
    console.print(f"• Leads with Phone / WhatsApp: [bold cyan]{leads_with_phone}[/bold cyan] ({(leads_with_phone/total_leads)*100:.1f}%)")
    console.print(f"• Leads with LinkedIn Profile: [bold blue]{leads_with_li}[/bold blue] ({(leads_with_li/total_leads)*100:.1f}%)")
    console.print(f"• Leads with Instagram Profile: [bold magenta]{leads_with_ig}[/bold magenta] ({(leads_with_ig/total_leads)*100:.1f}%)")

    # Display Top 15 Preview
    table = Table(show_header=True, box=box.MINIMAL_HEAVY_HEAD, border_style="dim", padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Lead Name", style="bold white")
    table.add_column("Market", style="cyan")
    table.add_column("Fit Score", style="green")
    table.add_column("Email", style="yellow")
    table.add_column("Phone / WhatsApp", style="cyan")
    table.add_column("LinkedIn", style="blue")
    table.add_column("Matched Offering", style="white")

    for idx, l in enumerate(processed_leads[:15], 1):
        name = l.get("full_name") or l.get("username", "?")
        score = l.get("agency_fit_score", 0)
        score_style = "green" if score >= 70 else "yellow" if score >= 40 else "dim"
        email_str = l.get("email") or "—"
        phone_str = l.get("phone") or "—"
        li_str = "Yes" if l.get("linkedin_url") else "—"
        svc = (l.get("matched_services", "")).split(",")[0][:22]

        table.add_row(
            str(idx),
            name[:20],
            l.get("market_region", "N/A"),
            f"[{score_style}]{score}/100[/{score_style}]",
            email_str[:22],
            phone_str[:15],
            li_str,
            svc
        )

    console.print("\n")
    console.print(table)
    console.print()
    return csv_latest, wa_latest

if __name__ == "__main__":
    run_lead_generation(target_count=110)
