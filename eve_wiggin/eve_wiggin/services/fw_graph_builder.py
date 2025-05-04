"""
Faction Warfare Graph Builder.

This module builds a NetworkX graph with all the necessary information for faction warfare analysis.
It focuses specifically on the Amarr/Minmatar warzone and avoids unnecessary data fetching.
"""

import logging
import pickle
import os
import networkx as nx
from typing import Dict, List, Set, Any, Optional, Tuple

from eve_wiggin.api.esi_client import get_esi_client
from eve_wiggin.models.faction_warfare import (
    FactionID, SystemAdjacency, SystemStatus
)

# Configure logging
logger = logging.getLogger(__name__)

# Path to filtered pickle files
AMA_MIN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ama_min.pickle")

# Define permanent frontline systems
AMARR_PERMANENT_FRONTLINES = {
    "Amamake", "Bosboger", "Auner", "Resbroko", "Evati", "Arnstur"
}

MINMATAR_PERMANENT_FRONTLINES = {
    "Raa", "Kamela", "Sosala", "Huola", "Anka", "Iesa", "Uusanen", "Saikamon", "Halmah"
}

class FWGraphBuilder:
    """
    Service for building a NetworkX graph with faction warfare data.
    """
    
    # Singleton instance
    _instance = None
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the faction warfare graph builder.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.esi_client = get_esi_client(access_token)
        self.graph = nx.Graph()
        self.system_id_to_name = {}
        self.system_name_to_id = {}
        
    async def build_warzone_graph(self) -> nx.Graph:
        """
        Build a NetworkX graph with all the necessary information for the Amarr/Minmatar warzone.
        
        Returns:
            nx.Graph: The NetworkX graph with faction warfare data.
        """
        try:
            # Step 1: Load the base graph from the filtered pickle file
            logger.info("Step 1: Loading base graph from filtered pickle file...")
            base_graph = self._load_base_graph()
            
            # Step 2: Get faction warfare systems from ESI API
            logger.info("Step 2: Getting faction warfare systems from ESI API...")
            fw_systems = await self._get_fw_systems()
            
            # Step 3: Enrich the graph with faction warfare data
            logger.info("Step 3: Enriching graph with faction warfare data...")
            self._enrich_graph_with_fw_data(base_graph, fw_systems)
            
            # Step 4: Determine system adjacency (frontline, command ops, rearguard)
            logger.info("Step 4: Determining system adjacency (frontline, command ops, rearguard)...")
            self._determine_system_adjacency(base_graph)
            
            logger.info(f"Built warzone graph with {base_graph.number_of_nodes()} nodes and {base_graph.number_of_edges()} edges")
            
            return base_graph
        except Exception as e:
            logger.error(f"Error building warzone graph: {e}", exc_info=True)
            # Return an empty graph in case of error
            return nx.Graph()
    
    def _load_base_graph(self) -> nx.Graph:
        """
        Load the base graph from the filtered pickle file.
        
        Returns:
            nx.Graph: The base NetworkX graph.
        """
        try:
            # Load the pickle file
            if not os.path.exists(AMA_MIN_FILE):
                logger.error(f"Pickle file not found: {AMA_MIN_FILE}")
                return nx.Graph()
            
            with open(AMA_MIN_FILE, 'rb') as f:
                systems_data = pickle.load(f)
            
            # Create a new undirected graph
            G = nx.Graph()
            
            # Add nodes to the graph
            for system_id, system_data in systems_data.items():
                # Convert system_id to string for consistency
                system_id = str(system_id)
                
                # Get system name
                system_name = system_data.get('solar_system_name', f"Unknown-{system_id}")
                
                # Store system ID to name mapping
                self.system_id_to_name[system_id] = system_name
                self.system_name_to_id[system_name] = system_id
                
                # Add node with all system attributes
                G.add_node(system_id, **system_data)
            
            # Add edges to the graph
            for system_id, system_data in systems_data.items():
                # Convert system_id to string for consistency
                system_id = str(system_id)
                
                # Get adjacent systems
                adjacent_systems = system_data.get('adjacent', [])
                
                # Convert adjacent_systems to strings if they are integers
                adjacent_systems = [str(adj_id) if isinstance(adj_id, int) else adj_id for adj_id in adjacent_systems]
                
                for adj_id in adjacent_systems:
                    # Check if the adjacent system is in our data
                    if adj_id in systems_data:
                        # Add edge if it doesn't already exist
                        if not G.has_edge(system_id, adj_id):
                            G.add_edge(system_id, adj_id)
            
            logger.info(f"Loaded base graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            return G
        
        except Exception as e:
            logger.error(f"Error loading base graph: {e}", exc_info=True)
            return nx.Graph()
    
    async def _get_fw_systems(self) -> Dict[str, Dict[str, Any]]:
        """
        Get faction warfare systems from the ESI API.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping system IDs to faction warfare data.
        """
        try:
            # Get faction warfare systems from ESI
            raw_systems = await self.esi_client.get_fw_systems()
            
            # Process systems
            fw_systems = {}
            for raw_system in raw_systems:
                system_id = str(raw_system["solar_system_id"])
                
                # Calculate contest percentage
                victory_points = raw_system["victory_points"]
                victory_points_threshold = raw_system["victory_points_threshold"]
                contest_percent = 0.0
                if victory_points_threshold > 0:
                    contest_percent = (victory_points / victory_points_threshold) * 100
                
                # Determine if this is an Amarr/Minmatar system
                occupier_faction_id = raw_system["occupier_faction_id"]
                if occupier_faction_id not in [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC]:
                    continue
                
                # Calculate advantage based on contested status and victory points
                # Advantage represents which faction has the upper hand in the system
                advantage = 0.0
                if raw_system["contested"] == "contested":
                    # If the system is contested, calculate advantage based on victory points
                    if victory_points_threshold > 0:
                        # Positive advantage means the occupier is winning
                        # Negative advantage means the owner is winning
                        advantage = ((victory_points / victory_points_threshold) - 0.5) * 2
                
                # Create system data
                fw_systems[system_id] = {
                    "owner_faction_id": raw_system["owner_faction_id"],
                    "occupier_faction_id": occupier_faction_id,
                    "contested": raw_system["contested"],
                    "victory_points": victory_points,
                    "victory_points_threshold": victory_points_threshold,
                    "advantage": advantage,
                    "contest_percent": contest_percent
                }
            
            logger.info(f"Got {len(fw_systems)} Amarr/Minmatar faction warfare systems from ESI")
            return fw_systems
        
        except Exception as e:
            logger.error(f"Error getting faction warfare systems: {e}", exc_info=True)
            return {}
    
    def _enrich_graph_with_fw_data(self, G: nx.Graph, fw_systems: Dict[str, Dict[str, Any]]) -> None:
        """
        Enrich the graph with faction warfare data.
        
        Args:
            G (nx.Graph): The NetworkX graph to enrich.
            fw_systems (Dict[str, Dict[str, Any]]): Dictionary mapping system IDs to faction warfare data.
        """
        try:
            # Add faction warfare data to nodes
            for system_id, fw_data in fw_systems.items():
                if system_id in G:
                    # Update node attributes with faction warfare data
                    nx.set_node_attributes(G, {system_id: fw_data})
            
            # Set default values for systems not in faction warfare
            for system_id in G.nodes():
                if system_id not in fw_systems:
                    # Set default values for non-faction warfare systems
                    default_data = {
                        "owner_faction_id": 0,  # 0 means not in faction warfare
                        "occupier_faction_id": 0,
                        "contested": SystemStatus.UNCONTESTED,
                        "victory_points": 0,
                        "victory_points_threshold": 0,
                        "advantage": 0.0,
                        "contest_percent": 0.0,
                        "adjacency": SystemAdjacency.REARGUARD  # Default adjacency
                    }
                    nx.set_node_attributes(G, {system_id: default_data})
            
            logger.info(f"Enriched graph with faction warfare data")
        
        except Exception as e:
            logger.error(f"Error enriching graph with faction warfare data: {e}", exc_info=True)
    
    def _determine_system_adjacency(self, G: nx.Graph) -> None:
        """
        Determine system adjacency (frontline, command ops, rearguard) for each node in the graph.
        
        Args:
            G (nx.Graph): The NetworkX graph to process.
        """
        try:
            # Step 1: Mark all systems as rearguard by default
            logger.info("Step 1: Marking all systems as rearguard by default...")
            for system_id in G.nodes():
                G.nodes[system_id]["adjacency"] = SystemAdjacency.REARGUARD
            
            # Step 2: Mark permanent frontline systems
            logger.info("Step 2: Marking permanent frontline systems...")
            self._mark_permanent_frontlines(G)
            
            # Step 3: Find frontline systems
            logger.info("Step 3: Finding frontline systems based on adjacency to enemy territory...")
            self._find_frontlines(G)
            
            # Step 4: Find command operations systems (one jump from frontlines)
            logger.info("Step 4: Finding command operations systems (one jump from frontlines)...")
            self._find_command_ops(G)
            
            # Count systems by adjacency
            frontlines = sum(1 for _, data in G.nodes(data=True) if data.get("adjacency") == SystemAdjacency.FRONTLINE)
            command_ops = sum(1 for _, data in G.nodes(data=True) if data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
            rearguards = sum(1 for _, data in G.nodes(data=True) if data.get("adjacency") == SystemAdjacency.REARGUARD)
            
            logger.info(f"Adjacency determination complete: {frontlines} frontlines, {command_ops} command ops, {rearguards} rearguards")
        
        except Exception as e:
            logger.error(f"Error determining system adjacency: {e}", exc_info=True)
    
    def _mark_permanent_frontlines(self, G: nx.Graph) -> None:
        """
        Mark permanent frontline systems based on the predefined lists.
        
        Args:
            G (nx.Graph): The NetworkX graph to process.
        """
        permanent_frontlines_marked = 0
        
        for system_id in G.nodes():
            system_name = G.nodes[system_id].get("solar_system_name", "")
            occupier_faction_id = G.nodes[system_id].get("occupier_faction_id", 0)
            
            # Check if this is a permanent frontline for the controlling faction
            if (occupier_faction_id == FactionID.AMARR_EMPIRE and 
                system_name in AMARR_PERMANENT_FRONTLINES):
                G.nodes[system_id]["adjacency"] = SystemAdjacency.FRONTLINE
                logger.info(f"Marked {system_name} as permanent Amarr frontline")
                permanent_frontlines_marked += 1
                
            if (occupier_faction_id == FactionID.MINMATAR_REPUBLIC and 
                system_name in MINMATAR_PERMANENT_FRONTLINES):
                G.nodes[system_id]["adjacency"] = SystemAdjacency.FRONTLINE
                logger.info(f"Marked {system_name} as permanent Minmatar frontline")
                permanent_frontlines_marked += 1
        
        logger.info(f"Marked {permanent_frontlines_marked} permanent frontline systems")
    
    def _find_frontlines(self, G: nx.Graph) -> None:
        """
        Find frontline systems using the NetworkX graph.
        
        Args:
            G (nx.Graph): The NetworkX graph to process.
        """
        # Get Amarr and Minmatar systems
        amarr_systems = [system_id for system_id, data in G.nodes(data=True) 
                         if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE]
        
        minmatar_systems = [system_id for system_id, data in G.nodes(data=True) 
                            if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC]
        
        logger.info(f"Found {len(amarr_systems)} Amarr systems and {len(minmatar_systems)} Minmatar systems")
        
        # For each Amarr system, check if it's adjacent to a Minmatar system
        amarr_frontlines_found = 0
        for amarr_id in amarr_systems:
            # Skip if already marked as frontline
            if G.nodes[amarr_id].get("adjacency") == SystemAdjacency.FRONTLINE:
                continue
            
            # Get adjacent systems
            adjacent_systems = list(G.neighbors(amarr_id))
            
            for adjacent_id in adjacent_systems:
                if adjacent_id in minmatar_systems:
                    # This Amarr system is adjacent to a Minmatar system, so it's a frontline
                    G.nodes[amarr_id]["adjacency"] = SystemAdjacency.FRONTLINE
                    system_name = G.nodes[amarr_id].get("solar_system_name", "")
                    adjacent_name = G.nodes[adjacent_id].get("solar_system_name", "")
                    logger.info(f"Marked {system_name} as Amarr frontline (adjacent to Minmatar system {adjacent_name})")
                    amarr_frontlines_found += 1
                    break
        
        # For each Minmatar system, check if it's adjacent to an Amarr system
        minmatar_frontlines_found = 0
        for minmatar_id in minmatar_systems:
            # Skip if already marked as frontline
            if G.nodes[minmatar_id].get("adjacency") == SystemAdjacency.FRONTLINE:
                continue
            
            # Get adjacent systems
            adjacent_systems = list(G.neighbors(minmatar_id))
            
            for adjacent_id in adjacent_systems:
                if adjacent_id in amarr_systems:
                    # This Minmatar system is adjacent to an Amarr system, so it's a frontline
                    G.nodes[minmatar_id]["adjacency"] = SystemAdjacency.FRONTLINE
                    system_name = G.nodes[minmatar_id].get("solar_system_name", "")
                    adjacent_name = G.nodes[adjacent_id].get("solar_system_name", "")
                    logger.info(f"Marked {system_name} as Minmatar frontline (adjacent to Amarr system {adjacent_name})")
                    minmatar_frontlines_found += 1
                    break
        
        logger.info(f"Found {amarr_frontlines_found} additional Amarr frontlines and {minmatar_frontlines_found} additional Minmatar frontlines")
    
    def _find_command_ops(self, G: nx.Graph) -> None:
        """
        Find command operations systems (one jump from frontlines) using the NetworkX graph.
        
        Args:
            G (nx.Graph): The NetworkX graph to process.
        """
        # Get frontline systems
        frontline_systems = [system_id for system_id, data in G.nodes(data=True) 
                             if data.get("adjacency") == SystemAdjacency.FRONTLINE]
        
        logger.info(f"Found {len(frontline_systems)} frontline systems to check for command ops neighbors")
        
        # For each frontline system, mark all adjacent systems of the same faction as command ops
        command_ops_found = 0
        for frontline_id in frontline_systems:
            frontline_faction = G.nodes[frontline_id].get("occupier_faction_id", 0)
            frontline_name = G.nodes[frontline_id].get("solar_system_name", "")
            
            # Get adjacent systems
            adjacent_systems = list(G.neighbors(frontline_id))
            
            for adjacent_id in adjacent_systems:
                adjacent_faction = G.nodes[adjacent_id].get("occupier_faction_id", 0)
                adjacent_adjacency = G.nodes[adjacent_id].get("adjacency", "")
                adjacent_name = G.nodes[adjacent_id].get("solar_system_name", "")
                
                if (adjacent_faction == frontline_faction and 
                    adjacent_adjacency != SystemAdjacency.FRONTLINE):
                    # This system is adjacent to a frontline of the same faction, so it's a command ops
                    G.nodes[adjacent_id]["adjacency"] = SystemAdjacency.COMMAND_OPERATIONS
                    logger.info(f"Marked {adjacent_name} as command ops (adjacent to frontline {frontline_name})")
                    command_ops_found += 1
        
        logger.info(f"Found {command_ops_found} command operations systems")


def get_fw_graph_builder(access_token: Optional[str] = None) -> FWGraphBuilder:
    """
    Get an instance of the faction warfare graph builder.
    
    Args:
        access_token (Optional[str], optional): The access token for authenticated requests.
    
    Returns:
        FWGraphBuilder: An instance of the faction warfare graph builder.
    """
    # Implement singleton pattern to avoid creating multiple instances
    if FWGraphBuilder._instance is None:
        FWGraphBuilder._instance = FWGraphBuilder(access_token)
        logger.info("Created new FWGraphBuilder instance")
    return FWGraphBuilder._instance
