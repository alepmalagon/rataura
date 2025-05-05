"""
Data models for faction warfare analysis.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FactionID(int, Enum):
    """
    Enumeration of faction IDs in EVE Online.
    """
    CALDARI_STATE = 500001
    MINMATAR_REPUBLIC = 500002
    AMARR_EMPIRE = 500003
    GALLENTE_FEDERATION = 500004
    GURISTAS_PIRATES = 500010
    ANGEL_CARTEL = 500011


class Warzone(str, Enum):
    """
    Enumeration of faction warfare warzones.
    """
    CALDARI_GALLENTE = "caldari_gallente"
    AMARR_MINMATAR = "amarr_minmatar"


class SystemStatus(str, Enum):
    """
    Enumeration of faction warfare system statuses.
    """
    UNCONTESTED = "uncontested"
    CONTESTED = "contested"
    VULNERABLE = "vulnerable"
    CAPTURED = "captured"


class SystemAdjacency(str, Enum):
    """
    Enumeration of faction warfare system adjacency types.
    """
    FRONTLINE = "frontline"
    COMMAND_OPERATIONS = "command_operations"
    REARGUARD = "rearguard"


class FWSystem(BaseModel):
    """
    Model for a faction warfare system.
    """
    solar_system_id: int
    solar_system_name: Optional[str] = None
    owner_faction_id: int
    occupier_faction_id: int
    contested: str
    victory_points: int
    victory_points_threshold: int
    advantage: float = 0.0
    amarr_advantage: float = 0.0
    minmatar_advantage: float = 0.0
    net_advantage: float = 0.0
    adjacency: Optional[str] = None
    
    # Calculated fields
    contest_percent: float = Field(default=0.0, description="Percentage of victory points towards capture")
    warzone: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class FWFactionStats(BaseModel):
    """
    Model for faction warfare statistics for a faction.
    """
    faction_id: int
    pilots: int
    systems_controlled: int
    kills_yesterday: int = 0
    kills_last_week: int = 0
    kills_total: int = 0
    victory_points_yesterday: int = 0
    victory_points_last_week: int = 0
    victory_points_total: int = 0


class FWWarzone(BaseModel):
    """
    Model for a faction warfare warzone.
    """
    name: str
    factions: List[int]
    systems: Dict[int, int] = {}  # faction_id -> count of systems
    contested: Dict[int, int] = {}  # faction_id -> count of contested systems
    
    # Calculated fields
    total_systems: int = 0
    control_percentages: Dict[int, float] = {}  # faction_id -> percentage of control


class FWWarzoneStatus(BaseModel):
    """
    Model for the status of all faction warfare warzones.
    """
    warzones: Dict[str, FWWarzone]
    faction_stats: Dict[int, FWFactionStats] = {}
    timestamp: Optional[str] = None
