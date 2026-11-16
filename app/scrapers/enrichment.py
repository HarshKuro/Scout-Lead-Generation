import re
import dns.resolver
import smtplib
import socket
import logging
import threading
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

from app.scrapers.stealth import random_user_agent, random_delay

logger = logging.getLogger(__name__)

EMAIL_RE = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
EMAIL_BLACKLIST = ['example.com', 'test.com', 'email.com', 'youremail.com',
                   'sentry.io', 'wixpress.com', 'googleapis.com', 'w3.org',
                   'schema.org', 'gravatar.com', 'wordpress.com']
FILE_EXT_BLACKLIST = ['.png', '.jpg', '.gif', '.css', '.js', '.svg', '.webp', '.ico']


class LeadEnricher:

    def __init__(self, hunter_api_key: Optional[str] = None):
        self.hunter_api_key = hunter_api_key
        self._domain_pattern_cache: Dict[str, Optional[str]] = {}
        self._cache_lock = threading.Lock()

    def enrich_lead(self, lead_data: Dict) -> Dict:
        enriched = lead_data.copy()
        email_candidates = []

        # Check existing email / phone on lead profile (e.g. from vcard or search)
        if lead_data.get('email') and self._is_valid_email(lead_data['email']):
            email_candidates.append((lead_data['email'], 'profile'))
        if lead_data.get('phone') and not enriched.get('phone'):
            enriched['phone'] = lead_data['phone']

        # Extract contacts from bio
        bio_contacts = self._extract_from_text(lead_data.get('bio', ''))
        if bio_contacts['email']:
            email_candidates.append((bio_contacts['email'], 'bio'))
        if bio_contacts['phone'] and not enriched.get('phone'):
            enriched['phone'] = bio_contacts['phone']

        # Extract contacts from search snippet if present
        if lead_data.get('snippet'):
            snip_contacts = self._extract_from_text(lead_data.get('snippet', ''))
            if snip_contacts['email']:
                email_candidates.append((snip_contacts['email'], 'snippet'))
            if snip_contacts['phone'] and not enriched.get('phone'):
                enriched['phone'] = snip_contacts['phone']

        website = lead_data.get('website', '')
        site_emails = []

        social_only_domains = ['youtube.com', 'youtu.be', 'twitter.com', 'x.com', 'facebook.com', 'spotify.com']
        website_is_useful = website and not any(d in website.lower() for d in social_only_domains)

        if website_is_useful:
            site_info = self._deep_scrape_website(website)
            site_emails = site_info.get('all_emails', [])

            if site_info.get('tech_analysis'):
                ta = site_info['tech_analysis']
                enriched['detected_technologies'] = ta.get('detected_technologies', [])
                enriched['cms_platform'] = ta.get('cms', '')
                enriched['has_chat_widget'] = ta.get('has_chat_widget', False)
                enriched['chat_widget'] = ta.get('chat_widget', '')
                enriched['tech_opportunities'] = ta.get('opportunities', [])
                enriched['tech_summary'] = ta.get('tech_summary', '')

            if site_info['email']:
                email_candidates.append((site_info['email'], 'website'))
            if site_info['phone'] and not enriched.get('phone'):
                enriched['phone'] = site_info['phone']

        company_domain = None
        if not website_is_useful or not site_emails:
            company_domain = self._find_company_domain(lead_data)
            if company_domain:
                enriched['company_domain'] = company_domain
                if not website_is_useful:
                    site_info = self._deep_scrape_website('https://' + company_domain)
                    site_emails = site_info.get('all_emails', [])
                    if site_info.get('tech_analysis'):
                        ta = site_info['tech_analysis']
                        enriched['detected_technologies'] = ta.get('detected_technologies', [])
                        enriched['cms_platform'] = ta.get('cms', '')
                        enriched['has_chat_widget'] = ta.get('has_chat_widget', False)
                        enriched['chat_widget'] = ta.get('chat_widget', '')
                        enriched['tech_opportunities'] = ta.get('opportunities', [])
                        enriched['tech_summary'] = ta.get('tech_summary', '')
                    if site_info['email']:
                        email_candidates.append((site_info['email'], 'website'))
                    if site_info['phone'] and not enriched.get('phone'):
                        enriched['phone'] = site_info['phone']

        work_domain = company_domain or (self._extract_domain(website) if website_is_useful else None)

        if lead_data.get('full_name') and work_domain:
            pattern_email = self._predict_email_from_pattern(
                lead_data['full_name'], 'https://' + work_domain, site_emails
            )
            if pattern_email:
                email_candidates.append((pattern_email, 'pattern'))

        if not email_candidates and lead_data.get('full_name') and work_domain:
            candidates = self._generate_email_candidates(lead_data['full_name'], 'https://' + work_domain)
            for c in candidates[:5]:
                smtp = self._verify_email_smtp(c)
                if smtp['exists'] and not smtp['accept_all']:
                    email_candidates.append((c, 'smtp_guess'))
                    break

        if self.hunter_api_key and lead_data.get('full_name') and website:
            hunter_email = self._find_with_hunter(
                lead_data.get('full_name'), website
            )
            if hunter_email:
                email_candidates.append((hunter_email, 'hunter.io'))

        bio_links = self._extract_bio_links(lead_data.get('bio', ''))
        if bio_links:
            for link in bio_links[:3]:
                link_info = self._scrape_link_page(link)
                if link_info['email']:
                    email_candidates.append((link_info['email'], 'bio_link'))
                if link_info['phone'] and not enriched.get('phone'):
                    enriched['phone'] = link_info['phone']

        if email_candidates:
            seen = set()
            unique = []
            for email, source in email_candidates:
                if email.lower() not in seen:
                    seen.add(email.lower())
                    unique.append((email, source))

            best = None
            best_score = -1

            for email, source in unique:
                scored = self._score_and_verify_email(
                    email, source,
                    pattern_match=(source == 'pattern'),
                    site_emails_count=len(site_emails)
                )
                if scored['score'] > best_score:
                    best_score = scored['score']
                    best = scored

            if best:
                enriched['email'] = best['email']
                enriched['email_score'] = best['score']
                enriched['email_source'] = best['source']
                enriched['email_verified'] = best['verified']

        if not enriched.get('email') and lead_data.get('full_name') and work_domain:
            enriched['possible_emails'] = self._generate_email_candidates(
                lead_data['full_name'], 'https://' + work_domain
            )

        enriched['lead_score'] = self._calculate_lead_score(enriched)
        return enriched

    def _extract_from_text(self, text: str) -> Dict[str, Optional[str]]:
        result = {'email': None, 'phone': None}
        if not text:
            return result

        emails = re.findall(EMAIL_RE, text)
        valid = [e for e in emails if self._is_valid_email(e)]
        if valid:
            result['email'] = valid[0]

        phone = self._extract_phone_from_text(text)
        if phone:
            result['phone'] = phone

        return result

    def _is_valid_email(self, email: str) -> bool:
        lower = email.lower()
        if any(b in lower for b in EMAIL_BLACKLIST):
            return False
        if any(lower.endswith(ext) for ext in FILE_EXT_BLACKLIST):
            return False
        return True

    def _extract_phone_from_text(self, text: str) -> Optional[str]:
        if not text:
            return None

        # 1. WhatsApp direct links (wa.me/91... or wa.me/92...)
        wa_links = re.findall(r'(?:wa\.me/|api\.whatsapp\.com/(?:send\?phone=|send/\?phone=))(\+?\d+)', text, re.IGNORECASE)
        for num in wa_links:
            clean = re.sub(r'[^\d+]', '', num)
            if not clean.startswith('+'):
                clean = '+' + clean
            if 11 <= len(clean) <= 16:
                return clean

        # 2. tel: links
        tel_links = re.findall(r'href=["\']tel:([+\d\s\-().]+)', text, re.IGNORECASE)
        for tel in tel_links:
            clean = re.sub(r'[^\d+]', '', tel)
            if 10 <= len(clean) <= 15:
                return clean if clean.startswith('+') else ('+' + clean)

        # 3. Labeled contact/phone/WhatsApp strings in text
        labeled = re.findall(r'(?:whatsapp|call|phone|mobile|mob|contact|ph)[^\w\n]{1,15}(\+?[0-9\s\-().]{8,18})', text, re.IGNORECASE)
        for raw in labeled:
            clean = re.sub(r'[^\d+]', '', raw)
            if 10 <= len(clean) <= 15:
                return clean if clean.startswith('+') else ('+' + clean)

        # 4. Pakistani mobile numbers (+92 3XX XXXXXXX or 03XX XXXXXXX)
        pk_matches = re.findall(r'(?:(?:\+|00)92[\s.-]?|0)(3\d{2}[\s.-]?\d{7})', text)
        for pkm in pk_matches:
            digits = re.sub(r'[^\d]', '', pkm)
            if len(digits) == 10:
                return f'+92{digits}'

        # 5. Indian mobile numbers (+91 9XXXX XXXXX, +91-9XXXXXXXXX, or 09XXXXXXXXX)
        in_matches = re.findall(r'(?:(?:\+|00)91[\s.-]?|0)?([6-9]\d{4}[\s.-]?\d{5})', text)
        for inm in in_matches:
            digits = re.sub(r'[^\d]', '', inm)
            if len(digits) == 10:
                return f'+91{digits}'

        # 6. International / US phone numbers
        intl_patterns = [
            r'\+1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+(?:44|971|65|61|49|33)[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
        ]
        for pattern in intl_patterns:
            phones = re.findall(pattern, text)
            for phone in phones:
                clean = re.sub(r'[^\d+]', '', phone)
                if 10 <= len(clean) <= 16:
                    return clean if clean.startswith('+') else ('+' + clean)

        return None

    def _fetch_page(self, url: str) -> Optional[str]:
        text, _, _ = self._fetch_page_with_meta(url)
        return text

    def _fetch_page_with_meta(self, url: str) -> Tuple[Optional[str], Dict[str, str], float]:
        import time as _t
        start = _t.time()
        try:
            if not url.startswith('http'):
                url = 'https://' + url
            resp = httpx.get(url, timeout=4, headers={
                'User-Agent': random_user_agent()
            }, follow_redirects=True)
            load_time = _t.time() - start
            if resp.status_code == 200:
                return resp.text, dict(resp.headers), load_time
        except Exception as e:
            logger.debug(f"Error fetching {url}: {e}")
        return None, {}, 0.0

    def _deep_scrape_website(self, website: str) -> Dict:
        result = {'email': None, 'phone': None, 'all_emails': [], 'tech_analysis': None}

        if not website.startswith('http'):
            website = 'https://' + website

        pages_to_check = [
            website,
            website.rstrip('/') + '/contact',
            website.rstrip('/') + '/contact-us',
            website.rstrip('/') + '/about',
            website.rstrip('/') + '/about-us',
        ]

        all_emails = []

        for idx, url in enumerate(pages_to_check):
            html, headers, load_time = self._fetch_page_with_meta(url)
            if not html:
                # If homepage failed to load, don't waste time checking subpages on dead host
                if idx == 0:
                    break
                continue

            # Run TechSniffer on primary page
            if idx == 0 and not result.get('tech_analysis'):
                try:
                    from app.scrapers.tech_sniffer import TechSniffer
                    sniffer = TechSniffer()
                    result['tech_analysis'] = sniffer.analyze_html(html, headers, load_time, url)
                except Exception as e:
                    logger.debug(f"TechSniffer error: {e}")

            emails = re.findall(EMAIL_RE, html)
            valid = [e for e in emails if self._is_valid_email(e)]
            all_emails.extend(valid)

            if not result['email'] and valid:
                result['email'] = valid[0]

            if not result['phone']:
                phone = self._extract_phone_from_text(html)
                if phone:
                    result['phone'] = phone

            if result['email'] and result['phone']:
                break

            random_delay(0.2, 0.4)

        result['all_emails'] = list(set(all_emails))
        return result

    def _predict_email_from_pattern(self, full_name: str, website: str,
                                     site_emails: List[str]) -> Optional[str]:
        domain = self._extract_domain(website)
        if not domain:
            return None

        parts = full_name.lower().strip().split()
        if len(parts) < 2:
            return None

        first, last = parts[0], parts[-1]

        domain_emails = [e for e in site_emails if e.lower().endswith('@' + domain)]
        if not domain_emails:
            return None

        sample = domain_emails[0].lower()
        local = sample.split('@')[0]

        pattern = self._detect_pattern(local)
        if not pattern:
            return None

        predicted = self._apply_pattern(pattern, first, last, domain)
        if predicted and predicted.lower() not in [e.lower() for e in domain_emails]:
            return predicted

        return predicted

    def _detect_pattern(self, local_part: str) -> Optional[str]:
        if '.' in local_part:
            parts = local_part.split('.')
            if len(parts) == 2:
                if len(parts[0]) == 1:
                    return 'f.last'
                return 'first.last'
        if re.match(r'^[a-z][a-z]+$', local_part):
            return 'first'
        if re.match(r'^[a-z]\.[a-z]+$', local_part):
            return 'f.last'
        return None

    def _apply_pattern(self, pattern: str, first: str, last: str, domain: str) -> Optional[str]:
        templates = {
            'first.last': f'{first}.{last}@{domain}',
            'first': f'{first}@{domain}',
            'f.last': f'{first[0]}.{last}@{domain}',
            'flast': f'{first[0]}{last}@{domain}',
            'firstlast': f'{first}{last}@{domain}',
        }
        return templates.get(pattern)

    def _verify_email_smtp(self, email: str) -> Dict:
        parts = email.split('@')
        if len(parts) != 2 or not parts[1]:
            return {'exists': False, 'accept_all': False, 'score': 0}
        domain = parts[1]
        result = {'exists': False, 'accept_all': False, 'score': 0}

        if getattr(self, '_port25_blocked', False):
            return result

        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(sorted(mx_records, key=lambda x: x.preference)[0].exchange).rstrip('.')
        except Exception:
            return result

        result['score'] += 10

        try:
            with smtplib.SMTP(timeout=2) as smtp:
                smtp.connect(mx_host, 25)
                smtp.helo('scout-verify.local')
                smtp.mail('verify@scout-verify.local')
                code, msg = smtp.rcpt(email)

                if code == 250:
                    result['exists'] = True
                    result['score'] += 80

                fake = f'zzznonexistent999@{domain}'
                code2, _ = smtp.rcpt(fake)
                if code2 == 250:
                    result['accept_all'] = True
                    result['score'] = max(result['score'] - 40, 30)

        except (socket.timeout, TimeoutError):
            # Port 25 is blocked by ISP/firewall on this network; disable further SMTP attempts to avoid delays
            self._port25_blocked = True
            result['score'] += 20
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError,
                ConnectionRefusedError, OSError) as e:
            logger.debug(f"SMTP verify failed for {email}: {e}")
            result['score'] += 20

        return result

    def _score_and_verify_email(self, email: str, source: str,
                                 pattern_match: bool = False,
                                 site_emails_count: int = 0) -> Dict:
        score = 0

        if source == 'bio':
            score += 90
        elif source == 'website':
            score += 70
        elif source == 'contact_page':
            score += 60
        elif source == 'hunter.io':
            score += 80
        elif source == 'smtp_guess':
            score += 70
        elif source == 'bio_link':
            score += 65
        elif source == 'pattern':
            score += 40
            if site_emails_count >= 3:
                score += 15
            elif site_emails_count >= 1:
                score += 10

        smtp_result = self._verify_email_smtp(email)
        if smtp_result['exists']:
            score += 10
        if smtp_result['accept_all']:
            score -= 20

        return {
            'email': email,
            'score': min(score, 100),
            'source': source,
            'verified': smtp_result['exists'],
            'accept_all': smtp_result['accept_all'],
        }

    def _extract_domain(self, website: str) -> Optional[str]:
        try:
            if not website.startswith('http'):
                website = 'https://' + website
            domain = urlparse(website).netloc or website
            return domain.replace('www.', '')
        except Exception:
            return None

    def _find_company_domain(self, lead_data: Dict) -> Optional[str]:
        company = lead_data.get('company', '')
        headline = lead_data.get('headline', '')
        bio = lead_data.get('bio', '')

        company_names = []

        if company:
            company_names.append(company)

        if headline:
            for marker in [' at ', ' @ ', ' - ']:
                if marker in headline:
                    parts = headline.split(marker)
                    if len(parts) >= 2:
                        company_names.append(parts[-1].strip().rstrip('.'))

            patterns = [
                r'(?:CEO|CTO|COO|CFO|Founder|Owner|Director|President|Partner)\s+(?:of|at|@|-)\s+(.+?)(?:\s*[|,.]|$)',
                r'(?:at|@)\s+(.+?)(?:\s*[|,.]|$)',
            ]
            for p in patterns:
                m = re.search(p, headline, re.IGNORECASE)
                if m:
                    company_names.append(m.group(1).strip())

        seen = set()
        unique_companies = []
        for name in company_names:
            clean = re.sub(r'[^\w\s]', '', name).strip()
            if clean and clean.lower() not in seen and len(clean) > 2:
                seen.add(clean.lower())
                unique_companies.append(clean)

        for name in unique_companies[:3]:
            domain = self._guess_domain(name)
            if domain:
                return domain

        return None

    def _guess_domain(self, company_name: str) -> Optional[str]:
        clean = company_name.lower().strip()
        clean = re.sub(r'\s+(inc|llc|ltd|co|corp|group|holdings)\.?$', '', clean, flags=re.IGNORECASE)
        slug = re.sub(r'[^a-z0-9]', '', clean)

        guesses = [
            f'{slug}.com',
            f'{slug}.io',
            f'{slug}.co',
        ]

        if ' ' in clean:
            parts = clean.split()
            if len(parts) == 2:
                guesses.append(f'{parts[0]}{parts[1]}.com')

        for domain in guesses:
            try:
                dns.resolver.resolve(domain, 'MX')
                return domain
            except Exception:
                continue

        return None

    def _generate_email_candidates(self, full_name: str, website: str) -> List[str]:
        domain = self._extract_domain(website)
        if not domain:
            return []

        parts = full_name.lower().strip().split()
        if len(parts) < 2:
            return []

        first, last = parts[0], parts[-1]
        return [
            f'{first}.{last}@{domain}',
            f'{first}@{domain}',
            f'{first}{last}@{domain}',
            f'{first[0]}{last}@{domain}',
            f'{first[0]}.{last}@{domain}',
            f'contact@{domain}',
            f'info@{domain}',
        ]

    def _extract_bio_links(self, bio: str) -> List[str]:
        if not bio:
            return []

        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|(?:linktr\.ee|stan\.store|beacons\.ai)/[^\s<>"{}|\\^`\[\]]+'
        links = re.findall(url_pattern, bio)

        cleaned = []
        for link in links:
            if not link.startswith('http'):
                link = 'https://' + link
            link = link.rstrip('.,;:!?)')
            cleaned.append(link)

        return cleaned

    def _scrape_link_page(self, url: str) -> Dict[str, Optional[str]]:
        result = {'email': None, 'phone': None}

        html = self._fetch_page(url)
        if not html:
            return result

        emails = re.findall(EMAIL_RE, html)
        valid = [e for e in emails if self._is_valid_email(e)]
        if valid:
            result['email'] = valid[0]

        phone = self._extract_phone_from_text(html)
        if phone:
            result['phone'] = phone

        return result

    def _find_with_hunter(self, full_name: Optional[str], website: Optional[str]) -> Optional[str]:
        if not self.hunter_api_key or not full_name or not website:
            return None

        try:
            domain = self._extract_domain(website)
            if not domain:
                return None

            parts = full_name.split()
            if len(parts) < 2:
                return None

            resp = httpx.get('https://api.hunter.io/v2/email-finder', params={
                'domain': domain,
                'first_name': parts[0],
                'last_name': parts[-1],
                'api_key': self.hunter_api_key,
            }, timeout=10)

            data = resp.json()
            if data.get('data', {}).get('email'):
                return data['data']['email']
        except Exception as e:
            logger.debug(f"Hunter.io error: {e}")

        return None

    def _calculate_lead_score(self, lead_data: Dict) -> int:
        score = 0

        if lead_data.get('email'):
            score += 30
            if lead_data.get('email_source') == 'hunter.io':
                score += 5
        if lead_data.get('phone'):
            score += 30
        if lead_data.get('is_verified'):
            score += 10

        followers_raw = lead_data.get('follower_count', 0)
        try:
            followers = int(followers_raw)
        except (ValueError, TypeError):
            followers = 0
        if 5000 <= followers <= 50000:
            score += 15
        elif 1000 <= followers <= 100000:
            score += 10
        elif followers > 0:
            score += 5

        if lead_data.get('website'):
            score += 10

        bio = (lead_data.get('bio') or '').lower()
        keywords = ['coach', 'consultant', 'ceo', 'founder', 'entrepreneur',
                     'agency', 'business', 'owner', 'director', 'manager']
        if any(k in bio for k in keywords):
            score += 5

        return min(score, 100)

    def enrich_bulk(self, leads: List[Dict], max_workers: int = 3) -> List[Dict]:
        enriched = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.enrich_lead, lead): lead for lead in leads}

            for future in as_completed(futures):
                try:
                    enriched.append(future.result())
                except Exception as e:
                    logger.error(f"Enrichment error: {e}")
                    enriched.append(futures[future])

        return enriched


def enrich_lead(lead_data: Dict, hunter_api_key: Optional[str] = None) -> Dict:
    enricher = LeadEnricher(hunter_api_key=hunter_api_key)
    return enricher.enrich_lead(lead_data)
