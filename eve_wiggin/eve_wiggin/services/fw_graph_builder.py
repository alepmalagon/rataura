"""
Module for building a NetworkX graph of faction warfare systems.
"""

import logging
import os
import pickle
from typing import Dict, List, Set, Tuple, Any, Optional
import networkx as nx

from eve_wiggin.api.esi_client import get_esi_client
from eve_wiggin.api.warzone_api_client import get_warzone_api_client

logger = logging.getLogger(__name__)

# Constants
AMARR_FACTION_ID = 500003
MINMATAR_FACTION_ID = 500002
CALDARI_FACTION_ID = 500001
GALLENTE_FACTION_ID = 500004

# Permanent frontline systems
AMARR_PERMANENT_FRONTLINES = ["Raa", "Kamela", "Sosala", "Huola", "Anka", "Iesa", "Uusanen", "Saikamon", "Halmah"]
MINMATAR_PERMANENT_FRONTLINES = [ "Amamake", "Bosboger", "Auner", "Resbroko", "Evati", "Arnstur"]

# Pickle file paths
AMA_MIN_PICKLE = os.path.join(os.path.dirname(__file__), "..", "data", "ama_min.pickle")

class FWGraphBuilder:
    """
    Builder for faction warfare system graphs.
    """
    
    def __init__(self):
        """
        Initialize the graph builder.
        """
        self.esi_client = get_esi_client()
        self.warzone_api_client = get_warzone_api_client()
        
    async def build_graph(self, warzone: str = "amarr_minmatar") -> nx.Graph:
        """
        Build a NetworkX graph of faction warfare systems.
        
        Args:
            warzone (str, optional): The warzone to build the graph for. Defaults to "amarr_minmatar".
        
        Returns:
            nx.Graph: A NetworkX graph of faction warfare systems.
        """
        logger.info(f"Building graph for {warzone} warzone...")
        
        # Load the pickle file
        if warzone == "amarr_minmatar":
            pickle_file = AMA_MIN_PICKLE
            faction_ids = [AMARR_FACTION_ID, MINMATAR_FACTION_ID]
        else:
            raise ValueError(f"Unsupported warzone: {warzone}")
        
        # Load the pickle file - SOURCE: ama_min.pickle
        with open(pickle_file, "rb") as f:
            systems_data = pickle.load(f)
        
        logger.info(f"Loaded {len(systems_data)} systems from {pickle_file}")
        
        # Create a new graph
        graph = nx.Graph()
        
        # Check if systems_data is a dictionary or a list
        if isinstance(systems_data, dict):
            # Convert dictionary to list of values for consistent processing
            systems_list = list(systems_data.values())
            # Create a dictionary with string keys for consistent handling
            systems_dict = {str(system["solar_system_id"]): system for system in systems_list}
        else:
            # If it's already a list, use it directly
            systems_dict = {str(system["solar_system_id"]): system for system in systems_data}
        
        # Add nodes to the graph - SOURCE: ama_min.pickle for system name, neighbors, region
        for system_id, system in systems_dict.items():
            # Extract data from pickle file
            solar_system_name = system.get("solar_system_name", f"System {system_id}")
            region_name = system.get("region_name", "Unknown Region")
            constellation_name = system.get("constellation_name", "Unknown Constellation")
            solar_system_id = system.get("solar_system_id", system_id)
            
            graph.add_node(
                system_id,
                # Data from pickle file (ama_min.pickle)
                solar_system_name=solar_system_name,  # From pickle
                region_name=region_name,      # From pickle
                constellation_name=constellation_name,  # From pickle
                solar_system_id=solar_system_id,  # From pickle
                
                # Data to be populated from ESI API
                owner_faction_id=None,  # Will be populated from ESI data
                occupier_faction_id=None,  # Will be populated from ESI data
                victory_points=0,  # Will be populated from ESI data
                victory_points_threshold=0,  # Will be populated from ESI data
                contested=False,  # Will be populated from ESI data
                contest_percentage=0.0,  # Will be populated from ESI data
                
                # Data to be populated from warzone API
                amarr_advantage=0.0,  # Will be populated from warzone API
                minmatar_advantage=0.0,  # Will be populated from warzone API
                net_advantage=0.0,  # Will be populated from warzone API
                
                # Default adjacency
                adjacency="rearguard"  # Will be determined based on graph analysis
            )
            
            # Add edges to the graph - SOURCE: ama_min.pickle for system neighbors
            for adjacent_id in system["adjacent"]:
                # Convert to string for consistent handling
                adjacent_id = str(adjacent_id)
                if adjacent_id in systems_dict:
                    graph.add_edge(system_id, adjacent_id)
                    logger.debug(f"Added edge between {solar_system_name} and {systems_dict[adjacent_id].get('solar_system_name', f'System {adjacent_id}')}")
        
        # Log the number of nodes and edges
        logger.info(f"Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Check if any nodes have no adjacent systems
        for node in graph.nodes:
            neighbors = list(graph.neighbors(node))
            logger.debug(f"System {graph.nodes[node]['solar_system_name']} has {len(neighbors)} adjacent systems")
        
        # Enrich the graph with ESI data - SOURCE: ESI API /fw/systems/ endpoint
        await self._enrich_graph_with_esi_data(graph, faction_ids)
        
        # Enrich the graph with advantage data - SOURCE: EVE Online API warzone/status
        await self._enrich_graph_with_advantage_data(graph)
        
        # Determine adjacency for each system
        self._determine_adjacency(graph)
        
        return graph
    
    async def build_warzone_graph(self, warzone: str = "amarr_minmatar") -> nx.Graph:
        """
        Build a NetworkX graph of faction warfare systems for a specific warzone.
        This is an alias for build_graph for backward compatibility.
        
        Args:
            warzone (str, optional): The warzone to build the graph for. Defaults to "amarr_minmatar".
        
        Returns:
            nx.Graph: A NetworkX graph of faction warfare systems.
        """
        return await self.build_graph(warzone)
    
    async def _enrich_graph_with_esi_data(self, graph: nx.Graph, faction_ids: List[int]) -> None:
        """
        Enrich the graph with data from the ESI API.
        
        Args:
            graph (nx.Graph): The graph to enrich.
            faction_ids (List[int]): The faction IDs to filter by.
        """
        logger.info("Enriching graph with ESI data from /fw/systems/ endpoint...")
        
        # Get faction warfare systems from ESI - SOURCE: ESI API /fw/systems/ endpoint
        fw_systems = await self.esi_client.get_fw_systems()
        
        # Create a dictionary for quick lookup
        fw_systems_dict = {str(system["solar_system_id"]): system for system in fw_systems}
        
        # Update the graph nodes with ESI data
        for node in graph.nodes:
            if node in fw_systems_dict:
                fw_system = fw_systems_dict[node]
                
                # Update node attributes - SOURCE: ESI API /fw/systems/ endpoint
                graph.nodes[node]["owner_faction_id"] = fw_system["owner_faction_id"]
                graph.nodes[node]["occupier_faction_id"] = fw_system["occupier_faction_id"]
                graph.nodes[node]["victory_points"] = fw_system["victory_points"]
                graph.nodes[node]["victory_points_threshold"] = fw_system["victory_points_threshold"]
                graph.nodes[node]["contested"] = fw_system["contested"]
                
                # Calculate contest percentage - SOURCE: ESI API /fw/systems/ endpoint
                if fw_system["victory_points_threshold"] > 0:
                    contest_percentage = fw_system["victory_points"] / fw_system["victory_points_threshold"] * 100
                    graph.nodes[node]["contest_percentage"] = contest_percentage
                
                logger.debug(f"Enriched {graph.nodes[node]['solar_system_name']} with ESI data")
            else:
                logger.warning(f"System {graph.nodes[node]['solar_system_name']} (ID: {node}) not found in ESI data")
    
    async def _enrich_graph_with_advantage_data(self, graph: nx.Graph) -> None:
        """
        Enrich the graph with advantage data from the warzone API.
        
        Args:
            graph (nx.Graph): The graph to enrich.
        """
        logger.info("Enriching graph with advantage data from EVE Online API warzone/status endpoint...")
        
        # Get advantage data from the warzone API - SOURCE: EVE Online API warzone/status
        advantage_data = await self.warzone_api_client.get_system_advantage_data()
        
        # Update the graph nodes with advantage data
        for node in graph.nodes:
            system_name = graph.nodes[node]["solar_system_name"]
            
            if system_name in advantage_data:
                system_advantage = advantage_data[system_name]
                # Update node attributes - SOURCE: EVE Online API warzone/status
                graph.nodes[node]["amarr_advantage"] = system_advantage["amarr"]
                graph.nodes[node]["minmatar_advantage"] = system_advantage["minmatar"]
                graph.nodes[node]["net_advantage"] = system_advantage["net_advantage"]
                logger.debug(f"Set advantage for {system_name}: Amarr={system_advantage['amarr']}, Minmatar={system_advantage['minmatar']}, Net={system_advantage['net_advantage']}")
            else:
                # If the system is not in the advantage data, calculate a default value
                # based on the contest percentage
                if graph.nodes[node]["contested"]:
                    # For contested systems, use a default value of 0.5 (neutral)
                    graph.nodes[node]["amarr_advantage"] = 0.5
                    graph.nodes[node]["minmatar_advantage"] = 0.5
                    graph.nodes[node]["net_advantage"] = 0.0
                else:
                    # For uncontested systems, set advantage to 0 (no advantage)
                    graph.nodes[node]["amarr_advantage"] = 0.0
                    graph.nodes[node]["minmatar_advantage"] = 0.0
                    graph.nodes[node]["net_advantage"] = 0.0
                
                logger.debug(f"Using default advantage for {system_name}: Amarr={graph.nodes[node]['amarr_advantage']}, Minmatar={graph.nodes[node]['minmatar_advantage']}, Net={graph.nodes[node]['net_advantage']}")
    
    def _determine_adjacency(self, graph: nx.Graph) -> None:
        """
        Determine the adjacency type for each system in the graph.
        
        Adjacency types:
        - Frontline: Systems that are adjacent to enemy-controlled systems or are in the list of permanent frontlines
        - Command Operations: Systems that are adjacent to same-faction frontline systems
        - Rearguard: All other systems
        
        Args:
            graph (nx.Graph): The graph to process.
        """
        logger.info("Determining adjacency for each system...")
        
        # Mark all systems as rearguard by default
        for node in graph.nodes:
            graph.nodes[node]["adjacency"] = "rearguard"
        
        # First, mark permanent frontline systems
        frontline_systems = set()
        for node in graph.nodes:
            system_name = graph.nodes[node]["solar_system_name"]
            occupier_faction_id = graph.nodes[node]["occupier_faction_id"]
            
            # Check if the system is a permanent frontline
            if (system_name in AMARR_PERMANENT_FRONTLINES and occupier_faction_id == AMARR_FACTION_ID) or \
               (system_name in MINMATAR_PERMANENT_FRONTLINES and occupier_faction_id == MINMATAR_FACTION_ID):
                graph.nodes[node]["adjacency"] = "frontline"
                frontline_systems.add(node)
                logger.debug(f"Marked {system_name} as frontline (permanent)")
        
        logger.info(f"Marked {len(frontline_systems)} permanent frontline systems")
        
        # Next, find additional frontline systems based on adjacency to enemy territory
        additional_frontlines = set()
        for node in graph.nodes:
            if node in frontline_systems:
                continue  # Skip already marked frontline systems
            
            system_name = graph.nodes[node]["solar_system_name"]
            occupier_faction_id = graph.nodes[node]["occupier_faction_id"]
            
            if not occupier_faction_id:
                logger.warning(f"System {system_name} has no occupier faction ID")
                continue
            
            # Check if the system is adjacent to an enemy-controlled system
            for neighbor in graph.neighbors(node):
                neighbor_occupier = graph.nodes[neighbor]["occupier_faction_id"]
                
                if not neighbor_occupier:
                    logger.warning(f"Neighbor {graph.nodes[neighbor]['solar_system_name']} of {system_name} has no occupier faction ID")
                    continue
                
                if neighbor_occupier != occupier_faction_id:
                    # This system is adjacent to an enemy-controlled system, so it's a frontline
                    graph.nodes[node]["adjacency"] = "frontline"
                    additional_frontlines.add(node)
                    logger.debug(f"Marked {system_name} as frontline (adjacent to enemy)")
                    break
        
        logger.info(f"Found {len(additional_frontlines)} additional frontline systems based on adjacency to enemy territory")
        
        # Combine all frontline systems
        all_frontlines = frontline_systems.union(additional_frontlines)
        logger.info(f"Total frontline systems: {len(all_frontlines)}")
        
        # Finally, mark command operations systems (adjacent to same-faction frontlines)
        command_ops_systems = set()
        for node in graph.nodes:
            if node in all_frontlines:
                continue  # Skip frontline systems
            
            system_name = graph.nodes[node]["solar_system_name"]
            occupier_faction_id = graph.nodes[node]["occupier_faction_id"]
            
            if not occupier_faction_id:
                logger.warning(f"System {system_name} has no occupier faction ID")
                continue
            
            # Check if the system is adjacent to a same-faction frontline system
            for neighbor in graph.neighbors(node):
                if neighbor in all_frontlines and graph.nodes[neighbor]["occupier_faction_id"] == occupier_faction_id:
                    # This system is adjacent to a same-faction frontline system, so it's a command operations system
                    graph.nodes[node]["adjacency"] = "command_ops"
                    command_ops_systems.add(node)
                    logger.debug(f"Marked {system_name} as command_ops (adjacent to same-faction frontline)")
                    break
        
        logger.info(f"Marked {len(command_ops_systems)} command operations systems")
        
        # Count the remaining rearguard systems
        rearguard_count = graph.number_of_nodes() - len(all_frontlines) - len(command_ops_systems)
        logger.info(f"Remaining rearguard systems: {rearguard_count}")

# Create a global graph builder instance
fw_graph_builder = FWGraphBuilder()

def get_fw_graph_builder(access_token: Optional[str] = None) -> FWGraphBuilder:
    """
    Get a faction warfare graph builder instance.
    
    Args:
        access_token (Optional[str], optional): The access token for authenticated requests.
    
    Returns:
        FWGraphBuilder: A faction warfare graph builder instance.
    """
    return fw_graph_builder
