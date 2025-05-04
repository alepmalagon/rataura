#!/usr/bin/env python3
"""
Demo script to load the warzone pickle file, convert it to a NetworkX graph,
and display some basic information about the graph.
"""

import logging
import json
import networkx as nx
import matplotlib.pyplot as plt
from eve_wiggin.graph_utils import load_pickle_to_dict, convert_to_networkx, get_warzone_graph, analyze_graph

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to demonstrate the graph utilities.
    """
    try:
        # Step 1: Load the Amarr-Minmatar warzone data
        logger.info("Step 1: Loading Amarr-Minmatar warzone data...")
        warzone = 'amarr_minmatar'
        graph, system_name_to_index, systems_data = get_warzone_graph(warzone)
        
        # Step 2: Output the list of dictionaries to the logs
        logger.info("Step 2: Outputting the list of dictionaries to the logs...")
        logger.info(f"Loaded {len(systems_data)} systems from the {warzone} warzone")
        
        # Print the first 3 systems as a sample
        for i, system in enumerate(systems_data[:3]):
            logger.info(f"System {i+1}:")
            logger.info(json.dumps(system, indent=2))
        
        # Step 3: Analyze the graph
        logger.info("Step 3: Analyzing the graph...")
        metrics = analyze_graph(graph)
        logger.info("Graph metrics:")
        logger.info(json.dumps(metrics, indent=2))
        
        # Step 4: Visualize the graph (optional, can be commented out for headless environments)
        logger.info("Step 4: Visualizing the graph...")
        try:
            # Use spring layout for visualization
            pos = nx.spring_layout(graph, seed=42)
            
            plt.figure(figsize=(12, 8))
            
            # Draw nodes
            nx.draw_networkx_nodes(graph, pos, node_size=50, alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(graph, pos, alpha=0.4)
            
            # Draw labels for high degree nodes only
            high_degree_nodes = [node['node_id'] for node in metrics['high_degree_nodes']]
            labels = {node_id: graph.nodes[node_id].get('name', f"Unknown-{node_id}") 
                     for node_id in high_degree_nodes}
            nx.draw_networkx_labels(graph, pos, labels=labels, font_size=10)
            
            plt.title(f"{warzone.replace('_', '-').title()} Warzone Graph")
            plt.axis('off')
            
            # Save the figure
            output_file = f"{warzone}_graph.png"
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Graph visualization saved to {output_file}")
            
            # Close the figure to free memory
            plt.close()
            
        except Exception as e:
            logger.warning(f"Could not visualize graph: {e}")
        
        logger.info("Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)

if __name__ == "__main__":
    main()

