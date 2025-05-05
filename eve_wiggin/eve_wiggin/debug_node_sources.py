#!/usr/bin/env python3
"""
Debug script to verify that NetworkX nodes are being populated correctly from the right sources.
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def debug_node_sources():
    """
    Debug the sources of data for NetworkX nodes.
    """
    logger.info("Debugging NetworkX node sources...")
    
    # Get the graph builder
    graph_builder = get_fw_graph_builder()
    
    # Build the graph
    graph = await graph_builder.build_graph()
    
    # Create a debug directory if it doesn't exist
    debug_dir = os.path.join(os.path.dirname(__file__), "debug")
    os.makedirs(debug_dir, exist_ok=True)
    
    # Create a report of node sources
    node_sources = {}
    
    for node in graph.nodes:
        node_data = graph.nodes[node]
        system_name = node_data.get("name", "Unknown")
        
        # Categorize data by source
        node_sources[system_name] = {
            "from_pickle": {
                "name": node_data.get("name"),
                "region": node_data.get("region"),
                "constellation": node_data.get("constellation"),
                "system_id": node_data.get("system_id"),
                "neighbors": list(graph.neighbors(node))
            },
            "from_esi_api": {
                "owner_faction_id": node_data.get("owner_faction_id"),
                "occupier_faction_id": node_data.get("occupier_faction_id"),
                "victory_points": node_data.get("victory_points"),
                "victory_points_threshold": node_data.get("victory_points_threshold"),
                "contested": node_data.get("contested"),
                "contest_percentage": node_data.get("contest_percentage")
            },
            "from_warzone_api": {
                "amarr_advantage": node_data.get("amarr_advantage"),
                "minmatar_advantage": node_data.get("minmatar_advantage"),
                "net_advantage": node_data.get("net_advantage")
            },
            "calculated": {
                "adjacency": node_data.get("adjacency")
            }
        }
    
    # Save the report to a JSON file
    report_path = os.path.join(debug_dir, "node_sources.json")
    with open(report_path, "w") as f:
        json.dump(node_sources, f, indent=2)
    
    logger.info(f"Saved node sources report to {report_path}")
    
    # Print a summary
    logger.info(f"Total nodes: {len(node_sources)}")
    
    # Check for any missing data
    missing_data = {}
    for system_name, sources in node_sources.items():
        system_missing = {}
        
        # Check pickle data
        if not sources["from_pickle"]["name"]:
            system_missing["name"] = True
        if not sources["from_pickle"]["region"]:
            system_missing["region"] = True
        if not sources["from_pickle"]["neighbors"]:
            system_missing["neighbors"] = True
        
        # Check ESI API data
        if sources["from_esi_api"]["owner_faction_id"] is None:
            system_missing["owner_faction_id"] = True
        if sources["from_esi_api"]["occupier_faction_id"] is None:
            system_missing["occupier_faction_id"] = True
        
        # Check warzone API data
        if sources["from_warzone_api"]["amarr_advantage"] == 0.0 and sources["from_warzone_api"]["minmatar_advantage"] == 0.0:
            system_missing["advantage"] = True
        
        if system_missing:
            missing_data[system_name] = system_missing
    
    if missing_data:
        logger.warning(f"Found {len(missing_data)} systems with missing data:")
        for system_name, missing in missing_data.items():
            logger.warning(f"  {system_name}: {', '.join(missing.keys())}")
    else:
        logger.info("All systems have complete data!")
    
    # Print a sample node
    sample_system = next(iter(node_sources.keys()))
    logger.info(f"Sample system data for {sample_system}:")
    logger.info(json.dumps(node_sources[sample_system], indent=2))

if __name__ == "__main__":
    asyncio.run(debug_node_sources())

