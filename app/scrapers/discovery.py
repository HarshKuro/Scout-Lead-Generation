import re
import html
import base64
import urllib.parse
import logging
from typing import List, Dict, Any, Optional

import httpx
from app.scrapers.stealth import random_user_agent, random_delay

logger = logging.getLogger(__name__)


class LeadDiscoveryEngine:
    """
    Search & OSINT Discovery Engine for Scout.
    Executes search dorks (e.g. Google/Bing/GitHub API) to discover target decision makers
    across LinkedIn, GitHub, Instagram, and websites.
    """

    DUCKDUCKGO_HTML_URL = "https://html.duckduckgo.com/html/"
    BING_URL = "https://www.bing.com/search"
    GITHUB_API_SEARCH = "https://api.github.com/search/users"

    PLATFORM_PATTERNS = {
        "linkedin": r"linkedin\.com/in/([a-zA-Z0-9_\-\.]+)",
        "instagram": r"instagram\.com/([a-zA-Z0-9_\.]+)",
        "github": r"github\.com/([a-zA-Z0-9_\-]+)",
        "twitter": r"(?:twitter|x)\.com/([a-zA-Z0-9_]+)",
    }

    IGNORE_SLUGS = {
        "instagram": ["p", "stories", "explore", "reels", "about", "developer", "legal", "terms"],
        "github": ["features", "topics", "collections", "pricing", "security", "about", "orgs", "explore", "trending", "search"],
        "linkedin": ["posts", "pulse", "company", "school", "jobs", "feed", "learning", "in"],
        "twitter": ["home", "explore", "notifications", "messages", "settings", "search"],
    }

    BLACKLIST_DOMAINS = [
        "merriam-webster.com", "dictionary.cambridge.org", "collinsdictionary.com",
        "wikipedia.org", "imdb.com", "wiktionary.org", "thefreedictionary.com"
    ]

    def search_dork(self, query: str, max_results: int = 25) -> List[Dict[str, Any]]:
        """
        Execute a search dork query and extract matching leads and profile links.
        """
        results = []
        platform = self.detect_query_platform(query)

        # If targeting GitHub profiles, use GitHub Search API directly (most reliable)
        if platform == "github":
            results = self._search_github_api(query, max_results)

        # If not enough results or other platforms, query Bing / DDG
        if len(results) < max_results:
            bing_res = self._search_bing(query, max_results - len(results))
            results.extend(bing_res)

        if not results:
            ddg_res = self._search_duckduckgo(query, max_results)
            results.extend(ddg_res)

        # Extract handles and clean results
        cleaned_leads = []
        seen_usernames = set()

        for r in results:
            url = r.get("url", "")

            # Filter blacklist domains
            if any(b in url.lower() for b in self.BLACKLIST_DOMAINS):
                continue

            username = r.get("username") or self.extract_username_from_url(url, platform)

            if username:
                if username.lower() not in seen_usernames and username.lower() not in self.IGNORE_SLUGS.get(platform, []):
                    seen_usernames.add(username.lower())
                    cleaned_leads.append({
                        "username": username,
                        "platform": platform,
                        "title": r.get("title", ""),
                        "url": url,
                        "snippet": r.get("snippet", ""),
                    })
            elif platform == "general":
                cleaned_leads.append({
                    "username": "",
                    "platform": "web",
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

        # Decode Bing redirect URL if present
        url = self._decode_bing_url(url)

        # Clean redirects (e.g. DuckDuckGo /uddg?uddg=...)
        if "duckduckgo.com/l/?uddg=" in url or "/uddg=" in url:
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

    def _decode_bing_url(self, bing_url: str) -> str:
        clean = html.unescape(bing_url).replace('&amp;', '&')
        if "/ck/a?" in clean:
            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(clean).query)
            u_val = parsed.get("u", [None])[0]
            if u_val:
                raw_b64 = u_val[2:] if u_val.startswith("a1") else u_val
                pad = len(raw_b64) % 4
                if pad:
                    raw_b64 += "=" * (4 - pad)
                try:
                    decoded = base64.b64decode(raw_b64).decode("utf-8", errors="ignore")
                    return decoded
                except Exception:
                    pass
        return clean

    def _search_github_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        leads = []
        clean_q = query.replace('site:github.com', '').strip()
        location = ""
        for loc in ["Bengaluru", "Bangalore", "Mumbai", "Delhi", "Gurgaon", "Noida", "Hyderabad", "Chennai",
                    "Pune", "Lahore", "Karachi", "Islamabad", "San Francisco", "New York", "London", "Dubai", "Singapore"]:
            if loc.lower() in clean_q.lower():
                location = loc
                break

        terms = [w.strip(' "\'') for w in clean_q.split() if w.strip(' "\'') and w.lower() != location.lower()]
        search_param = " ".join(terms)
        if location:
            search_param += f' location:"{location}"'

        try:
            headers = {
                "User-Agent": random_user_agent(),
                "Accept": "application/vnd.github.v3+json"
            }

            resp = httpx.get(
                self.GITHUB_API_SEARCH,
                params={"q": search_param, "per_page": min(max_results, 30)},
                headers=headers,
                timeout=12
            )

            if resp.status_code == 200:
                items = resp.json().get("items", [])
                for item in items:
                    leads.append({
                        "username": item.get("login"),
                        "platform": "github",
                        "title": f"{item.get('login')} (GitHub User)",
                        "url": item.get("html_url"),
                        "snippet": ""
                    })
                    if len(leads) >= max_results:
                        break
        except Exception as e:
            logger.debug(f"GitHub API search error: {e}")

        # If rate-limited or insufficient results, fallback to GitHub HTML search
        if len(leads) < max_results:
            html_leads = self._search_github_html(search_param or clean_q, max_results - len(leads))
            for hl in html_leads:
                if not any(l['username'].lower() == hl['username'].lower() for l in leads):
                    leads.append(hl)

        return leads

    def _search_github_html(self, search_param: str, max_results: int) -> List[Dict[str, Any]]:
        leads = []
        try:
            headers = {
                "User-Agent": random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            pages_needed = max(1, (max_results // 10) + 1)
            for p in range(1, pages_needed + 1):
                resp = httpx.get("https://github.com/search", params={"q": search_param, "type": "users", "p": p}, headers=headers, timeout=10)
                if resp.status_code == 200:
                    links = re.findall(r'href="/([a-zA-Z0-9_\-]+)"', resp.text)
                    ignored = {'features', 'pricing', 'login', 'signup', 'explore', 'topics', 'about', 'search', 'contact', 'security', 'orgs'}
                    for u in links:
                        if u.lower() not in ignored and not u.startswith('_') and len(u) > 1:
                            if not any(l['username'].lower() == u.lower() for l in leads):
                                leads.append({
                                    "username": u,
                                    "platform": "github",
                                    "title": f"{u} (GitHub User)",
                                    "url": f"https://github.com/{u}",
                                    "snippet": ""
                                })
                                if len(leads) >= max_results:
                                    break
                if len(leads) >= max_results:
                    break
        except Exception as e:
            logger.debug(f"GitHub HTML search error: {e}")
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
                page_html = resp.text

                # Match <h2><a href="URL">TITLE</a></h2>
                blocks = re.findall(
                    r'<h2>\s*<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>',
                    page_html,
                    re.DOTALL | re.IGNORECASE
                )

                for raw_url, raw_title in blocks:
                    decoded = self._decode_bing_url(raw_url)
                    if any(b in decoded.lower() for b in self.BLACKLIST_DOMAINS):
                        continue

                    title = re.sub(r'<[^>]+>', '', raw_title).strip()
                    title = html.unescape(title)

                    leads.append({
                        "title": title,
                        "url": decoded,
                        "snippet": ""
                    })
                    if len(leads) >= max_results:
                        break
        except Exception as e:
            logger.debug(f"Bing search error: {e}")

        return leads

    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        leads = []
        try:
            headers = {
                "User-Agent": random_user_agent(),
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
                results = re.findall(
                    r'<a[^>]+class=[\'"][^\'"]*result__a[^\'"]*[\'"][^>]+href=[\'"]([^\'"]+)[\'"][^>]*>(.*?)</a>',
                    resp.text,
                    re.DOTALL | re.IGNORECASE
                )

                for raw_url, raw_title in results:
                    actual_url = raw_url
                    if "/l/?uddg=" in raw_url:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                        if "uddg" in parsed and parsed["uddg"]:
                            actual_url = parsed["uddg"][0]

                    if any(b in actual_url.lower() for b in self.BLACKLIST_DOMAINS):
                        continue

                    title = re.sub(r'<[^>]+>', '', raw_title).strip()
                    title = html.unescape(title)

                    leads.append({
                        "title": title,
                        "url": actual_url,
                        "snippet": ""
                    })

                    if len(leads) >= max_results:
                        break
        except Exception as e:
            logger.debug(f"DuckDuckGo search error: {e}")

        return leads

    @classmethod
    def build_dork(cls, platform: str, role: str, industry: str, location: str) -> str:
        site_map = {
            "linkedin": "site:linkedin.com/in",
            "instagram": "site:instagram.com",
            "github": "site:github.com",
            "twitter": "site:twitter.com OR site:x.com",
        }

        site_part = site_map.get(platform.lower(), "site:linkedin.com/in")
        parts = [site_part]

        if role:
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
