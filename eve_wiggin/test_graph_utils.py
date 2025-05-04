#!/usr/bin/env python3
"""
Test script for the graph utilities.
"""

import logging
import json
from eve_wiggin.graph_utils import load_pickle_to_dict, get_warzone_graph, analyze_graph

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the graph utilities.
    """
    try:
        # Test loading the pickle file
        logger.info("Testing load_pickle_to_dict...")
        from eve_wiggin.graph_utils import AMA_MIN_FILE
        systems_data = load_pickle_to_dict(AMA_MIN_FILE)
        
        logger.info(f"Loaded {len(systems_data)} systems from {AMA_MIN_FILE}")
        
        # Print the first 3 systems as a sample
        for i, system in enumerate(systems_data[:3]):
            logger.info(f"System {i+1}:")
            logger.info(json.dumps(system, indent=2))
        
        # Test getting the warzone graph
        logger.info("\nTesting get_warzone_graph...")
        graph, system_name_to_index, _ = get_warzone_graph('amarr_minmatar')
        
        logger.info(f"Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
        # Test analyzing the graph
        logger.info("\nTesting analyze_graph...")
        metrics = analyze_graph(graph)
        
        logger.info("Graph metrics:")
        logger.info(json.dumps(metrics, indent=2))
        
        logger.info("Tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)

if __name__ == "__main__":
    main()

