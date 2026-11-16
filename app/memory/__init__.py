"""
Agency Memory & Lead Matching Module for Scout.
Provides persistent knowledge about agency services, portfolio, expertise,
and intelligence for targeting Indian, Pakistani, and International clients.
"""

from .manager import AgencyMemory, DEFAULT_PROFILE_PATH
from .matcher import LeadMatcher

__all__ = ["AgencyMemory", "LeadMatcher", "DEFAULT_PROFILE_PATH"]
