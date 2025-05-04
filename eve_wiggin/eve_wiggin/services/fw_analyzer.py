"""
Faction Warfare analyzer service.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
import networkx as nx

from eve_wiggin.api.esi_client import get_esi_client
from eve_wiggin.models.faction_warfare import (
    FWSystem, FWFactionStats, FWWarzone, FWWarzoneStatus,
    FactionID, Warzone, SystemStatus, SystemAdjacency
)
from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder

# Configure logging
logger = logging.getLogger(__name__)

class FWAnalyzer:
    """
    Service for analyzing faction warfare data.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the faction warfare analyzer.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.esi_client = get_esi_client(access_token)
        self.graph_builder = get_fw_graph_builder(access_token)
        
        # Define faction names
        self.faction_names = {
            FactionID.CALDARI_STATE: "Caldari State",
            FactionID.MINMATAR_REPUBLIC: "Minmatar Republic",
            FactionID.AMARR_EMPIRE: "Amarr Empire",
            FactionID.GALLENTE_FEDERATION: "Gallente Federation",
            FactionID.GURISTAS_PIRATES: "Guristas Pirates",
            FactionID.ANGEL_CARTEL: "Angel Cartel"
        }
        
        # Define warzone factions
        self.warzone_factions = {
            Warzone.AMARR_MINMATAR: [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC]
        }
        
        # Cache for the warzone graph
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
    
    async def get_fw_systems(self) -> List[FWSystem]:
        """
        Get and process faction warfare systems from the warzone graph.
        
        Returns:
            List[FWSystem]: A list of processed faction warfare systems.
        """
        try:
            # Get the warzone graph
            graph = await self.get_warzone_graph()
            
            # Convert graph nodes to FWSystem objects
            systems = []
            for system_id, data in graph.nodes(data=True):
                # Skip systems not in faction warfare
                if data.get("owner_faction_id", 0) == 0:
                    continue
                
                # Create system model
                system = FWSystem(
                    solar_system_id=int(system_id),
                    solar_system_name=data.get("solar_system_name", f"System {system_id}"),
                    owner_faction_id=data.get("owner_faction_id", 0),
                    occupier_faction_id=data.get("occupier_faction_id", 0),
                    contested=data.get("contested", SystemStatus.UNCONTESTED),
                    victory_points=data.get("victory_points", 0),
                    victory_points_threshold=data.get("victory_points_threshold", 0),
                    advantage=data.get("advantage", 0.0),
                    contest_percent=data.get("contest_percent", 0.0),
                    adjacency=data.get("adjacency", SystemAdjacency.REARGUARD),
                    warzone=Warzone.AMARR_MINMATAR
                )
                
                systems.append(system)
            
            return systems
        except Exception as e:
            logger.error(f"Error getting faction warfare systems: {e}", exc_info=True)
            raise

    async def get_fw_faction_stats(self) -> Dict[int, FWFactionStats]:
        """
        Get and process faction warfare statistics.
        
        Returns:
            Dict[int, FWFactionStats]: A dictionary of faction statistics by faction ID.
        """
        try:
            # Get faction warfare statistics from ESI
            raw_stats = await self.esi_client.get_fw_stats()
            
            # Process statistics
            faction_stats = {}
            for raw_stat in raw_stats:
                faction_id = raw_stat["faction_id"]
                
                # Only include Amarr and Minmatar factions
                if faction_id not in [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC]:
                    continue
                
                # Create faction stats model
                stats = FWFactionStats(
                    faction_id=faction_id,
                    pilots=raw_stat["pilots"],
                    systems_controlled=raw_stat["systems_controlled"],
                    kills_yesterday=raw_stat["kills"]["yesterday"],
                    kills_last_week=raw_stat["kills"]["last_week"],
                    kills_total=raw_stat["kills"]["total"],
                    victory_points_yesterday=raw_stat["victory_points"]["yesterday"],
                    victory_points_last_week=raw_stat["victory_points"]["last_week"],
                    victory_points_total=raw_stat["victory_points"]["total"]
                )
                
                faction_stats[faction_id] = stats
            
            return faction_stats
        except Exception as e:
            logger.error(f"Error getting faction warfare statistics: {e}", exc_info=True)
            raise
    
    async def get_warzone_status(self) -> FWWarzoneStatus:
        """
        Get the status of the Amarr/Minmatar faction warfare warzone.
        
        Returns:
            FWWarzoneStatus: The status of the faction warfare warzone.
        """
        try:
            # Get faction warfare systems and statistics
            systems = await self.get_fw_systems()
            faction_stats = await self.get_fw_faction_stats()
            
            # Initialize warzone
            warzone = FWWarzone(
                name="Amarr-Minmatar Warzone",
                factions=[FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC],
                systems={FactionID.AMARR_EMPIRE: 0, FactionID.MINMATAR_REPUBLIC: 0},
                contested={FactionID.AMARR_EMPIRE: 0, FactionID.MINMATAR_REPUBLIC: 0}
            )
            
            # Count systems controlled by each faction
            for system in systems:
                owner_faction_id = system.owner_faction_id
                occupier_faction_id = system.occupier_faction_id
                contested = system.contested != SystemStatus.UNCONTESTED
                
                # Count systems by owner
                if owner_faction_id in warzone.systems:
                    warzone.systems[owner_faction_id] += 1
                
                # Count contested systems by occupier
                if contested and occupier_faction_id in warzone.contested:
                    warzone.contested[occupier_faction_id] += 1
            
            # Calculate total systems and control percentages
            total_systems = sum(warzone.systems.values())
            warzone.total_systems = total_systems
            
            if total_systems > 0:
                for faction_id, count in warzone.systems.items():
                    warzone.control_percentages[faction_id] = (count / total_systems) * 100
            
            # Create warzone status
            warzone_status = FWWarzoneStatus(
                warzones={Warzone.AMARR_MINMATAR: warzone},
                faction_stats=faction_stats,
                timestamp=datetime.utcnow().isoformat()
            )
            
            return warzone_status
        except Exception as e:
            logger.error(f"Error getting warzone status: {e}", exc_info=True)
            raise
    
    async def get_system_details(self, system_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a faction warfare system.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Dict[str, Any]: Detailed information about the system.
        """
        try:
            # Get the warzone graph
            graph = await self.get_warzone_graph()
            
            # Convert system_id to string for graph lookup
            system_id_str = str(system_id)
            
            # Check if the system is in the graph
            if system_id_str not in graph:
                raise ValueError(f"System with ID {system_id} is not part of the Amarr/Minmatar warzone")
            
            # Get system data from the graph
            system_data = graph.nodes[system_id_str]
            
            # Create FWSystem object
            fw_system = FWSystem(
                solar_system_id=system_id,
                solar_system_name=system_data.get("solar_system_name", f"System {system_id}"),
                owner_faction_id=system_data.get("owner_faction_id", 0),
                occupier_faction_id=system_data.get("occupier_faction_id", 0),
                contested=system_data.get("contested", SystemStatus.UNCONTESTED),
                victory_points=system_data.get("victory_points", 0),
                victory_points_threshold=system_data.get("victory_points_threshold", 0),
                advantage=system_data.get("advantage", 0.0),
                contest_percent=system_data.get("contest_percent", 0.0),
                adjacency=system_data.get("adjacency", SystemAdjacency.REARGUARD),
                warzone=Warzone.AMARR_MINMATAR
            )
            
            # Create result dictionary
            result = {
                "system": fw_system.dict(),
                "system_info": {
                    "name": fw_system.solar_system_name,
                    "security_status": system_data.get("security_status"),
                    "constellation_id": system_data.get("constellation_id"),
                    "constellation_name": system_data.get("constellation_name"),
                    "region_name": system_data.get("region_name")
                },
                "owner_faction_name": self.faction_names.get(fw_system.owner_faction_id),
                "occupier_faction_name": self.faction_names.get(fw_system.occupier_faction_id),
                "graph_data": {
                    "degree": len(list(graph.neighbors(system_id_str))),
                    "neighbors": [
                        {
                            "id": neighbor,
                            "name": graph.nodes[neighbor].get("solar_system_name", f"System {neighbor}"),
                            "owner": graph.nodes[neighbor].get("owner_faction_id", 0),
                            "adjacency": graph.nodes[neighbor].get("adjacency", SystemAdjacency.REARGUARD)
                        }
                        for neighbor in graph.neighbors(system_id_str)
                    ]
                }
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting system details: {e}", exc_info=True)
            raise

