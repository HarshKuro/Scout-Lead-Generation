import re
import urllib.parse
from typing import Dict, Any, List, Optional

from app.memory.manager import AgencyMemory

# Regional keyword dictionaries
INDIA_KEYWORDS = [
    "india", "bengaluru", "bangalore", "mumbai", "delhi", "ncr", "gurgaon",
    "gurugram", "noida", "hyderabad", "pune", "chennai", "kolkata", "ahmedabad",
    "jaipur", "surat", "indore", "kochi", "kerala", "chandigarh", ".in", ".co.in", "inr", "rupees", "₹"
]

PAKISTAN_KEYWORDS = [
    "pakistan", "karachi", "lahore", "islamabad", "rawalpindi", "faisalabad",
    "peshawar", "multan", "sialkot", "gujranwala", ".pk", ".com.pk", "pkr", "rs."
]

INTERNATIONAL_KEYWORDS = [
    "united states", "usa", "san francisco", "new york", "austin", "california",
    "london", "united kingdom", "uk", "canada", "toronto", "vancouver",
    "dubai", "uae", "abu dhabi", "singapore", "australia", "sydney", "melbourne",
    "berlin", "germany", "france", "paris", "netherlands", "amsterdam"
]


class LeadMatcher:
    """
    Matches enriched leads against Agency Memory (Pragtify).
    Determines market region (India, Pakistan, International),
    calculates agency fit score, finds relevant services and portfolio case studies,
    incorporates website tech stack & pain points, and crafts high-converting pitches.
    """

    def __init__(self, memory: Optional[AgencyMemory] = None):
        self.memory = memory or AgencyMemory()

    def detect_region(self, lead: Dict[str, Any]) -> str:
        """
        Detect whether lead is from India, Pakistan, or International market.
        """
        combined_text = " ".join([
            str(lead.get("location", "")),
            str(lead.get("bio", "")),
            str(lead.get("headline", "")),
            str(lead.get("website", "")),
            str(lead.get("company", ""))
        ]).lower()

        phone = str(lead.get("phone", "")).strip()

        # Check phone prefixes first (most accurate)
        clean_phone = re.sub(r"[^\d+]", "", phone)
        if clean_phone.startswith("+91") or (clean_phone.startswith("91") and len(clean_phone) == 12):
            return "India"
        if clean_phone.startswith("+92") or (clean_phone.startswith("92") and len(clean_phone) == 12):
            return "Pakistan"
        if clean_phone.startswith("+1") or clean_phone.startswith("+44") or clean_phone.startswith("+971") or clean_phone.startswith("+61"):
            return "International"

        # Check keywords in text
        for kw in INDIA_KEYWORDS:
            if kw in combined_text:
                return "India"

        for kw in PAKISTAN_KEYWORDS:
            if kw in combined_text:
                return "Pakistan"

        for kw in INTERNATIONAL_KEYWORDS:
            if kw in combined_text:
                return "International"

        # Fallback based on email or website TLD
        email = lead.get("email", "").lower()
        website = lead.get("website", "").lower()
        if email.endswith(".in") or ".in/" in website or website.endswith(".in"):
            return "India"
        if email.endswith(".pk") or ".pk/" in website or website.endswith(".pk"):
            return "Pakistan"

        return "International"

    def clean_phone_for_whatsapp(self, phone: str, region: str) -> Optional[str]:
        """
        Normalize phone number for WhatsApp wa.me links.
        """
        if not phone:
            return None

        digits = re.sub(r"\D", "", phone)
        if not digits:
            return None

        if region == "India":
            # 10 digit Indian number starting with 6,7,8,9
            if len(digits) == 10 and digits[0] in "6789":
                return "91" + digits
            elif len(digits) == 11 and digits.startswith("0"):
                return "91" + digits[1:]
            elif len(digits) == 12 and digits.startswith("91"):
                return digits
        elif region == "Pakistan":
            # 11 digit Pakistani number like 03001234567
            if len(digits) == 11 and digits.startswith("03"):
                return "92" + digits[1:]
            elif len(digits) == 10 and digits.startswith("3"):
                return "92" + digits
            elif len(digits) == 12 and digits.startswith("92"):
                return digits
        else:
            # International
            if len(digits) == 10:  # Common US/Canada format without country code
                return "1" + digits
            elif len(digits) >= 11:
                return digits

        return digits if len(digits) >= 10 else None

    def match_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Augment an enriched lead with agency match intelligence, fit score,
        relevant case studies, website tech stack analysis, and customized outreach pitch.
        """
        enriched = lead.copy()
        region = self.detect_region(lead)
        enriched["market_region"] = region

        # Collect text corpus for matching
        corpus = " ".join([
            str(lead.get("bio", "")),
            str(lead.get("headline", "")),
            str(lead.get("company", "")),
            str(lead.get("website", "")),
            str(lead.get("industry", "")),
            str(lead.get("tech_stack", "")),
            str(lead.get("tech_summary", ""))
        ])

        # Match services
        matched_services = self.memory.match_services(corpus)
        top_services = [ms["service"] for ms in matched_services[:2]]
        service_names = [s.get("name") for s in top_services]
        enriched["matched_services"] = ", ".join(service_names) if service_names else "Full-Stack & AI Engineering"

        # Match portfolio items
        matched_projects = self.memory.match_portfolio(
            text=corpus,
            industry=lead.get("industry", ""),
            tech_stack=lead.get("detected_technologies", [])
        )
        top_project = matched_projects[0] if matched_projects else None
        enriched["matched_portfolio"] = top_project.get("name") if top_project else "MAAYA - Personal AI Operating Agent"

        # Calculate Agency Fit Score (0-100)
        fit_score = self._calculate_fit_score(lead, matched_services, top_project)
        enriched["agency_fit_score"] = fit_score

        # Generate Pitch
        lead_name = lead.get("full_name") or lead.get("username") or "there"
        pitch = self._generate_pitch(lead_name, region, top_services, top_project, lead)
        enriched["recommended_pitch"] = pitch

        # WhatsApp click-to-chat link
        cleaned_phone = self.clean_phone_for_whatsapp(lead.get("phone", ""), region)
        if cleaned_phone:
            encoded_msg = urllib.parse.quote(pitch)
            enriched["whatsapp_chat_link"] = f"https://wa.me/{cleaned_phone}?text={encoded_msg}"
        else:
            enriched["whatsapp_chat_link"] = ""

        return enriched

    def _calculate_fit_score(self, lead: Dict[str, Any], matched_services: List[Dict], top_project: Optional[Dict]) -> int:
        score = 25  # Base score

        # Contactability
        if lead.get("email"):
            score += 20
        if lead.get("phone"):
            score += 20
        if lead.get("website"):
            score += 10

        # Memory match relevance
        if matched_services:
            top_match = matched_services[0]["match_score"]
            score += min(top_match * 3, 15)

        if top_project:
            score += 10

        # Tech sniffer opportunity bonus
        if lead.get("tech_opportunities"):
            score += 10

        # Decision maker check
        title = (str(lead.get("headline", "")) + " " + str(lead.get("bio", ""))).lower()
        if any(role in title for role in ["founder", "ceo", "cto", "co-founder", "owner", "director", "head of", "partner", "vp"]):
            score += 10

        return min(score, 100)

    def _generate_pitch(self, name: str, region: str, top_services: List[Dict],
                        top_project: Optional[Dict], lead: Dict[str, Any]) -> str:
        agency_name = self.memory.agency_name
        agency_url = self.memory.website or "https://pragtify.com"

        primary_service = top_services[0].get("name") if top_services else "Generative AI, AI Agents & Full-Stack Engineering"
        project_name = top_project.get("name") if top_project else "MAAYA (AI Operating Agent)"

        first_name = name.split()[0] if " " in name else name
        company = lead.get("company") or "your team"

        # Tech audit hook if sniffer found opportunities
        tech_hook = ""
        opportunities = lead.get("tech_opportunities", [])
        if opportunities:
            tech_hook = f" (Saw your site at {lead.get('website', '')} — {opportunities[0].lower()})"

        if region == "India":
            return (
                f"Hi {first_name}, noticed your work at {company}{tech_hook}. "
                f"At {agency_name}, we build production-ready {primary_service} and custom automations "
                f"with rapid 2-4 week sprints (like our work on {project_name}). "
                f"Would you be open to a quick 5-min WhatsApp chat to see how we can accelerate your tech roadmap? "
                f"Portfolio: {agency_url}"
            )

        elif region == "Pakistan":
            return (
                f"Salam {first_name}, came across your profile and work at {company}{tech_hook}. "
                f"We at {agency_name} collaborate with software houses and founders on {primary_service} "
                f"and advanced LLM/RAG pipelines ({project_name}). "
                f"We act as an agile engineering arm to ship complex features without overhead. "
                f"Would love to connect and share a 2-min demo: {agency_url}"
            )

        else:
            # International / Global (US, UK, UAE, EU)
            return (
                f"Hi {first_name},\n\n"
                f"Saw what you're building at {company}{tech_hook}. "
                f"At {agency_name}, we engineer high-performance {primary_service}. "
                f"Our team contributes to the Linux kernel and has delivered systems like {project_name} "
                f"with clean, scalable architecture from day one.\n\n"
                f"Are you exploring ways to automate workflows or ship new AI features this quarter? "
                f"Happy to share a 3-minute Loom walkthrough or architecture outline: {agency_url}\n\n"
                f"Best,\n{agency_name} Team"
            )
