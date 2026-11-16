import csv
import json
import time
import logging
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

SENT_TRACKER_PATH = Path(__file__).parent.parent / "memory" / "dispatched_leads.json"


class WhatsAppDispatcher:
    """
    One-Click WhatsApp Outreach & Campaign Dispatcher for Scout.
    Manages interactive and batch outreach using pre-formatted wa.me links,
    tracks sent status to avoid duplicate messaging, and exports campaign CSVs.
    """

    def __init__(self, tracker_path: Optional[Path] = None):
        self.tracker_path = tracker_path or SENT_TRACKER_PATH
        self.sent_numbers = self._load_tracker()

    def _load_tracker(self) -> set:
        if self.tracker_path.exists():
            try:
                with open(self.tracker_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("dispatched_phones", []))
            except Exception as e:
                logger.debug(f"Error loading WhatsApp dispatch tracker: {e}")
        return set()

    def _save_tracker(self):
        try:
            self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.tracker_path, "w", encoding="utf-8") as f:
                json.dump({"dispatched_phones": sorted(list(self.sent_numbers))}, f, indent=2)
        except Exception as e:
            logger.debug(f"Error saving WhatsApp dispatch tracker: {e}")

    def is_dispatched(self, phone: str) -> bool:
        clean = self._clean_phone(phone)
        return clean in self.sent_numbers if clean else False

    def mark_as_dispatched(self, phone: str):
        clean = self._clean_phone(phone)
        if clean:
            self.sent_numbers.add(clean)
            self._save_tracker()

    def _clean_phone(self, phone: str) -> str:
        import re
        return re.sub(r"\D", "", phone or "")

    def get_ready_leads(self, leads: List[Dict[str, Any]], filter_sent: bool = True) -> List[Dict[str, Any]]:
        """
        Filter leads that have a valid whatsapp_chat_link or usable phone number.
        """
        ready = []
        for lead in leads:
            wa_link = lead.get("whatsapp_chat_link", "")
            phone = lead.get("phone", "")

            if not wa_link and not phone:
                continue

            clean = self._clean_phone(phone)
            if filter_sent and clean in self.sent_numbers:
                continue

            ready.append(lead)
        return ready

    def dispatch_lead(self, lead: Dict[str, Any]) -> bool:
        """
        Open the pre-filled WhatsApp link in user's browser.
        """
        url = lead.get("whatsapp_chat_link")
        if not url:
            phone = self._clean_phone(lead.get("phone", ""))
            pitch = lead.get("recommended_pitch", "Hello!")
            import urllib.parse
            url = f"https://wa.me/{phone}?text={urllib.parse.quote(pitch)}"

        try:
            webbrowser.open(url)
            self.mark_as_dispatched(lead.get("phone", ""))
            return True
        except Exception as e:
            logger.error(f"Failed to open WhatsApp URL {url}: {e}")
            return False

    def export_campaign_csv(self, leads: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Export a targeted WhatsApp campaign CSV with pre-filled pitch and direct URLs.
        """
        if not filename:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"whatsapp_campaign_{ts}.csv"

        fieldnames = ["full_name", "company", "phone", "market_region", "recommended_pitch", "whatsapp_chat_link", "agency_fit_score"]
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)

        return filename

    @classmethod
    def load_leads_from_csv(cls, csv_path: str) -> List[Dict[str, Any]]:
        """
        Load leads from an existing Scout export CSV.
        """
        path = Path(csv_path)
        if not path.exists():
            return []

        leads = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append(row)
        return leads
