"""
Faction Warfare adjacency detector using BFS approach.
"""

import logging
import pickle
from collections import deque
from typing import Dict, List, Set, TypedDict, Optional, Any
import os

from eve_wiggin.models.faction_warfare import (
    FWSystem, FactionID, SystemAdjacency
)

# Configure logging
logger = logging.getLogger(__name__)

# Define permanent frontline systems
AMARR_PERMANENT_FRONTLINES = {
    "Amamake", "Bosboger", "Auner", "Resbroko", "Evati", "Arnstur"
}

MINMATAR_PERMANENT_FRONTLINES = {
    "Raa", "Kamela", "Sosala", "Huola", "Anka", "Iesa", "Uusanen", "Saikamon", "Halmah"
}

# Path to solar systems data file
SOLAR_SYSTEMS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "solar_systems.pickle")


class SolarSystem(TypedDict):
    """
    TypedDict for solar system data from the pickle file.
    """
    name: str
    solar_system_id: str
    region: str
    region_id: str
    constellation: str
    constellation_id: str
    adjacent: List[str]  # list of all id's of adjacent Solar Systems


class AdjacencyDetector:
    """
    Service for detecting faction warfare system adjacency using BFS.
    """
    
    def __init__(self):
        """
        Initialize the adjacency detector.
        """
        self.solar_systems: Dict[str, SolarSystem] = {}
        self.fw_systems: Dict[str, FWSystem] = {}
        self.amarr_systems: Set[str] = set()
        self.minmatar_systems: Set[str] = set()
        self.frontline_systems: Set[str] = set()
        self.command_ops_systems: Set[str] = set()
        
        # Load solar systems data
        self._load_solar_systems()
    
    def _load_solar_systems(self) -> None:
        """
        Load solar systems data from pickle file.
        """
        try:
            if os.path.exists(SOLAR_SYSTEMS_FILE):
                with open(SOLAR_SYSTEMS_FILE, 'rb') as f:
                    self.solar_systems = pickle.load(f)
                logger.info(f"Loaded {len(self.solar_systems)} solar systems from {SOLAR_SYSTEMS_FILE}")
            else:
                logger.warning(f"Solar systems file not found: {SOLAR_SYSTEMS_FILE}")
                self.solar_systems = {}
        except Exception as e:
            logger.error(f"Error loading solar systems data: {e}", exc_info=True)
            self.solar_systems = {}
    
    def determine_adjacency(self, fw_systems: List[FWSystem]) -> List[FWSystem]:
        """
        Determine the adjacency type for each faction warfare system using BFS.
        
        Args:
            fw_systems (List[FWSystem]): The list of faction warfare systems.
        
        Returns:
            List[FWSystem]: The updated list of faction warfare systems with adjacency information.
        """
        # Reset state
        self.fw_systems = {str(system.solar_system_id): system for system in fw_systems}
        self.amarr_systems = {str(system.solar_system_id) for system in fw_systems 
                             if system.owner_faction_id == FactionID.AMARR_EMPIRE}
        self.minmatar_systems = {str(system.solar_system_id) for system in fw_systems 
                                if system.owner_faction_id == FactionID.MINMATAR_REPUBLIC}
        self.frontline_systems = set()
        self.command_ops_systems = set()
        
        # First, mark all systems as rearguard by default
        for system_id, system in self.fw_systems.items():
            system.adjacency = SystemAdjacency.REARGUARD
        
        # Mark permanent frontline systems
        self._mark_permanent_frontlines()
        
        # Filter solar systems to only include FW systems
        fw_solar_systems = {
            system_id: system for system_id, system in self.solar_systems.items()
            if system_id in self.fw_systems
        }
        
        if not fw_solar_systems:
            logger.warning("No faction warfare systems found in solar systems data")
            return list(self.fw_systems.values())
        
        logger.info(f"Found {len(fw_solar_systems)} faction warfare systems in solar systems data")
        logger.info(f"Amarr systems: {len(self.amarr_systems)}, Minmatar systems: {len(self.minmatar_systems)}")
        
        # Find frontline systems using BFS
        self._find_frontlines_bfs(fw_solar_systems)
        
        # Find command operations systems (one jump from frontlines)
        self._find_command_ops(fw_solar_systems)
        
        logger.info(f"Adjacency determination complete: {len(self.frontline_systems)} frontlines, "
                   f"{len(self.command_ops_systems)} command ops, "
                   f"{len(self.fw_systems) - len(self.frontline_systems) - len(self.command_ops_systems)} rearguards")
        
        return list(self.fw_systems.values())
    
    def _mark_permanent_frontlines(self) -> None:
        """
        Mark permanent frontline systems based on the predefined lists.
        """
        for system_id, system in self.fw_systems.items():
            system_name = system.solar_system_name
            
            # Check if this is a permanent frontline for the controlling faction
            if (system.owner_faction_id == FactionID.AMARR_EMPIRE and 
                system_name in AMARR_PERMANENT_FRONTLINES):
                self.frontline_systems.add(system_id)
                system.adjacency = SystemAdjacency.FRONTLINE
                logger.debug(f"Marked {system_name} as permanent Amarr frontline")
                
            if (system.owner_faction_id == FactionID.MINMATAR_REPUBLIC and 
                system_name in MINMATAR_PERMANENT_FRONTLINES):
                self.frontline_systems.add(system_id)
                system.adjacency = SystemAdjacency.FRONTLINE
                logger.debug(f"Marked {system_name} as permanent Minmatar frontline")
    
    def _find_frontlines_bfs(self, fw_solar_systems: Dict[str, SolarSystem]) -> None:
        """
        Find frontline systems using Breadth-First Search.
        
        Args:
            fw_solar_systems (Dict[str, SolarSystem]): The dictionary of faction warfare solar systems.
        """
        # For each Amarr system, check if it's adjacent to a Minmatar system
        for amarr_id in self.amarr_systems:
            if amarr_id not in fw_solar_systems:
                continue
                
            amarr_system = fw_solar_systems[amarr_id]
            
            for adjacent_id in amarr_system["adjacent"]:
                if adjacent_id in self.minmatar_systems:
                    # This Amarr system is adjacent to a Minmatar system, so it's a frontline
                    self.frontline_systems.add(amarr_id)
                    self.fw_systems[amarr_id].adjacency = SystemAdjacency.FRONTLINE
                    logger.debug(f"Marked {amarr_system['name']} as Amarr frontline (adjacent to Minmatar)")
                    break
        
        # For each Minmatar system, check if it's adjacent to an Amarr system
        for minmatar_id in self.minmatar_systems:
            if minmatar_id not in fw_solar_systems:
                continue
                
            minmatar_system = fw_solar_systems[minmatar_id]
            
            for adjacent_id in minmatar_system["adjacent"]:
                if adjacent_id in self.amarr_systems:
                    # This Minmatar system is adjacent to an Amarr system, so it's a frontline
                    self.frontline_systems.add(minmatar_id)
                    self.fw_systems[minmatar_id].adjacency = SystemAdjacency.FRONTLINE
                    logger.debug(f"Marked {minmatar_system['name']} as Minmatar frontline (adjacent to Amarr)")
                    break
    
    def _find_command_ops(self, fw_solar_systems: Dict[str, SolarSystem]) -> None:
        """
        Find command operations systems (one jump from frontlines).
        
        Args:
            fw_solar_systems (Dict[str, SolarSystem]): The dictionary of faction warfare solar systems.
        """
        # For each frontline system, mark all adjacent systems of the same faction as command ops
        for frontline_id in self.frontline_systems:
            if frontline_id not in fw_solar_systems:
                continue
                
            frontline_system = fw_solar_systems[frontline_id]
            frontline_fw_system = self.fw_systems[frontline_id]
            frontline_faction = frontline_fw_system.owner_faction_id
            
            for adjacent_id in frontline_system["adjacent"]:
                if (adjacent_id in self.fw_systems and 
                    adjacent_id not in self.frontline_systems and
                    self.fw_systems[adjacent_id].owner_faction_id == frontline_faction):
                    # This system is adjacent to a frontline of the same faction, so it's a command ops
                    self.command_ops_systems.add(adjacent_id)
                    self.fw_systems[adjacent_id].adjacency = SystemAdjacency.COMMAND_OPERATIONS
                    logger.debug(f"Marked {fw_solar_systems.get(adjacent_id, {}).get('name', adjacent_id)} "
                               f"as command ops (adjacent to frontline {frontline_system['name']})")


def get_adjacency_detector() -> AdjacencyDetector:
    """
    Get an instance of the adjacency detector.
    
    Returns:
        AdjacencyDetector: An instance of the adjacency detector.
    """
    return AdjacencyDetector()
