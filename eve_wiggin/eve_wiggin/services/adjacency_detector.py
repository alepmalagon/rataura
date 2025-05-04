"""
Faction Warfare adjacency detector using NetworkX graph.
"""

import logging
import os
from typing import Dict, List, Set, Optional, Any
import networkx as nx

from eve_wiggin.models.faction_warfare import (
    FWSystem, FactionID, SystemAdjacency
)
from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder

# Configure logging
logger = logging.getLogger(__name__)

# Define path to solar systems pickle file
SOLAR_SYSTEMS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "solar_systems.pickle")

class AdjacencyDetector:
    """
    Service for detecting faction warfare system adjacency using NetworkX graph.
    """
    
    # Singleton instance
    _instance = None
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the adjacency detector.
        """
        self.graph_builder = get_fw_graph_builder(access_token)
        self._warzone_graph = None
    
    async def get_warzone_graph(self) -> nx.Graph:
        """
        Get the warzone graph, building it if necessary.
        
        Returns:
            nx.Graph: The warzone graph.
        """
        if self._warzone_graph is None:
            self._warzone_graph = await self.graph_builder.build_warzone_graph()
        return self._warzone_graph
    
    async def determine_adjacency(self, fw_systems: List[FWSystem]) -> List[FWSystem]:
        """
        Determine the adjacency type for each faction warfare system using NetworkX graph.
        
        Args:
            fw_systems (List[FWSystem]): The list of faction warfare systems.
        
        Returns:
            List[FWSystem]: The updated list of faction warfare systems with adjacency information.
        """
        try:
            # Get the warzone graph
            graph = await self.get_warzone_graph()
            
            # Update adjacency information in the FWSystem objects
            for system in fw_systems:
                system_id = str(system.solar_system_id)
                
                if system_id in graph:
                    # Get adjacency from the graph
                    adjacency = graph.nodes[system_id].get("adjacency", SystemAdjacency.REARGUARD)
                    system.adjacency = adjacency
            
            return fw_systems
        
        except Exception as e:
            logger.error(f"Error determining adjacency: {e}", exc_info=True)
            # Return the original systems if there's an error
            return fw_systems


def get_adjacency_detector(access_token: Optional[str] = None) -> AdjacencyDetector:
    """
    Get an instance of the adjacency detector.
    
    Args:
        access_token (Optional[str], optional): The access token for authenticated requests.
    
    Returns:
        AdjacencyDetector: An instance of the adjacency detector.
    """
    # Implement singleton pattern to avoid creating multiple instances
    if AdjacencyDetector._instance is None:
        AdjacencyDetector._instance = AdjacencyDetector(access_token)
        logger.info("Created new AdjacencyDetector instance")
    return AdjacencyDetector._instance
