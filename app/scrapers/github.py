"""
GitHub Profile Scraper

Scrapes public GitHub user profiles using mobile/desktop web HTML parsing (unlimited)
with API fallback. Extracts bio, company, location, website, email, and social handles
(LinkedIn, Instagram, X/Twitter).
"""

import requests
import html
from typing import Dict, Optional
import logging
import re

from app.scrapers.stealth import get_requests_proxies, random_user_agent
from app.scrapers.utils import extract_email

logger = logging.getLogger(__name__)


def scrape_profile(username: str) -> Optional[Dict]:
    """Fetch GitHub profile data for a username via web HTML (unlimited) with API fallback."""
    # 1. Try HTML scraping first (no 60 req/hr rate limit)
    html_profile = _scrape_profile_html(username)
    if html_profile:
        return html_profile

    # 2. Fallback to REST API
    return _scrape_profile_api(username)


def _scrape_profile_html(username: str) -> Optional[Dict]:
    """Scrape GitHub profile page HTML directly."""
    url = f'https://github.com/{username}'
    headers = {
        'User-Agent': random_user_agent(),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        r = requests.get(url, headers=headers, timeout=10, proxies=get_requests_proxies())
        if r.status_code == 404:
            return None
        if r.status_code != 200:
            return None

        text = r.text

        # Full name
        name_match = re.search(r'<span class="p-name[^"]*"[^>]*>(.*?)</span>', text, re.DOTALL)
        full_name = html.unescape(name_match.group(1)).strip() if name_match else username

        # Bio
        bio_match = re.search(r'<div class="p-note[^"]*"[^>]*>(.*?)</div>', text, re.DOTALL)
        bio = ""
        if bio_match:
            bio = re.sub(r'<[^>]+>', ' ', bio_match.group(1)).strip()
            bio = html.unescape(re.sub(r'\s+', ' ', bio))

        # Company
        comp_match = re.search(r'itemprop="worksFor"[^>]*>.*?<span class="p-org"[^>]*>(.*?)</span>', text, re.DOTALL)
        company = html.unescape(re.sub(r'<[^>]+>', '', comp_match.group(1))).strip() if comp_match else ""

        # Location
        loc_match = re.search(r'itemprop="homeLocation"[^>]*>.*?<span class="p-label"[^>]*>(.*?)</span>', text, re.DOTALL)
        location = html.unescape(re.sub(r'<[^>]+>', '', loc_match.group(1))).strip() if loc_match else ""

        # Social links & Website from vcard-details
        website = ""
        linkedin_url = ""
        instagram_url = ""
        twitter_url = ""
        email = ""

        # Email in mailto
        mailto = re.search(r'href="mailto:([^"]+)"', text)
        if mailto:
            email = mailto.group(1).strip()
        elif bio:
            email = _extract_email(bio)

        # Direct links in vcard
        vcard = re.search(r'<ul class="vcard-details"[^>]*>(.*?)</ul>', text, re.DOTALL)
        if vcard:
            links = re.findall(r'href="([^"]+)"', vcard.group(1))
            for l in links:
                l_lower = l.lower()
                if "linkedin.com/in/" in l_lower and not linkedin_url:
                    linkedin_url = l
                elif "instagram.com/" in l_lower and not instagram_url:
                    instagram_url = l
                elif ("twitter.com/" in l_lower or "x.com/" in l_lower) and not twitter_url:
                    twitter_url = l
                elif not website and l.startswith("http") and not any(x in l_lower for x in ["github.com", "linkedin.com", "instagram.com", "twitter.com", "x.com"]):
                    website = l

        # Followers
        followers_match = re.search(r'href="https://github.com/[^"]+\?tab=followers"[^>]*>.*?<span class="text-bold[^"]*"[^>]*>(.*?)</span>', text, re.DOTALL)
        followers = followers_match.group(1).strip() if followers_match else "0"

        # Public repos
        repos_match = re.search(r'href="https://github.com/[^"]+\?tab=repositories"[^>]*>.*?<span class="Counter[^"]*"[^>]*>(.*?)</span>', text, re.DOTALL)
        repos = repos_match.group(1).strip() if repos_match else "0"

        if not any([full_name, bio, company, website, linkedin_url, email]):
            return None

        from app.scrapers.utils import parse_abbreviated_number
        follower_num = parse_abbreviated_number(followers) if isinstance(followers, str) else followers
        repos_num = parse_abbreviated_number(repos) if isinstance(repos, str) else repos

        return {
            'username': username,
            'full_name': full_name,
            'bio': bio,
            'email': email,
            'company': company.lstrip('@'),
            'location': location,
            'website': website,
            'linkedin_url': linkedin_url,
            'instagram_url': instagram_url,
            'twitter_url': twitter_url,
            'follower_count': follower_num,
            'following_count': 0,
            'public_repos': repos_num,
            'is_hireable': False,
            'platform': 'github',
            'profile_url': f'https://github.com/{username}',
        }
    except Exception as e:
        logger.debug(f"GitHub HTML scrape error for @{username}: {e}")
        return None


def _scrape_profile_api(username: str) -> Optional[Dict]:
    """Fetch GitHub profile data for a username via API."""
    url = f'https://api.github.com/users/{username}'
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': random_user_agent(),
    }

    try:
        r = requests.get(url, headers=headers, timeout=10, proxies=get_requests_proxies())
        if r.status_code != 200:
            return None

        data = r.json()
        bio = data.get('bio') or ''

        return {
            'username': data.get('login', username),
            'full_name': data.get('name') or '',
            'bio': bio,
            'email': data.get('email') or _extract_email(bio),
            'company': (data.get('company') or '').lstrip('@'),
            'location': data.get('location') or '',
            'website': data.get('blog') or '',
            'twitter_url': f"https://x.com/{data['twitter_username']}" if data.get('twitter_username') else '',
            'follower_count': data.get('followers', 0),
            'following_count': data.get('following', 0),
            'public_repos': data.get('public_repos', 0),
            'is_hireable': data.get('hireable') or False,
            'platform': 'github',
            'profile_url': data.get('html_url', f'https://github.com/{username}'),
        }
    except Exception:
        return None


_extract_email = extract_email
