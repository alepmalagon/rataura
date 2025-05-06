"""
Display capture effort metrics for Amarr systems.

This script loads the NetworkX graph built by the FWGraphBuilder and displays
the capture effort metrics for all Amarr-occupied systems.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Any, Optional
import networkx as nx
from tabulate import tabulate

# Add the parent directory to the path so we can import the eve_wiggin package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder
from eve_wiggin.services.capture_effort_analyzer import get_capture_effort_analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
AMARR_FACTION_ID = 500003

async def display_capture_effort():
    """
    Display capture effort metrics for Amarr systems.
    """
    logger.info("Loading faction warfare graph...")
    
    # Get the graph builder
    graph_builder = get_fw_graph_builder()
    
    # Build the graph
    graph = await graph_builder.build_graph()
    
    logger.info(f"Loaded graph with {graph.number_of_nodes()} nodes")
    
    # Filter for Amarr-occupied systems
    amarr_systems = []
    for node in graph.nodes:
        if graph.nodes[node].get("occupier_faction_id") == AMARR_FACTION_ID:
            amarr_systems.append({
                "system_name": graph.nodes[node]["solar_system_name"],
                "region": graph.nodes[node]["region_name"],
                "adjacency": graph.nodes[node]["adjacency"],
                "victory_points": graph.nodes[node]["victory_points"],
                "vp_threshold": graph.nodes[node]["victory_points_threshold"],
                "amarr_advantage": graph.nodes[node]["amarr_advantage"],
                "minmatar_advantage": graph.nodes[node]["minmatar_advantage"],
                "capture_effort": graph.nodes[node]["capture_effort"],
                "category": graph.nodes[node]["capture_effort_category"]
            })
    
    # Sort by capture effort (easiest to hardest)
    amarr_systems.sort(key=lambda x: x["capture_effort"])
    
    # Display the results
    headers = [
        "System", "Region", "Adjacency", "VP", "VP Threshold", 
        "Amarr Adv", "Minmatar Adv", "Capture Effort", "Category"
    ]
    
    table_data = [
        [
            system["system_name"],
            system["region"],
            system["adjacency"],
            system["victory_points"],
            system["vp_threshold"],
            f"{system['amarr_advantage']:.2f}",
            f"{system['minmatar_advantage']:.2f}",
            f"{system['capture_effort']:.2f}",
            system["category"]
        ]
        for system in amarr_systems
    ]
    
    print("\nCAPTURE EFFORT ANALYSIS FOR AMARR SYSTEMS")
    print("=========================================")
    print(f"Total Amarr systems: {len(amarr_systems)}")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Display summary by category
    categories = {}
    for system in amarr_systems:
        category = system["category"]
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    print("\nSUMMARY BY CATEGORY")
    print("==================")
    for category, count in sorted(categories.items(), key=lambda x: [
        "Very Easy", "Easy", "Moderate", "Hard", "Very Hard"
    ].index(x[0])):
        print(f"{category}: {count} systems ({count/len(amarr_systems)*100:.1f}%)")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(display_capture_effort())

