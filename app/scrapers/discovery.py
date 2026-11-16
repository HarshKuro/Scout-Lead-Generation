import re
import urllib.parse
import logging
from typing import List, Dict, Any, Optional

import httpx
from app.scrapers.stealth import random_user_agent, random_delay

logger = logging.getLogger(__name__)


class LeadDiscoveryEngine:
    """
    Search & OSINT Discovery Engine for Scout.
    Executes search dorks (e.g. Google/DuckDuckGo X-Ray search) to discover target decision makers
    across LinkedIn, Instagram, GitHub, and websites without requiring paid search APIs.
    """

    DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
    BING_URL = "https://www.bing.com/search"

    PLATFORM_PATTERNS = {
        "linkedin": r"linkedin\.com/in/([a-zA-Z0-9_\-\.]+)",
        "instagram": r"instagram\.com/([a-zA-Z0-9_\.]+)",
        "github": r"github\.com/([a-zA-Z0-9_\-]+)",
        "twitter": r"(?:twitter|x)\.com/([a-zA-Z0-9_]+)",
    }

    IGNORE_SLUGS = {
        "instagram": ["p", "stories", "explore", "reels", "about", "developer", "legal", "terms"],
        "github": ["features", "topics", "collections", "pricing", "security", "about", "orgs", "explore", "trending"],
        "linkedin": ["posts", "pulse", "company", "school", "jobs", "feed", "learning"],
        "twitter": ["home", "explore", "notifications", "messages", "settings", "search"],
    }

    def search_dork(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """
        Execute a search dork query and extract matching leads and profile links.
        """
        results = []
        platform = self.detect_query_platform(query)

        # 1. Try DuckDuckGo HTML
        results = self._search_duckduckgo(query, max_results)

        # 2. Fallback to Bing if DDG returned empty
        if not results:
            logger.info("DuckDuckGo returned no results, attempting Bing fallback...")
            results = self._search_bing(query, max_results)

        # Extract handles and clean results
        cleaned_leads = []
        seen_usernames = set()

        for r in results:
            url = r.get("url", "")
            username = self.extract_username_from_url(url, platform)

            if username:
                if username.lower() not in seen_usernames:
                    seen_usernames.add(username.lower())
                    cleaned_leads.append({
                        "username": username,
                        "platform": platform,
                        "title": r.get("title", ""),
                        "url": url,
                        "snippet": r.get("snippet", ""),
                    })
            else:
                # General result (e.g. company domain)
                cleaned_leads.append({
                    "username": "",
                    "platform": platform or "web",
                    "title": r.get("title", ""),
                    "url": url,
                    "snippet": r.get("snippet", ""),
                })

        return cleaned_leads[:max_results]

    def detect_query_platform(self, query: str) -> str:
        q = query.lower()
        if "linkedin.com" in q:
            return "linkedin"
        if "instagram.com" in q:
            return "instagram"
        if "github.com" in q:
            return "github"
        if "twitter.com" in q or "x.com" in q:
            return "twitter"
        return "general"

    def extract_username_from_url(self, url: str, platform: str) -> Optional[str]:
        if not url:
            return None

        # Clean redirects (e.g. DuckDuckGo /uddg?uddg=... or Bing)
        if "duckduckgo.com/l/?uddg=" in url:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            if "uddg" in parsed and parsed["uddg"]:
                url = parsed["uddg"][0]

        plat = platform if platform != "general" else self.detect_query_platform(url)
        pattern = self.PLATFORM_PATTERNS.get(plat)
        if not pattern:
            return None

        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            candidate = match.group(1).rstrip("/").split("?")[0].split("#")[0].strip()
            ignored = self.IGNORE_SLUGS.get(plat, [])
            if candidate.lower() not in ignored and len(candidate) > 1:
                return candidate

        return None

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        leads = []
        try:
            headers = {
                "User-Agent": random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            resp = httpx.post(
                self.DUCKDUCKGO_HTML_URL,
                data={"q": query},
                headers=headers,
                timeout=12,
                follow_redirects=True
            )

            if resp.status_code == 200:
                html = resp.text

                # Parse organic result links
                # DDG HTML results typically have <a class="result__url" href="..."> or <a class="result__snippet" ...>
                # and <h2 class="result__title"><a class="result__a" href="...">
                results = re.findall(
                    r'<a[^>]+class=[\'"][^\'"]*result__a[^\'"]*[\'"][^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>',
                    html,
                    re.DOTALL | re.IGNORECASE
                )

                snippets = re.findall(
                    r'<a[^>]+class=[\'"][^\'"]*result__snippet[^\'"]*[\'"][^>]*>(.*?)</a>',
                    html,
                    re.DOTALL | re.IGNORECASE
                )

                for idx, (raw_url, raw_title) in enumerate(results):
                    # Unescape HTML entities
                    title = re.sub(r'<[^>]+>', '', raw_title).strip()
                    title = title.replace('&amp;', '&').replace('&quot;', '"').replace('&#x27;', "'")

                    # Extract actual target URL from DDG redirect if present
                    actual_url = raw_url
                    if "/l/?uddg=" in raw_url:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                        if "uddg" in parsed and parsed["uddg"]:
                            actual_url = parsed["uddg"][0]

                    snippet_text = ""
                    if idx < len(snippets):
                        snippet_text = re.sub(r'<[^>]+>', '', snippets[idx]).strip()

                    leads.append({
                        "title": title,
                        "url": actual_url,
                        "snippet": snippet_text
                    })

                    if len(leads) >= max_results:
                        break

        except Exception as e:
            logger.debug(f"DuckDuckGo search error: {e}")

        return leads

    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, str]]:
        leads = []
        try:
            headers = {
                "User-Agent": random_user_agent(),
                "Accept-Language": "en-US,en;q=0.9",
            }
            resp = httpx.get(
                self.BING_URL,
                params={"q": query},
                headers=headers,
                timeout=12,
                follow_redirects=True
            )

            if resp.status_code == 200:
                html = resp.text

                # Match <li class="b_algo"> ... <h2><a href="URL">TITLE</a></h2> ... <p>SNIPPET</p>
                blocks = re.findall(
                    r'<h2><a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a></h2>',
                    html,
                    re.DOTALL | re.IGNORECASE
                )

                for raw_url, raw_title in blocks:
                    title = re.sub(r'<[^>]+>', '', raw_title).strip()
                    leads.append({
                        "title": title,
                        "url": raw_url,
                        "snippet": ""
                    })
                    if len(leads) >= max_results:
                        break
        except Exception as e:
            logger.debug(f"Bing search error: {e}")

        return leads

    @classmethod
    def build_dork(cls, platform: str, role: str, industry: str, location: str) -> str:
        """
        Helper method to construct a Google/DuckDuckGo X-Ray dork query.
        """
        site_map = {
            "linkedin": "site:linkedin.com/in",
            "instagram": "site:instagram.com",
            "github": "site:github.com",
            "twitter": "site:twitter.com OR site:x.com",
        }

        site_part = site_map.get(platform.lower(), "site:linkedin.com/in")
        parts = [site_part]

        if role:
            # Handle comma separated or single
            roles = [r.strip() for r in role.split(",") if r.strip()]
            if len(roles) > 1:
                parts.append("(" + " OR ".join([f'"{r}"' for r in roles]) + ")")
            else:
                parts.append(f'"{roles[0]}"')

        if industry:
            parts.append(f'"{industry.strip()}"')

        if location:
            parts.append(f'"{location.strip()}"')

        return " ".join(parts)
