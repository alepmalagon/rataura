#!/usr/bin/env python3
"""
Display all data for all nodes in the NetworkX graph after analysis is completed.

This script loads the NetworkX graph built by the FWGraphBuilder and logs all the data
for each node, providing a comprehensive view of the graph structure and node attributes.
"""

import asyncio
import logging
import os
import sys
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import the eve_wiggin package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder
from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define faction names for better readability
FACTION_NAMES = {
    FactionID.AMARR_EMPIRE: "Amarr Empire",
    FactionID.MINMATAR_REPUBLIC: "Minmatar Republic",
    0: "None"
}

# Define adjacency names for better readability
ADJACENCY_NAMES = {
    SystemAdjacency.FRONTLINE: "Frontline",
    SystemAdjacency.COMMAND_OPERATIONS: "Command Operations",
    SystemAdjacency.REARGUARD: "Rearguard"
}

async def display_graph_nodes():
    """
    Display all data for all nodes in the NetworkX graph after analysis is completed.
    """
    try:
        # Get the graph builder
        graph_builder = get_fw_graph_builder()
        
        # Build the warzone graph
        logger.info("Building warzone graph...")
        graph = await graph_builder.build_warzone_graph()
        
        # Log the graph statistics
        logger.info(f"Graph has {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Count systems by faction and adjacency
        amarr_systems = sum(1 for _, data in graph.nodes(data=True) 
                           if data.get("owner_faction_id") == FactionID.AMARR_EMPIRE)
        minmatar_systems = sum(1 for _, data in graph.nodes(data=True) 
                              if data.get("owner_faction_id") == FactionID.MINMATAR_REPUBLIC)
        neutral_systems = sum(1 for _, data in graph.nodes(data=True) 
                             if data.get("owner_faction_id") == 0)
        
        frontlines = sum(1 for _, data in graph.nodes(data=True) 
                        if data.get("adjacency") == SystemAdjacency.FRONTLINE)
        command_ops = sum(1 for _, data in graph.nodes(data=True) 
                         if data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        rearguards = sum(1 for _, data in graph.nodes(data=True) 
                        if data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        logger.info(f"Systems by faction: {amarr_systems} Amarr, {minmatar_systems} Minmatar, {neutral_systems} Neutral")
        logger.info(f"Systems by adjacency: {frontlines} Frontlines, {command_ops} Command Ops, {rearguards} Rearguards")
        
        # Get all nodes and sort them by system name for better readability
        nodes = sorted(
            [(node_id, data) for node_id, data in graph.nodes(data=True)],
            key=lambda x: x[1].get("solar_system_name", "")
        )
        
        # Display all node data
        logger.info("=== DETAILED NODE DATA ===")
        for i, (node_id, data) in enumerate(nodes, 1):
            system_name = data.get("solar_system_name", f"Unknown-{node_id}")
            owner_faction_id = data.get("owner_faction_id", 0)
            owner_faction_name = FACTION_NAMES.get(owner_faction_id, "Unknown")
            adjacency = data.get("adjacency", SystemAdjacency.REARGUARD)
            adjacency_name = ADJACENCY_NAMES.get(adjacency, "Unknown")
            
            # Format the node data for better readability
            formatted_data = {
                "system_id": node_id,
                "solar_system_name": system_name,
                "owner_faction": owner_faction_name,
                "adjacency": adjacency_name,
                "victory_points": data.get("victory_points", 0),
                "victory_points_threshold": data.get("victory_points_threshold", 0),
                "contest_percent": round(data.get("contest_percent", 0), 2),
                "advantage": round(data.get("advantage", 0), 2),
                "contested": data.get("contested", "uncontested"),
                "neighbors": [graph.nodes[n].get("solar_system_name", n) for n in graph.neighbors(node_id)]
            }
            
            # Log the node data
            logger.info(f"System #{i}: {system_name} (ID: {node_id})")
            logger.info(json.dumps(formatted_data, indent=2))
            logger.info("")
        
        logger.info("=== END OF NODE DATA ===")
        
    except Exception as e:
        logger.error(f"Error displaying graph nodes: {e}", exc_info=True)

if __name__ == "__main__":
    # Run the async function
    asyncio.run(display_graph_nodes())
