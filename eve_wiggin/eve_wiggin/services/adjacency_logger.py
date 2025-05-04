#!/usr/bin/env python3
"""
Adjacency Logger for EVE Wiggin.

This module provides enhanced logging for the adjacency determination process
in the faction warfare graph builder. It logs detailed information about why
each system is classified as frontline, command operations, or rearguard.
"""

import logging
import networkx as nx
import os
import json
from typing import Dict, List, Set, Any, Optional, Tuple

from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency
from eve_wiggin.services.fw_graph_builder import (
    get_fw_graph_builder, AMARR_PERMANENT_FRONTLINES, MINMATAR_PERMANENT_FRONTLINES
)

# Configure logging
logger = logging.getLogger(__name__)

class AdjacencyLogger:
    """
    Service for logging detailed information about the adjacency determination process.
    """
    
    def __init__(self, graph: nx.Graph):
        """
        Initialize the adjacency logger.
        
        Args:
            graph (nx.Graph): The NetworkX graph to analyze.
        """
        self.graph = graph
        self.adjacency_reasons = {}
        
    def log_adjacency_reasoning(self) -> Dict[str, Dict[str, Any]]:
        """
        Log detailed reasoning for each system's adjacency classification.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping system IDs to their adjacency reasoning.
        """
        try:
            logger.info("=== ADJACENCY REASONING ANALYSIS ===")
            
            # Get all nodes and sort them by system name for better readability
            nodes = sorted(
                [(node_id, data) for node_id, data in self.graph.nodes(data=True)],
                key=lambda x: x[1].get("solar_system_name", "")
            )
            
            # Analyze each system
            for node_id, data in nodes:
                self._analyze_system_adjacency(node_id, data)
            
            # Log summary statistics
            self._log_adjacency_summary()
            
            logger.info("=== END OF ADJACENCY REASONING ANALYSIS ===")
            
            return self.adjacency_reasons
            
        except Exception as e:
            logger.error(f"Error logging adjacency reasoning: {e}", exc_info=True)
            return {}
    
    def _analyze_system_adjacency(self, system_id: str, system_data: Dict[str, Any]) -> None:
        """
        Analyze and log the reasoning behind a system's adjacency classification.
        
        Args:
            system_id (str): The ID of the system to analyze.
            system_data (Dict[str, Any]): The system's data from the graph.
        """
        system_name = system_data.get("solar_system_name", f"Unknown-{system_id}")
        adjacency = system_data.get("adjacency", SystemAdjacency.REARGUARD)
        occupier_faction_id = system_data.get("occupier_faction_id", 0)
        
        # Initialize reasoning data
        reasoning = {
            "system_id": system_id,
            "system_name": system_name,
            "adjacency": adjacency,
            "occupier_faction_id": occupier_faction_id,
            "reasons": [],
            "neighbors": []
        }
        
        # Get faction name for better readability
        faction_name = "None"
        if occupier_faction_id == FactionID.AMARR_EMPIRE:
            faction_name = "Amarr Empire"
        elif occupier_faction_id == FactionID.MINMATAR_REPUBLIC:
            faction_name = "Minmatar Republic"
        
        # Check if this is a permanent frontline
        if adjacency == SystemAdjacency.FRONTLINE:
            if occupier_faction_id == FactionID.AMARR_EMPIRE and system_name in AMARR_PERMANENT_FRONTLINES:
                reasoning["reasons"].append("Permanent Amarr frontline system")
            elif occupier_faction_id == FactionID.MINMATAR_REPUBLIC and system_name in MINMATAR_PERMANENT_FRONTLINES:
                reasoning["reasons"].append("Permanent Minmatar frontline system")
        
        # Check if this is a frontline due to being adjacent to enemy territory
        if adjacency == SystemAdjacency.FRONTLINE and not reasoning["reasons"]:
            # Get neighboring systems
            neighbors = list(self.graph.neighbors(system_id))
            
            # Check if any neighbors are controlled by the enemy faction
            enemy_neighbors = []
            for neighbor_id in neighbors:
                neighbor_data = self.graph.nodes[neighbor_id]
                neighbor_name = neighbor_data.get("solar_system_name", f"Unknown-{neighbor_id}")
                neighbor_faction = neighbor_data.get("occupier_faction_id", 0)
                
                # Check if this is an enemy system
                is_enemy = False
                if occupier_faction_id == FactionID.AMARR_EMPIRE and neighbor_faction == FactionID.MINMATAR_REPUBLIC:
                    is_enemy = True
                elif occupier_faction_id == FactionID.MINMATAR_REPUBLIC and neighbor_faction == FactionID.AMARR_EMPIRE:
                    is_enemy = True
                
                if is_enemy:
                    enemy_neighbors.append(neighbor_name)
            
            if enemy_neighbors:
                reasoning["reasons"].append(f"Adjacent to enemy systems: {', '.join(enemy_neighbors)}")
        
        # Check if this is a command operations system
        if adjacency == SystemAdjacency.COMMAND_OPERATIONS:
            # Get neighboring systems
            neighbors = list(self.graph.neighbors(system_id))
            
            # Check if any neighbors are frontline systems of the same faction
            frontline_neighbors = []
            for neighbor_id in neighbors:
                neighbor_data = self.graph.nodes[neighbor_id]
                neighbor_name = neighbor_data.get("solar_system_name", f"Unknown-{neighbor_id}")
                neighbor_faction = neighbor_data.get("occupier_faction_id", 0)
                neighbor_adjacency = neighbor_data.get("adjacency", "")
                
                # Check if this is a frontline system of the same faction
                if (neighbor_faction == occupier_faction_id and 
                    neighbor_adjacency == SystemAdjacency.FRONTLINE):
                    frontline_neighbors.append(neighbor_name)
            
            if frontline_neighbors:
                reasoning["reasons"].append(f"Adjacent to frontline systems of the same faction: {', '.join(frontline_neighbors)}")
        
        # If no specific reason was found, it's a rearguard by default
        if not reasoning["reasons"] and adjacency == SystemAdjacency.REARGUARD:
            reasoning["reasons"].append("Default classification (not a frontline or command operations system)")
        
        # Get all neighboring systems for reference
        for neighbor_id in self.graph.neighbors(system_id):
            neighbor_data = self.graph.nodes[neighbor_id]
            neighbor_name = neighbor_data.get("solar_system_name", f"Unknown-{neighbor_id}")
            neighbor_faction = neighbor_data.get("occupier_faction_id", 0)
            neighbor_adjacency = neighbor_data.get("adjacency", SystemAdjacency.REARGUARD)
            
            # Get faction name for better readability
            neighbor_faction_name = "None"
            if neighbor_faction == FactionID.AMARR_EMPIRE:
                neighbor_faction_name = "Amarr Empire"
            elif neighbor_faction == FactionID.MINMATAR_REPUBLIC:
                neighbor_faction_name = "Minmatar Republic"
            
            # Add neighbor info
            reasoning["neighbors"].append({
                "system_id": neighbor_id,
                "system_name": neighbor_name,
                "faction": neighbor_faction_name,
                "adjacency": neighbor_adjacency
            })
        
        # Store the reasoning
        self.adjacency_reasons[system_id] = reasoning
        
        # Log the reasoning
        logger.info(f"System: {system_name} ({system_id})")
        logger.info(f"  Faction: {faction_name}")
        logger.info(f"  Adjacency: {adjacency}")
        logger.info(f"  Reasoning: {', '.join(reasoning['reasons']) if reasoning['reasons'] else 'No specific reason found'}")
        logger.info(f"  Neighbors: {len(reasoning['neighbors'])} systems")
        logger.info("")
    
    def _log_adjacency_summary(self) -> None:
        """
        Log summary statistics about the adjacency classifications.
        """
        # Count systems by faction and adjacency
        amarr_systems = sum(1 for _, data in self.graph.nodes(data=True) 
                           if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE)
        minmatar_systems = sum(1 for _, data in self.graph.nodes(data=True) 
                              if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC)
        
        amarr_frontlines = sum(1 for _, data in self.graph.nodes(data=True) 
                              if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE and
                              data.get("adjacency") == SystemAdjacency.FRONTLINE)
        amarr_command_ops = sum(1 for _, data in self.graph.nodes(data=True) 
                               if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE and
                               data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        amarr_rearguards = sum(1 for _, data in self.graph.nodes(data=True) 
                              if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE and
                              data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        minmatar_frontlines = sum(1 for _, data in self.graph.nodes(data=True) 
                                 if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC and
                                 data.get("adjacency") == SystemAdjacency.FRONTLINE)
        minmatar_command_ops = sum(1 for _, data in self.graph.nodes(data=True) 
                                  if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC and
                                  data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        minmatar_rearguards = sum(1 for _, data in self.graph.nodes(data=True) 
                                 if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC and
                                 data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        logger.info("=== ADJACENCY SUMMARY ===")
        logger.info(f"Total Amarr systems: {amarr_systems}")
        logger.info(f"  - Frontlines: {amarr_frontlines}")
        logger.info(f"  - Command Ops: {amarr_command_ops}")
        logger.info(f"  - Rearguards: {amarr_rearguards}")
        logger.info(f"Total Minmatar systems: {minmatar_systems}")
        logger.info(f"  - Frontlines: {minmatar_frontlines}")
        logger.info(f"  - Command Ops: {minmatar_command_ops}")
        logger.info(f"  - Rearguards: {minmatar_rearguards}")
        
        # Check for permanent frontlines that aren't marked as frontlines
        missing_amarr_frontlines = []
        missing_minmatar_frontlines = []
        
        for system_id, data in self.graph.nodes(data=True):
            system_name = data.get("solar_system_name", "")
            occupier_faction_id = data.get("occupier_faction_id", 0)
            adjacency = data.get("adjacency", "")
            
            if (occupier_faction_id == FactionID.AMARR_EMPIRE and 
                system_name in AMARR_PERMANENT_FRONTLINES and
                adjacency != SystemAdjacency.FRONTLINE):
                missing_amarr_frontlines.append(system_name)
            
            if (occupier_faction_id == FactionID.MINMATAR_REPUBLIC and 
                system_name in MINMATAR_PERMANENT_FRONTLINES and
                adjacency != SystemAdjacency.FRONTLINE):
                missing_minmatar_frontlines.append(system_name)
        
        if missing_amarr_frontlines:
            logger.warning(f"Missing Amarr permanent frontlines: {', '.join(missing_amarr_frontlines)}")
        
        if missing_minmatar_frontlines:
            logger.warning(f"Missing Minmatar permanent frontlines: {', '.join(missing_minmatar_frontlines)}")
        
        # Check for systems that should be frontlines but aren't
        potential_frontlines = []
        
        for system_id, data in self.graph.nodes(data=True):
            if data.get("adjacency") != SystemAdjacency.FRONTLINE:
                system_name = data.get("solar_system_name", "")
                occupier_faction_id = data.get("occupier_faction_id", 0)
                
                # Skip systems with no faction
                if occupier_faction_id == 0:
                    continue
                
                # Check if this system has neighbors of the enemy faction
                neighbors = list(self.graph.neighbors(system_id))
                has_enemy_neighbor = False
                
                for neighbor_id in neighbors:
                    neighbor_faction = self.graph.nodes[neighbor_id].get("occupier_faction_id", 0)
                    
                    if ((occupier_faction_id == FactionID.AMARR_EMPIRE and 
                         neighbor_faction == FactionID.MINMATAR_REPUBLIC) or
                        (occupier_faction_id == FactionID.MINMATAR_REPUBLIC and 
                         neighbor_faction == FactionID.AMARR_EMPIRE)):
                        has_enemy_neighbor = True
                        break
                
                if has_enemy_neighbor:
                    potential_frontlines.append(system_name)
        
        if potential_frontlines:
            logger.warning(f"Potential frontlines not marked as such: {', '.join(potential_frontlines)}")

async def log_adjacency_reasoning():
    """
    Log detailed reasoning for each system's adjacency classification.
    """
    try:
        # Get the graph builder
        graph_builder = get_fw_graph_builder()
        
        # Build the warzone graph
        logger.info("Building warzone graph...")
        graph = await graph_builder.build_warzone_graph()
        
        # Create adjacency logger
        adjacency_logger = AdjacencyLogger(graph)
        
        # Log adjacency reasoning
        adjacency_logger.log_adjacency_reasoning()
        
    except Exception as e:
        logger.error(f"Error logging adjacency reasoning: {e}", exc_info=True)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Run the async function
    import asyncio
    asyncio.run(log_adjacency_reasoning())

