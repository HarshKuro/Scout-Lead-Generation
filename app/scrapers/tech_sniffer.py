import re
import time
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

import httpx
from app.scrapers.stealth import random_user_agent

logger = logging.getLogger(__name__)


class TechSniffer:
    """
    Website Technology Stack & Opportunity Sniffer.
    Inspects headers, meta tags, and scripts on client websites to detect:
    - CMS & E-commerce platforms (Shopify, WordPress, WooCommerce, Webflow, Wix, etc.)
    - Frontend frameworks (Next.js, React, Vue, Nuxt, Angular, Tailwind, etc.)
    - Chat & AI widgets (Intercom, Crisp, Zendesk, WhatsApp widgets, HubSpot, Tidio, etc.)
    - Load speed and latency
    - Actionable client sales hooks for Pragtify services.
    """

    CMS_SIGNATURES = {
        "Shopify": [
            r"cdn\.shopify\.com",
            r"Shopify\.theme",
            r"Shopify\.shop",
            r"myshopify\.com",
            r"name=[\"']shopify-digital-wallet",
            r"shopify-section"
        ],
        "WordPress": [
            r"wp-content/",
            r"wp-includes/",
            r"wp-json",
            r"<meta[^>]+name=[\"']generator[\"'][^>]+content=[\"']WordPress",
        ],
        "WooCommerce": [
            r"woocommerce",
            r"wc-api",
            r"wc-ajax",
            r"woocommerce-page",
        ],
        "Webflow": [
            r"webflow\.com",
            r"webflow\.js",
            r"data-wf-page",
            r"data-wf-site",
        ],
        "Wix": [
            r"wix\.com",
            r"wix-code",
            r"parastorage\.com",
            r"static\.wixstatic\.com",
        ],
        "Squarespace": [
            r"squarespace\.com",
            r"static1\.squarespace\.com",
        ],
        "Magento": [
            r"mage/cookies",
            r"skin/frontend",
            r"static/frontend",
        ],
    }

    FRAMEWORK_SIGNATURES = {
        "Next.js": [
            r"/_next/",
            r"__NEXT_DATA__",
            r"id=[\"']__next[\"']",
        ],
        "Nuxt.js": [
            r"/_nuxt/",
            r"__NUXT__",
            r"data-n-head",
        ],
        "React": [
            r"react\.production\.min\.js",
            r"react-dom",
            r"_reactRootContainer",
            r"data-reactroot",
        ],
        "Vue.js": [
            r"vue\.min\.js",
            r"vue\.runtime",
            r"data-v-[a-f0-9]{6,8}",
        ],
        "Angular": [
            r"ng-version",
            r"ng-app",
        ],
        "Tailwind CSS": [
            r"tailwind",
            r"class=[\"'][^\"']*\b(flex|grid|items-center|justify-between|text-sm|px-\d|py-\d)\b[^\"']*[\"']",
        ],
        "Bootstrap": [
            r"bootstrap(?:\.min)?\.(?:css|js)",
        ],
    }

    CHAT_WIDGET_SIGNATURES = {
        "Intercom": [r"widget\.intercom\.io", r"Intercom\('boot'"],
        "Crisp": [r"client\.crisp\.chat", r"\$crisp"],
        "Zendesk": [r"static\.zdassets\.com", r"zE\('webWidget'"],
        "HubSpot": [r"js\.hs-scripts\.com", r"js\.hsforms\.net"],
        "Tidio": [r"code\.tidio\.co"],
        "Drift": [r"js\.driftt\.com"],
        "LiveChat": [r"cdn\.livechatinc\.com"],
        "Tawk.to": [r"embed\.tawk\.to"],
        "Freshchat": [r"wchat\.freshchat\.com"],
        "WhatsApp Widget": [
            r"wa\.me",
            r"api\.whatsapp\.com",
            r"wati\.io",
            r"interakt\.shop",
            r"gallabox",
            r"whatsapp-widget"
        ],
    }

    def analyze_html(self, html: str, headers: Optional[Dict[str, str]] = None,
                     load_time: float = 0.0, url: str = "") -> Dict[str, Any]:
        """
        Analyze HTML and headers to detect technologies and generate sales hooks.
        """
        if not html:
            return {
                "detected_technologies": [],
                "cms": None,
                "framework": None,
                "has_chat_widget": False,
                "chat_widget": None,
                "load_time_seconds": round(load_time, 2),
                "is_slow": False,
                "opportunities": [],
                "tech_summary": ""
            }

        headers_str = " ".join([f"{k}: {v}" for k, v in (headers or {}).items()]).lower()
        content = html + " " + headers_str
        detected = []

        # 1. CMS Detection
        detected_cms = None
        for cms, patterns in self.CMS_SIGNATURES.items():
            if any(re.search(pat, content, re.IGNORECASE) for pat in patterns):
                detected.append(cms)
                if not detected_cms:
                    detected_cms = cms

        # 2. Frontend Framework Detection
        detected_framework = None
        for fw, patterns in self.FRAMEWORK_SIGNATURES.items():
            if any(re.search(pat, content, re.IGNORECASE) for pat in patterns):
                detected.append(fw)
                if not detected_framework:
                    detected_framework = fw

        # 3. Chat / Support Widget Detection
        detected_chat = None
        for widget, patterns in self.CHAT_WIDGET_SIGNATURES.items():
            if any(re.search(pat, content, re.IGNORECASE) for pat in patterns):
                if not detected_chat:
                    detected_chat = widget
                if widget not in detected:
                    detected.append(widget)

        # 4. Meta & SEO checks
        has_og_title = bool(re.search(r'<meta[^>]+property=["\']og:title["\']', html, re.IGNORECASE))
        has_og_image = bool(re.search(r'<meta[^>]+property=["\']og:image["\']', html, re.IGNORECASE))
        has_meta_desc = bool(re.search(r'<meta[^>]+name=["\']description["\']', html, re.IGNORECASE))

        is_slow = load_time >= 2.5
        opportunities = []

        # 5. Formulate Opportunities & Sales Hooks
        if not detected_chat:
            opportunities.append("No conversational AI or live chat widget installed (opportunity for AI agent)")
        elif detected_chat == "WhatsApp Widget":
            opportunities.append("Has WhatsApp widget installed (primed for custom WhatsApp workflow automation)")

        if detected_cms == "Shopify":
            if "WhatsApp Widget" not in detected:
                opportunities.append("Shopify store without automated WhatsApp abandoned cart or order tracking")
            opportunities.append("Shopify e-commerce brand (pitch WhatsApp automation and custom apps)")

        if detected_cms in ["WordPress", "WooCommerce"] and is_slow:
            opportunities.append(f"WordPress site with slow response latency ({round(load_time, 2)}s) (pitch Next.js / headless migration)")

        if not has_og_image or not has_meta_desc:
            opportunities.append("Missing core social preview / SEO meta tags (pitch SEO & conversion optimization)")

        if detected_framework in ["Next.js", "React"] and not detected_chat:
            opportunities.append("Modern React/Next.js frontend (ready for high-performance AI integration)")

        # Unique deduplicated list
        detected = list(dict.fromkeys(detected))

        summary_parts = []
        if detected_cms:
            summary_parts.append(f"CMS: {detected_cms}")
        if detected_framework:
            summary_parts.append(f"Framework: {detected_framework}")
        if detected_chat:
            summary_parts.append(f"Chat: {detected_chat}")
        else:
            summary_parts.append("Chat: None")
        if is_slow:
            summary_parts.append(f"Latency: Slow ({round(load_time, 2)}s)")
        else:
            summary_parts.append(f"Latency: {round(load_time, 2)}s")

        return {
            "detected_technologies": detected,
            "cms": detected_cms,
            "framework": detected_framework,
            "has_chat_widget": bool(detected_chat),
            "chat_widget": detected_chat,
            "load_time_seconds": round(load_time, 2),
            "is_slow": is_slow,
            "opportunities": opportunities,
            "tech_summary": " | ".join(summary_parts)
        }

    def inspect_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch URL and inspect its tech stack and performance.
        """
        if not url.startswith("http"):
            url = "https://" + url

        start = time.time()
        try:
            resp = httpx.get(
                url,
                timeout=10,
                headers={"User-Agent": random_user_agent()},
                follow_redirects=True
            )
            load_time = time.time() - start
            return self.analyze_html(resp.text, dict(resp.headers), load_time, url)
        except Exception as e:
            logger.debug(f"TechSniffer error inspecting {url}: {e}")
            return self.analyze_html("", {}, 0.0, url)
