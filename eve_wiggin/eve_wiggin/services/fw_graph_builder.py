"""
Module for building a NetworkX graph of faction warfare systems.
"""

import logging
import os
import pickle
from typing import Dict, List, Set, Tuple, Any, Optional
import networkx as nx

from eve_wiggin.api.cached_esi_client import get_cached_esi_client
from eve_wiggin.api.web_scraper_selenium import get_web_scraper_selenium
from eve_wiggin.api.puppeteer_scraper import get_puppeteer_scraper

logger = logging.getLogger(__name__)

# Constants
AMARR_FACTION_ID = 500003
MINMATAR_FACTION_ID = 500002
CALDARI_FACTION_ID = 500001
GALLENTE_FACTION_ID = 500004

# Permanent frontline systems
AMARR_PERMANENT_FRONTLINES = ["Arzad", "Kamela", "Huola", "Kourmonen"]
MINMATAR_PERMANENT_FRONTLINES = ["Amamake", "Teonusude", "Eszur", "Vard"]

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
        self.esi_client = get_cached_esi_client()
        self.web_scraper = get_puppeteer_scraper()  # Use the Puppeteer scraper instead
        
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
        
        # Load the pickle file
        with open(pickle_file, "rb") as f:
            systems_data = pickle.load(f)
        
        logger.info(f"Loaded {len(systems_data)} systems from {pickle_file}")
        
        # Create a new graph
        graph = nx.Graph()
        
        # Create a dictionary with string keys for consistent handling
        systems_dict = {str(system["solar_system_id"]): system for system in systems_data}
        
        # Add nodes to the graph
        for system_id, system in systems_dict.items():
            graph.add_node(
                system_id,
                name=system["solar_system_name"],
                region=system["region_name"],
                constellation=system["constellation_name"],
                system_id=system["solar_system_id"],
                owner_faction_id=None,  # Will be populated from ESI data
                occupier_faction_id=None,  # Will be populated from ESI data
                victory_points=0,
                victory_points_threshold=0,
                contested=False,
                contest_percentage=0.0,
                advantage=0.0,
                adjacency="rearguard"  # Default adjacency
            )
            
            # Add edges to the graph
            for adjacent_id in system["adjacent"]:
                # Convert to string for consistent handling
                adjacent_id = str(adjacent_id)
                if adjacent_id in systems_dict:
                    graph.add_edge(system_id, adjacent_id)
                    logger.debug(f"Added edge between {system['solar_system_name']} and {systems_dict[adjacent_id]['solar_system_name']}")
        
        # Log the number of nodes and edges
        logger.info(f"Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Check if any nodes have no adjacent systems
        for node in graph.nodes:
            neighbors = list(graph.neighbors(node))
            logger.debug(f"System {graph.nodes[node]['name']} has {len(neighbors)} adjacent systems")
        
        # Enrich the graph with ESI data
        await self._enrich_graph_with_esi_data(graph, faction_ids)
        
        # Enrich the graph with advantage data from the web scraper
        await self._enrich_graph_with_advantage_data(graph)
        
        # Determine adjacency for each system
        self._determine_adjacency(graph)
        
        return graph
    
    async def _enrich_graph_with_esi_data(self, graph: nx.Graph, faction_ids: List[int]) -> None:
        """
        Enrich the graph with data from the ESI API.
        
        Args:
            graph (nx.Graph): The graph to enrich.
            faction_ids (List[int]): The faction IDs to filter by.
        """
        logger.info("Enriching graph with ESI data...")
        
        # Get faction warfare systems from ESI
        fw_systems = await self.esi_client.get_fw_systems(faction_ids)
        
        # Create a dictionary for quick lookup
        fw_systems_dict = {str(system["solar_system_id"]): system for system in fw_systems}
        
        # Update the graph nodes with ESI data
        for node in graph.nodes:
            if node in fw_systems_dict:
                fw_system = fw_systems_dict[node]
                
                # Update node attributes
                graph.nodes[node]["owner_faction_id"] = fw_system["owner_faction_id"]
                graph.nodes[node]["occupier_faction_id"] = fw_system["occupier_faction_id"]
                graph.nodes[node]["victory_points"] = fw_system["victory_points"]
                graph.nodes[node]["victory_points_threshold"] = fw_system["victory_points_threshold"]
                graph.nodes[node]["contested"] = fw_system["contested"]
                
                # Calculate contest percentage
                if fw_system["victory_points_threshold"] > 0:
                    contest_percentage = fw_system["victory_points"] / fw_system["victory_points_threshold"] * 100
                    graph.nodes[node]["contest_percentage"] = contest_percentage
                
                logger.debug(f"Enriched {graph.nodes[node]['name']} with ESI data")
            else:
                logger.warning(f"System {graph.nodes[node]['name']} (ID: {node}) not found in ESI data")
    
    async def _enrich_graph_with_advantage_data(self, graph: nx.Graph) -> None:
        """
        Enrich the graph with advantage data from the web scraper.
        
        Args:
            graph (nx.Graph): The graph to enrich.
        """
        logger.info("Enriching graph with advantage data from web scraper...")
        
        # Get advantage data from the web scraper
        advantage_data = await self.web_scraper.get_advantage_data()
        
        # Update the graph nodes with advantage data
        for node in graph.nodes:
            system_name = graph.nodes[node]["name"]
            
            if system_name in advantage_data:
                graph.nodes[node]["advantage"] = advantage_data[system_name]
                logger.debug(f"Set advantage for {system_name} to {advantage_data[system_name]}")
            else:
                # If the system is not in the advantage data, calculate a default value
                # based on the contest percentage
                if graph.nodes[node]["contested"]:
                    # For contested systems, use a default value of 0.5 (neutral)
                    graph.nodes[node]["advantage"] = 0.5
                else:
                    # For uncontested systems, set advantage to 0 (no advantage)
                    graph.nodes[node]["advantage"] = 0.0
                
                logger.debug(f"Using default advantage for {system_name}: {graph.nodes[node]['advantage']}")
    
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
            system_name = graph.nodes[node]["name"]
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
            
            system_name = graph.nodes[node]["name"]
            occupier_faction_id = graph.nodes[node]["occupier_faction_id"]
            
            if not occupier_faction_id:
                logger.warning(f"System {system_name} has no occupier faction ID")
                continue
            
            # Check if the system is adjacent to an enemy-controlled system
            for neighbor in graph.neighbors(node):
                neighbor_occupier = graph.nodes[neighbor]["occupier_faction_id"]
                
                if not neighbor_occupier:
                    logger.warning(f"Neighbor {graph.nodes[neighbor]['name']} of {system_name} has no occupier faction ID")
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
            
            system_name = graph.nodes[node]["name"]
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

def get_fw_graph_builder() -> FWGraphBuilder:
    """
    Get a faction warfare graph builder instance.
    
    Returns:
        FWGraphBuilder: A faction warfare graph builder instance.
    """
    return fw_graph_builder
