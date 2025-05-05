#!/usr/bin/env python3
"""
Debug script to verify that advantage data is being properly mapped to NetworkX nodes.
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder
from eve_wiggin.api.warzone_api_client import get_warzone_api_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def debug_advantage_mapping():
    """
    Debug the mapping of advantage data to NetworkX nodes.
    """
    logger.info("Debugging advantage data mapping...")
    
    # Get the warzone API client
    warzone_client = get_warzone_api_client()
    
    # Get advantage data directly from the API
    logger.info("Getting advantage data from warzone API...")
    advantage_data = await warzone_client.get_system_advantage_data(force_refresh=True)
    
    # Log the number of systems with advantage data
    logger.info(f"Got advantage data for {len(advantage_data)} systems")
    
    # Log a few examples of advantage data
    logger.info("Sample advantage data:")
    count = 0
    for system_id, data in advantage_data.items():
        logger.info(f"System ID: {system_id}, Amarr: {data['amarr']:.2f}, Minmatar: {data['minmatar']:.2f}, Net: {data['net_advantage']:.2f}")
        count += 1
        if count >= 5:
            break
    
    # Get the graph builder
    graph_builder = get_fw_graph_builder()
    
    # Build the graph
    logger.info("Building NetworkX graph...")
    graph = await graph_builder.build_graph()
    
    # Check how many nodes have advantage data
    nodes_with_advantage = 0
    nodes_with_default = 0
    
    for node in graph.nodes:
        amarr_advantage = graph.nodes[node]["amarr_advantage"]
        minmatar_advantage = graph.nodes[node]["minmatar_advantage"]
        
        if amarr_advantage != 0.0 or minmatar_advantage != 0.0:
            nodes_with_advantage += 1
        else:
            nodes_with_default += 1
    
    logger.info(f"Nodes with advantage data: {nodes_with_advantage}")
    logger.info(f"Nodes with default advantage: {nodes_with_default}")
    
    # Create a debug directory if it doesn't exist
    debug_dir = os.path.join(os.path.dirname(__file__), "debug")
    os.makedirs(debug_dir, exist_ok=True)
    
    # Save the advantage data to a file for reference
    advantage_file = os.path.join(debug_dir, "advantage_data.json")
    with open(advantage_file, "w") as f:
        # Convert keys to strings for JSON serialization
        serializable_data = {str(k): v for k, v in advantage_data.items()}
        json.dump(serializable_data, f, indent=2)
    
    logger.info(f"Saved advantage data to {advantage_file}")
    
    # Save node data to a file for reference
    node_data = {}
    for node in graph.nodes:
        node_data[node] = {
            "solar_system_name": graph.nodes[node]["solar_system_name"],
            "solar_system_id": graph.nodes[node]["solar_system_id"],
            "amarr_advantage": graph.nodes[node]["amarr_advantage"],
            "minmatar_advantage": graph.nodes[node]["minmatar_advantage"],
            "net_advantage": graph.nodes[node]["net_advantage"]
        }
    
    node_file = os.path.join(debug_dir, "node_advantage_data.json")
    with open(node_file, "w") as f:
        json.dump(node_data, f, indent=2)
    
    logger.info(f"Saved node advantage data to {node_file}")
    
    # Check for mismatches between advantage data and node data
    mismatches = []
    for node in graph.nodes:
        node_id = str(graph.nodes[node]["solar_system_id"])
        
        if node_id in advantage_data:
            api_amarr = advantage_data[node_id]["amarr"]
            api_minmatar = advantage_data[node_id]["minmatar"]
            
            node_amarr = graph.nodes[node]["amarr_advantage"]
            node_minmatar = graph.nodes[node]["minmatar_advantage"]
            
            if abs(api_amarr - node_amarr) > 0.01 or abs(api_minmatar - node_minmatar) > 0.01:
                mismatches.append({
                    "node_id": node,
                    "system_id": node_id,
                    "system_name": graph.nodes[node]["solar_system_name"],
                    "api_amarr": api_amarr,
                    "node_amarr": node_amarr,
                    "api_minmatar": api_minmatar,
                    "node_minmatar": node_minmatar
                })
    
    if mismatches:
        logger.warning(f"Found {len(mismatches)} mismatches between advantage data and node data:")
        for mismatch in mismatches[:5]:  # Show first 5 mismatches
            logger.warning(f"  System: {mismatch['system_name']} (ID: {mismatch['system_id']})")
            logger.warning(f"    API Amarr: {mismatch['api_amarr']:.2f}, Node Amarr: {mismatch['node_amarr']:.2f}")
            logger.warning(f"    API Minmatar: {mismatch['api_minmatar']:.2f}, Node Minmatar: {mismatch['node_minmatar']:.2f}")
    else:
        logger.info("No mismatches found between advantage data and node data!")

if __name__ == "__main__":
    asyncio.run(debug_advantage_mapping())

