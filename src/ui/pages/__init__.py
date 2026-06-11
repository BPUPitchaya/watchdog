"""Page classes for the WatchDog AI Dashboard.

Each page is implemented as a class that takes the main dashboard as a reference
to access shared resources like page_container, models, and AI client.
"""

from .ai_mentor_page import AIMentorPage
from .autonomous_shield_page import AutonomousShieldPage
from .forensic_vault_page import ForensicVaultPage
from .live_sentinel_page import LiveSentinelPage
from .network_topology_page import NetworkTopologyPage
from .placeholder_page import PlaceholderPage
from .settings_page import SettingsPage
from .threat_encyclopedia_page import ThreatEncyclopediaPage

__all__ = [
    "LiveSentinelPage",
    "ForensicVaultPage",
    "AutonomousShieldPage",
    "AIMentorPage",
    "NetworkTopologyPage",
    "SettingsPage",
    "PlaceholderPage",
    "ThreatEncyclopediaPage",
]
