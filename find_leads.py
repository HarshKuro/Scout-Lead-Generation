import csv
import time
import os
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

from app.memory import AgencyMemory, LeadMatcher
from app.scrapers.discovery import LeadDiscoveryEngine
from app.scrapers.github import scrape_profile as scrape_github
from app.scrapers.enrichment import LeadEnricher
from app.scrapers.whatsapp_dispatcher import WhatsAppDispatcher

console = Console()

def run_lead_generation():
    console.print("\n[bold cyan]=== Starting Pragtify Lead Generation Engine ===[/bold cyan]\n")

    memory = AgencyMemory()
    matcher = LeadMatcher(memory)
    discovery = LeadDiscoveryEngine()
    enricher = LeadEnricher()

    console.print(f"[white]Agency Memory:[/white] [bold green]{memory.agency_name}[/bold green] | Location: [dim]{memory.location}[/dim] | Services: [green]{len(memory.services)}[/green] | Portfolio: [green]{len(memory.portfolio)}[/green]\n")

    # High-yield targets across India, Pakistan, and International markets
    search_queries = [
        # India (Bengaluru, Delhi, Mumbai, Gurgaon)
        {"region": "India", "query": 'site:github.com "founder" "Bengaluru"'},
        {"region": "India", "query": 'site:github.com "CEO" "Fintech" "Bengaluru"'},
        {"region": "India", "query": 'site:github.com "founder" "Mumbai"'},
        {"region": "India", "query": 'site:github.com "founder" "Delhi"'},

        # Pakistan (Lahore, Karachi, Islamabad)
        {"region": "Pakistan", "query": 'site:github.com "founder" "Lahore"'},
        {"region": "Pakistan", "query": 'site:github.com "CEO" "Karachi"'},
        {"region": "Pakistan", "query": 'site:github.com "CTO" "Islamabad"'},

        # International (US / UK / UAE)
        {"region": "International", "query": 'site:github.com "CTO" "AI" "San Francisco"'},
        {"region": "International", "query": 'site:github.com "founder" "SaaS" "New York"'},
        {"region": "International", "query": 'site:github.com "founder" "London"'},
        {"region": "International", "query": 'site:github.com "founder" "Dubai"'},
    ]

    discovered_usernames = []
    seen = set()

    console.print("[bold yellow][1/3] Discovering Verified Founders & Tech Decision Makers...[/bold yellow]")

    for sq in search_queries:
        q = sq["query"]
        console.print(f"  [dim]Searching ({sq['region']}):[/dim] [white]{q}[/white]")
        found = discovery.search_dork(q, max_results=3)
        for item in found:
            u = item.get("username")
            if u and u.lower() not in seen:
                seen.add(u.lower())
                discovered_usernames.append({"username": u, "region": sq["region"]})
        time.sleep(0.5)

    console.print(f"\n[green]✓ Discovered {len(discovered_usernames)} target decision-maker profiles[/green]\n")

    # Step 2: Scrape Profiles & Enrich Contacts / Tech Stacks
    console.print("[bold yellow][2/3] Scraping Profiles, Detecting Tech Stacks & Contacts...[/bold yellow]")
    enriched_leads = []

    for item in discovered_usernames:
        u = item["username"]
        try:
            profile = scrape_github(u)
            if profile and (profile.get("full_name") or profile.get("bio") or profile.get("company") or profile.get("website")):
                # Set location fallback if missing
                if not profile.get("location"):
                    profile["location"] = item["region"]

                enriched = enricher.enrich_lead(profile)
                enriched_leads.append(enriched)
                lead_name = enriched.get("full_name") or u
                comp = enriched.get("company") or "Independent"
                email_status = f"[green]{enriched['email']}[/green]" if enriched.get("email") else "[dim]No email[/dim]"
                console.print(f"  [green]✓[/green] [bold white]{lead_name}[/bold white] | {comp} | {email_status}")
            else:
                console.print(f"  [dim]• Skipped {u} (minimal public bio)[/dim]")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed {u}: {e}")

        time.sleep(0.5)

    console.print(f"\n[green]✓ Enriched {len(enriched_leads)} high-quality lead profiles[/green]\n")

    # Step 3: Match with Pragtify Agency Memory & Craft Pitches
    console.print("[bold yellow][3/3] Matching against Pragtify Memory & Generating Pitches...[/bold yellow]\n")
    final_leads = []

    for lead in enriched_leads:
        matched = matcher.match_lead(lead)
        final_leads.append(matched)

    # Sort descending by Agency Fit Score
    final_leads.sort(key=lambda x: x.get("agency_fit_score", 0), reverse=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    csv_filename = f"pragtify_leads_{timestamp}.csv"
    wa_csv_filename = f"whatsapp_campaign_{timestamp}.csv"

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

    with open(csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=export_columns, extrasaction="ignore")
        writer.writeheader()
        for row in final_leads:
            clean_row = row.copy()
            if isinstance(clean_row.get("detected_technologies"), list):
                clean_row["detected_technologies"] = " | ".join(clean_row["detected_technologies"])
            if isinstance(clean_row.get("tech_opportunities"), list):
                clean_row["tech_opportunities"] = " | ".join(clean_row["tech_opportunities"])
            if not clean_row.get("github_url"):
                clean_row["github_url"] = f"https://github.com/{clean_row.get('username', '')}"
            writer.writerow(clean_row)

    # Export WhatsApp campaign if any phone numbers found
    dispatcher = WhatsAppDispatcher()
    ready_leads = dispatcher.get_ready_leads(final_leads, filter_sent=False)
    if ready_leads:
        dispatcher.export_campaign_csv(ready_leads, wa_csv_filename)

    console.print(f"[bold green]✓ Master Lead Export saved to:[/bold green] [white]{csv_filename}[/white]")
    if ready_leads:
        console.print(f"[bold green]✓ WhatsApp Campaign Export saved to:[/bold green] [white]{wa_csv_filename}[/white]\n")

    # Display Pretty Table
    table = Table(show_header=True, box=box.MINIMAL_HEAVY_HEAD, border_style="dim", padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Lead Name", style="bold white")
    table.add_column("Market", style="cyan")
    table.add_column("Fit Score", style="green")
    table.add_column("Verified Email", style="yellow")
    table.add_column("Matched Offering", style="white")
    table.add_column("Company / Venture", style="dim")

    for idx, l in enumerate(final_leads, 1):
        name = l.get("full_name") or l.get("username", "?")
        score = l.get("agency_fit_score", 0)
        score_style = "green" if score >= 70 else "yellow" if score >= 40 else "dim"
        email_str = l.get("email") or "InMail/DM"
        svc = (l.get("matched_services", "")).split(",")[0][:25]
        comp = l.get("company") or "Founder"
        table.add_row(
            str(idx),
            name[:22],
            l.get("market_region", "N/A"),
            f"[{score_style}]{score}/100[/{score_style}]",
            email_str[:25],
            svc,
            comp[:25]
        )

    console.print(table)
    console.print()
    return csv_filename, wa_csv_filename

if __name__ == "__main__":
    run_lead_generation()
