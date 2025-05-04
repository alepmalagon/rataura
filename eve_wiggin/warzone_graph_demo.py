#!/usr/bin/env python3
"""
Demo script to show how to use the new NetworkX graph functionality.
"""

import os
import sys
import logging
import asyncio
import networkx as nx
import matplotlib.pyplot as plt
from pprint import pformat

# Add the parent directory to the path so we can import the eve_wiggin package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder
from eve_wiggin.graph_utils import analyze_graph
from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """
    Main function to demonstrate the NetworkX graph functionality.
    """
    try:
        # Get the graph builder
        graph_builder = get_fw_graph_builder()
        
        # Build the warzone graph
        logger.info("Building warzone graph...")
        graph = await graph_builder.build_warzone_graph()
        
        # Log basic graph information
        logger.info(f"Graph has {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Analyze the graph
        logger.info("Analyzing graph...")
        metrics = analyze_graph(graph)
        logger.info(f"Graph metrics:\n{pformat(metrics)}")
        
        # Count systems by faction and adjacency
        amarr_systems = sum(1 for _, data in graph.nodes(data=True) 
                           if data.get("owner_faction_id") == FactionID.AMARR_EMPIRE)
        minmatar_systems = sum(1 for _, data in graph.nodes(data=True) 
                              if data.get("owner_faction_id") == FactionID.MINMATAR_REPUBLIC)
        
        frontlines = sum(1 for _, data in graph.nodes(data=True) 
                        if data.get("adjacency") == SystemAdjacency.FRONTLINE)
        command_ops = sum(1 for _, data in graph.nodes(data=True) 
                         if data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        rearguards = sum(1 for _, data in graph.nodes(data=True) 
                        if data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        logger.info(f"Amarr systems: {amarr_systems}")
        logger.info(f"Minmatar systems: {minmatar_systems}")
        logger.info(f"Frontline systems: {frontlines}")
        logger.info(f"Command operations systems: {command_ops}")
        logger.info(f"Rearguard systems: {rearguards}")
        
        # Log some sample system data
        logger.info("Sample system data:")
        for i, (system_id, data) in enumerate(list(graph.nodes(data=True))[:5]):
            logger.info(f"System {i+1}: {data.get('solar_system_name', 'Unknown')} (ID: {system_id})")
            logger.info(f"  Owner: {data.get('owner_faction_id', 'Unknown')}")
            logger.info(f"  Adjacency: {data.get('adjacency', 'Unknown')}")
            logger.info(f"  Victory Points: {data.get('victory_points', 0)}/{data.get('victory_points_threshold', 0)}")
            logger.info(f"  Contest Percent: {data.get('contest_percent', 0):.2f}%")
            logger.info(f"  Adjacent Systems: {len(list(graph.neighbors(system_id)))}")
        
        # Visualize the graph (optional)
        # Note: This can be slow for large graphs
        try:
            logger.info("Visualizing graph...")
            
            # Create a position layout
            pos = nx.spring_layout(graph, seed=42)
            
            # Create a figure
            plt.figure(figsize=(12, 8))
            
            # Draw nodes by faction
            amarr_nodes = [n for n, d in graph.nodes(data=True) 
                          if d.get("owner_faction_id") == FactionID.AMARR_EMPIRE]
            minmatar_nodes = [n for n, d in graph.nodes(data=True) 
                             if d.get("owner_faction_id") == FactionID.MINMATAR_REPUBLIC]
            other_nodes = [n for n, d in graph.nodes(data=True) 
                          if d.get("owner_faction_id") not in [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC]]
            
            # Draw nodes by adjacency
            frontline_nodes = [n for n, d in graph.nodes(data=True) 
                              if d.get("adjacency") == SystemAdjacency.FRONTLINE]
            command_ops_nodes = [n for n, d in graph.nodes(data=True) 
                                if d.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS]
            rearguard_nodes = [n for n, d in graph.nodes(data=True) 
                              if d.get("adjacency") == SystemAdjacency.REARGUARD]
            
            # Draw nodes
            nx.draw_networkx_nodes(graph, pos, nodelist=amarr_nodes, node_color='gold', node_size=100, label='Amarr')
            nx.draw_networkx_nodes(graph, pos, nodelist=minmatar_nodes, node_color='red', node_size=100, label='Minmatar')
            nx.draw_networkx_nodes(graph, pos, nodelist=other_nodes, node_color='gray', node_size=50, label='Other')
            
            # Draw edges
            nx.draw_networkx_edges(graph, pos, width=0.5, alpha=0.5)
            
            # Draw labels for frontline systems
            frontline_labels = {n: graph.nodes[n].get('solar_system_name', n) for n in frontline_nodes}
            nx.draw_networkx_labels(graph, pos, labels=frontline_labels, font_size=8)
            
            # Add a title and legend
            plt.title('Amarr-Minmatar Warzone Graph')
            plt.legend()
            
            # Save the figure
            plt.savefig('warzone_graph.png', dpi=300, bbox_inches='tight')
            logger.info("Graph visualization saved to warzone_graph.png")
            
        except Exception as e:
            logger.error(f"Error visualizing graph: {e}", exc_info=True)
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())

