import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PATH = Path(__file__).parent / "agency_profile.json"


class AgencyMemory:
    """
    Agency Memory Engine for Scout.
    Loads and provides structured access to the agency's profile (Pragtify),
    services, portfolio, technical expertise, and delivery capabilities.
    All fields are optional; feeded information is utilized dynamically.
    """

    def __init__(self, profile_path: Optional[str] = None):
        self.profile_path = Path(profile_path) if profile_path else DEFAULT_PROFILE_PATH
        self.profile: Dict[str, Any] = {}
        self.load_profile()

    def load_profile(self) -> bool:
        if not self.profile_path.exists():
            logger.warning(f"Profile not found at {self.profile_path}. Initializing empty memory.")
            self.profile = {}
            return False

        try:
            with open(self.profile_path, "r", encoding="utf-8") as f:
                self.profile = json.load(f)
            logger.info(f"Loaded agency memory from {self.profile_path}")
            return True
        except Exception as e:
            logger.error(f"Error reading agency profile {self.profile_path}: {e}")
            self.profile = {}
            return False

    @property
    def is_loaded(self) -> bool:
        return bool(self.profile)

    @property
    def agency(self) -> Dict[str, Any]:
        return self.profile.get("agency", {})

    @property
    def agency_name(self) -> str:
        return self.agency.get("name", "Pragtify")

    @property
    def website(self) -> str:
        return self.agency.get("website", "https://pragtify.com")

    @property
    def tagline(self) -> str:
        return self.agency.get("tagline", "")

    @property
    def positioning(self) -> str:
        return self.agency.get("positioning", "")

    @property
    def location(self) -> str:
        return self.agency.get("location", "Chandigarh, India")

    @property
    def summary(self) -> str:
        return self.agency.get("summary", "")

    @property
    def contact(self) -> Dict[str, Any]:
        return self.agency.get("contact", {})

    @property
    def core_strengths(self) -> List[str]:
        return self.profile.get("core_strengths", [])

    @property
    def services(self) -> List[Dict[str, Any]]:
        return self.profile.get("services", [])

    @property
    def portfolio(self) -> List[Dict[str, Any]]:
        return self.profile.get("portfolio", [])

    @property
    def technical_expertise(self) -> Dict[str, List[str]]:
        return self.profile.get("technical_expertise", {})

    @property
    def offerings(self) -> Dict[str, List[str]]:
        return self.profile.get("ai_ml_and_automation_offerings", {})

    @property
    def achievements(self) -> List[str]:
        return self.profile.get("achievements", [])

    @property
    def research_and_publications(self) -> List[Dict[str, Any]]:
        return self.profile.get("research_and_publications", [])

    @property
    def open_source_and_kernel(self) -> List[str]:
        return self.profile.get("open_source_and_kernel_development", [])

    @property
    def certifications(self) -> Dict[str, List[str]]:
        return self.profile.get("certifications", {})

    @property
    def delivery_approach(self) -> List[str]:
        return self.profile.get("delivery_approach", [])

    def get_stats_summary(self) -> Dict[str, Any]:
        return {
            "name": self.agency_name,
            "location": self.location,
            "services_count": len(self.services),
            "portfolio_count": len(self.portfolio),
            "publications": len(self.research_and_publications),
            "achievements_count": len(self.achievements),
            "open_source_count": len(self.open_source_and_kernel),
            "has_contact": bool(self.contact.get("email") or self.contact.get("github")),
        }

    def match_services(self, text: str) -> List[Dict[str, Any]]:
        """
        Match lead text (bio, headline, website keywords) against agency services.
        Handles both explicit tags and implicit name/description keywords.
        """
        if not text or not self.services:
            return []

        text_lower = text.lower()
        scored_services = []

        for service in self.services:
            score = 0
            name = service.get("name", "").lower()
            desc = service.get("description", "").lower()
            category = service.get("category", "").lower()
            tags = [t.lower() for t in service.get("tags", [])]
            techs = [tc.lower() for tc in service.get("technologies", [])]

            # Category hit
            if category in text_lower:
                score += 3

            # Direct keyword hits in name
            name_words = [w for w in name.replace('/', ' ').split() if len(w) > 3]
            for nw in name_words:
                if nw in text_lower:
                    score += 4

            # Description keywords
            desc_words = [w for w in desc.replace('.', ' ').replace(',', ' ').split() if len(w) > 4]
            for dw in desc_words:
                if dw in text_lower:
                    score += 1

            # Tags and tech
            for tag in tags:
                if tag in text_lower:
                    score += 3
            for tech in techs:
                if tech in text_lower:
                    score += 2

            if score > 0:
                scored_services.append({"service": service, "match_score": score})

        scored_services.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_services

    def match_portfolio(self, text: str = "", industry: str = "",
                        tech_stack: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Match best case studies / portfolio items for a given lead.
        """
        if not self.portfolio:
            return []

        scored_portfolio = []
        text_lower = (text or "").lower()
        tech_set = set(t.lower() for t in (tech_stack or []))

        for item in self.portfolio:
            score = 0
            item_name = item.get("name", "").lower()
            item_type = item.get("type", "").lower()
            item_desc = item.get("description", "").lower()
            item_tech = [t.lower() for t in item.get("tech_stack", [])]

            if industry and industry.lower() in item_desc:
                score += 5

            for t in item_tech:
                if t in tech_set or t in text_lower:
                    score += 3

            for word in item_name.split():
                if len(word) > 3 and word in text_lower:
                    score += 3

            for word in item_type.split():
                if len(word) > 3 and word in text_lower:
                    score += 2

            if score > 0:
                scored_portfolio.append({"project": item, "score": score})

        scored_portfolio.sort(key=lambda x: x["score"], reverse=True)
        return [sp["project"] for sp in scored_portfolio] if scored_portfolio else self.portfolio[:2]
