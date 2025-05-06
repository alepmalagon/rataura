"""
Test script for the capture effort analyzer.

This script loads the NetworkX graph, analyzes the capture effort for Amarr systems,
and displays the results.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, List, Any, Optional

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

async def test_capture_effort():
    """
    Test the capture effort analyzer.
    """
    logger.info("Testing capture effort analyzer...")
    
    # Get the graph builder
    graph_builder = get_fw_graph_builder()
    
    # Build the graph
    graph = await graph_builder.build_graph()
    
    logger.info(f"Built graph with {graph.number_of_nodes()} nodes")
    
    # Get the capture effort analyzer
    capture_effort_analyzer = get_capture_effort_analyzer()
    
    # Analyze capture effort
    capture_effort_analyzer.analyze_capture_effort(graph)
    
    # Display results for Amarr systems
    amarr_systems = []
    for node in graph.nodes:
        if graph.nodes[node].get("occupier_faction_id") == AMARR_FACTION_ID:
            amarr_systems.append({
                "name": graph.nodes[node]["solar_system_name"],
                "capture_effort": graph.nodes[node]["capture_effort"],
                "category": graph.nodes[node]["capture_effort_category"]
            })
    
    # Sort by capture effort (easiest to hardest)
    amarr_systems.sort(key=lambda x: x["capture_effort"])
    
    # Display results
    logger.info(f"Found {len(amarr_systems)} Amarr systems")
    logger.info("Capture effort results (easiest to hardest):")
    for system in amarr_systems:
        logger.info(f"{system['name']}: {system['capture_effort']:.2f} ({system['category']})")
    
    # Display summary by category
    categories = {}
    for system in amarr_systems:
        category = system["category"]
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    logger.info("Summary by category:")
    for category, count in sorted(categories.items(), key=lambda x: [
        "Very Easy", "Easy", "Moderate", "Hard", "Very Hard"
    ].index(x[0])):
        logger.info(f"{category}: {count} systems ({count/len(amarr_systems)*100:.1f}%)")

if __name__ == "__main__":
    # Run the async function
    asyncio.run(test_capture_effort())

