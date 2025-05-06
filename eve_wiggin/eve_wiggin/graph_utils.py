"""
Utilities for loading and converting warzone data to NetworkX graphs.
"""

import os
import pickle
import logging
import networkx as nx
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder

# Configure logging
logger = logging.getLogger(__name__)

# Define paths to filtered pickle files
AMA_MIN_FILE = os.path.join(os.path.dirname(__file__), "data", "ama_min.pickle")

def load_pickle_to_dict(pickle_file: str) -> List[Dict[str, Any]]:
    """
    Load a pickle file into a list of dictionaries.
    
    Args:
        pickle_file (str): Path to the pickle file.
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing the data.
    """
    try:
        if not os.path.exists(pickle_file):
            logger.error(f"Pickle file not found: {pickle_file}")
            return []
        
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        
        # Convert the dictionary to a list of dictionaries
        # Each item will have the system_id as a key in the dictionary
        result = []
        for system_id, system_data in data.items():
            # Add the system_id to the dictionary
            system_dict = system_data.copy()
            system_dict['system_id'] = system_id
            result.append(system_dict)
        
        logger.info(f"Loaded {len(result)} systems from {pickle_file}")
        return result
    
    except Exception as e:
        logger.error(f"Error loading pickle file: {e}", exc_info=True)
        return []

def convert_to_networkx(systems_data: List[Dict[str, Any]]) -> Tuple[nx.Graph, Dict[str, int]]:
    """
    Convert a list of system dictionaries to a NetworkX graph.
    
    Args:
        systems_data (List[Dict[str, Any]]): List of system dictionaries.
        
    Returns:
        Tuple[nx.Graph, Dict[str, int]]: NetworkX graph and a mapping of system names to node IDs.
    """
    try:
        # Create a new undirected graph
        G = nx.Graph()
        
        # Create a mapping of system IDs to indices in the systems_data list
        system_id_to_index = {system['system_id']: i for i, system in enumerate(systems_data)}
        
        # Create a mapping of system names to indices
        system_name_to_index = {}
        
        # Add nodes to the graph
        for i, system in enumerate(systems_data):
            system_name = system.get('solar_system_name', f"Unknown-{system['system_id']}")
            system_name_to_index[system_name] = i
            
            # Add node with all system attributes
            G.add_node(i, **system)
        
        # Add edges to the graph
        for i, system in enumerate(systems_data):
            # Get adjacent systems
            adjacent_systems = system.get('adjacent', [])
            
            # Convert adjacent_systems to strings if they are integers
            adjacent_systems = [str(adj_id) if isinstance(adj_id, int) else adj_id for adj_id in adjacent_systems]
            
            for adj_id in adjacent_systems:
                # Check if the adjacent system is in our data
                if adj_id in system_id_to_index:
                    j = system_id_to_index[adj_id]
                    # Add edge if it doesn't already exist
                    if not G.has_edge(i, j):
                        G.add_edge(i, j)
        
        logger.info(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        return G, system_name_to_index
    
    except Exception as e:
        logger.error(f"Error converting to NetworkX graph: {e}", exc_info=True)
        return nx.Graph(), {}

def get_warzone_graph(warzone: str = 'amarr_minmatar') -> Tuple[nx.Graph, Dict[str, int], List[Dict[str, Any]]]:
    """
    Get a NetworkX graph for a specific warzone.
    
    Args:
        warzone (str, optional): The warzone to get the graph for. 
                                 Only 'amarr_minmatar' is supported.
                                 Defaults to 'amarr_minmatar'.
        
    Returns:
        Tuple[nx.Graph, Dict[str, int], List[Dict[str, Any]]]: 
            - NetworkX graph
            - Mapping of system names to node IDs
            - Original list of system dictionaries
    """
    # Only support Amarr/Minmatar warzone
    if warzone.lower() != 'amarr_minmatar':
        logger.error(f"Invalid warzone: {warzone}. Only 'amarr_minmatar' is supported.")
        return nx.Graph(), {}, []
    
    # Load the pickle file
    systems_data = load_pickle_to_dict(AMA_MIN_FILE)
    
    # Convert to NetworkX graph
    graph, system_name_to_index = convert_to_networkx(systems_data)
    
    # Enrich the graph with capture effort data
    try:
        # Get the enriched graph with capture effort data
        enriched_graph = get_enriched_warzone_graph()
        
        # Copy capture effort data to our graph
        if enriched_graph and enriched_graph.number_of_nodes() > 0:
            for node in graph.nodes:
                system_name = graph.nodes[node].get('solar_system_name')
                
                # Find the corresponding node in the enriched graph
                for enriched_node in enriched_graph.nodes:
                    if enriched_graph.nodes[enriched_node].get('solar_system_name') == system_name:
                        # Copy capture effort data
                        graph.nodes[node]['capture_effort'] = enriched_graph.nodes[enriched_node].get('capture_effort', 0.0)
                        graph.nodes[node]['capture_effort_category'] = enriched_graph.nodes[enriched_node].get('capture_effort_category', 'Unknown')
                        break
            
            logger.info("Enriched graph with capture effort data")
        else:
            logger.warning("Could not enrich graph with capture effort data")
    except Exception as e:
        logger.error(f"Error enriching graph with capture effort data: {e}", exc_info=True)
    
    return graph, system_name_to_index, systems_data

def analyze_graph(G: nx.Graph) -> Dict[str, Any]:
    """
    Analyze a NetworkX graph and return various metrics.
    
    Args:
        G (nx.Graph): The graph to analyze.
        
    Returns:
        Dict[str, Any]: Dictionary of graph metrics.
    """
    metrics = {}
    
    # Basic metrics
    metrics['num_nodes'] = G.number_of_nodes()
    metrics['num_edges'] = G.number_of_edges()
    
    # Connectivity
    metrics['is_connected'] = nx.is_connected(G)
    
    if metrics['is_connected']:
        metrics['diameter'] = nx.diameter(G)
        metrics['average_shortest_path_length'] = nx.average_shortest_path_length(G)
    else:
        # Get the largest connected component
        largest_cc = max(nx.connected_components(G), key=len)
        largest_cc_graph = G.subgraph(largest_cc).copy()
        
        metrics['num_connected_components'] = nx.number_connected_components(G)
        metrics['largest_component_size'] = len(largest_cc)
        metrics['largest_component_diameter'] = nx.diameter(largest_cc_graph)
        metrics['largest_component_avg_path'] = nx.average_shortest_path_length(largest_cc_graph)
    
    # Degree statistics
    degrees = [d for _, d in G.degree()]
    metrics['min_degree'] = min(degrees)
    metrics['max_degree'] = max(degrees)
    metrics['avg_degree'] = sum(degrees) / len(degrees)
    
    # Find nodes with highest degree (most connections)
    high_degree_nodes = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:5]
    metrics['high_degree_nodes'] = [
        {
            'node_id': node_id,
            'degree': degree,
            'name': G.nodes[node_id].get('solar_system_name', f"Unknown-{node_id}")
        }
        for node_id, degree in high_degree_nodes
    ]
    
    return metrics

def get_enriched_warzone_graph() -> nx.Graph:
    """
    Get a NetworkX graph enriched with faction warfare data.
    This is a synchronous wrapper around the asynchronous fw_graph_builder.
    
    Returns:
        nx.Graph: The enriched NetworkX graph.
    """
    try:
        # Get the graph builder
        graph_builder = get_fw_graph_builder()
        
        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the build_warzone_graph method
        graph = loop.run_until_complete(graph_builder.build_warzone_graph())
        
        # Close the event loop
        loop.close()
        
        return graph
    except Exception as e:
        logger.error(f"Error getting enriched warzone graph: {e}", exc_info=True)
        return nx.Graph()
