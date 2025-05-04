"""
Faction Warfare adjacency detector using NetworkX graph.
"""

import logging
import pickle
from collections import deque
from typing import Dict, List, Set, TypedDict, Optional, Any
import os
import networkx as nx

from eve_wiggin.models.faction_warfare import (
    FWSystem, FactionID, SystemAdjacency
)
from eve_wiggin.graph_utils import get_warzone_graph

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
    Service for detecting faction warfare system adjacency using NetworkX graph.
    """
    
    # Singleton instance
    _instance = None
    
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
        
        # Get NetworkX graphs for both warzones
        self.amarr_min_graph, self.amarr_min_name_to_index, self.amarr_min_systems = get_warzone_graph('amarr_minmatar')
        self.cal_gal_graph, self.cal_gal_name_to_index, self.cal_gal_systems = get_warzone_graph('caldari_gallente')
        
        # Create a combined system data dictionary
        self.combined_systems = {}
        for system in self.amarr_min_systems + self.cal_gal_systems:
            system_id = str(system.get('system_id', ''))
            if system_id:
                self.combined_systems[system_id] = system
    
    def determine_adjacency(self, fw_systems: List[FWSystem]) -> List[FWSystem]:
        """
        Determine the adjacency type for each faction warfare system using NetworkX graph.
        
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
        
        # Find frontline systems using NetworkX graph
        self._find_frontlines_using_networkx()
        
        # Find command operations systems (one jump from frontlines)
        self._find_command_ops_using_networkx()
        
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
    
    def _find_frontlines_using_networkx(self) -> None:
        """
        Find frontline systems using the NetworkX graph.
        """
        # For each Amarr system, check if it's adjacent to a Minmatar system
        for amarr_id in self.amarr_systems:
            if amarr_id not in self.combined_systems:
                continue
            
            # Get adjacent systems from the NetworkX graph
            adjacent_systems = self._get_adjacent_systems(amarr_id)
            
            for adjacent_id in adjacent_systems:
                if adjacent_id in self.minmatar_systems:
                    # This Amarr system is adjacent to a Minmatar system, so it's a frontline
                    self.frontline_systems.add(amarr_id)
                    self.fw_systems[amarr_id].adjacency = SystemAdjacency.FRONTLINE
                    system_name = self.fw_systems[amarr_id].solar_system_name
                    logger.debug(f"Marked {system_name} as Amarr frontline (adjacent to Minmatar)")
                    break
        
        # For each Minmatar system, check if it's adjacent to an Amarr system
        for minmatar_id in self.minmatar_systems:
            if minmatar_id not in self.combined_systems:
                continue
            
            # Get adjacent systems from the NetworkX graph
            adjacent_systems = self._get_adjacent_systems(minmatar_id)
            
            for adjacent_id in adjacent_systems:
                if adjacent_id in self.amarr_systems:
                    # This Minmatar system is adjacent to an Amarr system, so it's a frontline
                    self.frontline_systems.add(minmatar_id)
                    self.fw_systems[minmatar_id].adjacency = SystemAdjacency.FRONTLINE
                    system_name = self.fw_systems[minmatar_id].solar_system_name
                    logger.debug(f"Marked {system_name} as Minmatar frontline (adjacent to Amarr)")
                    break
    
    def _find_command_ops_using_networkx(self) -> None:
        """
        Find command operations systems (one jump from frontlines) using the NetworkX graph.
        """
        # For each frontline system, mark all adjacent systems of the same faction as command ops
        for frontline_id in self.frontline_systems:
            if frontline_id not in self.combined_systems:
                continue
            
            frontline_fw_system = self.fw_systems[frontline_id]
            frontline_faction = frontline_fw_system.owner_faction_id
            
            # Get adjacent systems from the NetworkX graph
            adjacent_systems = self._get_adjacent_systems(frontline_id)
            
            for adjacent_id in adjacent_systems:
                if (adjacent_id in self.fw_systems and 
                    adjacent_id not in self.frontline_systems and
                    self.fw_systems[adjacent_id].owner_faction_id == frontline_faction):
                    # This system is adjacent to a frontline of the same faction, so it's a command ops
                    self.command_ops_systems.add(adjacent_id)
                    self.fw_systems[adjacent_id].adjacency = SystemAdjacency.COMMAND_OPERATIONS
                    system_name = self.fw_systems[adjacent_id].solar_system_name
                    logger.debug(f"Marked {system_name} as command ops (adjacent to frontline {frontline_fw_system.solar_system_name})")
    
    def _get_adjacent_systems(self, system_id: str) -> List[str]:
        """
        Get adjacent systems for a given system ID using the NetworkX graph.
        
        Args:
            system_id (str): The system ID to get adjacent systems for.
            
        Returns:
            List[str]: List of adjacent system IDs.
        """
        # Check if the system is in the combined systems dictionary
        if system_id not in self.combined_systems:
            return []
        
        # Get the adjacent systems from the system data
        system_data = self.combined_systems[system_id]
        adjacent_systems = system_data.get('adjacent', [])
        
        # Convert adjacent_systems to strings if they are integers
        adjacent_systems = [str(adj_id) if isinstance(adj_id, int) else adj_id for adj_id in adjacent_systems]
        
        return adjacent_systems


def get_adjacency_detector() -> AdjacencyDetector:
    """
    Get an instance of the adjacency detector.
    
    Returns:
        AdjacencyDetector: An instance of the adjacency detector.
    """
    # Implement singleton pattern to avoid creating multiple instances
    if AdjacencyDetector._instance is None:
        AdjacencyDetector._instance = AdjacencyDetector()
        logger.info("Created new AdjacencyDetector instance")
    return AdjacencyDetector._instance
