"""
Module for analyzing the effort required to capture Amarr systems.
"""

import logging
import networkx as nx
from typing import Dict, Any, Optional, List

# Configure logging
logger = logging.getLogger(__name__)

# Constants
AMARR_FACTION_ID = 500003
MINMATAR_FACTION_ID = 500002
VARD_SYSTEM_NAME = "Vard"  # Base system for Minmatar corporation

class CaptureEffortAnalyzer:
    """
    Service for analyzing the effort required to capture Amarr systems.
    """
    
    def __init__(self):
        """
        Initialize the capture effort analyzer.
        """
        self.vard_system_id = None
    
    def analyze_capture_effort(self, graph: nx.Graph) -> None:
        """
        Analyze the effort required to capture Amarr systems and add the metric to the graph.
        
        The capture effort is calculated based on:
        1. Distance from Vard (systems that are far from Vard would require travel and more effort)
        2. Amarr Advantage vs Minmatar Advantage (Systems with a net amarr advantage will be harder to capture)
        3. Amount of Victory Points (the more VPs the easier to capture)
        4. Adjacency (Frontlines are easier to capture, Command Ops are hard to capture, Rearguards are almost impossible to capture)
        
        Args:
            graph (nx.Graph): The NetworkX graph to analyze.
        """
        logger.info("Analyzing capture effort for Amarr systems...")
        
        # Find Vard system ID
        self.vard_system_id = self._find_system_by_name(graph, VARD_SYSTEM_NAME)
        if not self.vard_system_id:
            logger.error(f"Could not find system '{VARD_SYSTEM_NAME}' in the graph. Capture effort analysis will be inaccurate.")
            # Use a fallback approach - find any Minmatar system to use as a reference
            for node in graph.nodes:
                if graph.nodes[node].get("occupier_faction_id") == MINMATAR_FACTION_ID:
                    self.vard_system_id = node
                    logger.warning(f"Using {graph.nodes[node]['solar_system_name']} as a fallback reference system for Minmatar.")
                    break
        
        # Calculate capture effort for each Amarr system
        for node in graph.nodes:
            # Only calculate for Amarr-occupied systems
            if graph.nodes[node].get("occupier_faction_id") == AMARR_FACTION_ID:
                capture_effort = self._calculate_capture_effort(graph, node)
                graph.nodes[node]["capture_effort"] = capture_effort
                
                # Add a human-readable capture effort category
                effort_category = self._categorize_capture_effort(capture_effort)
                graph.nodes[node]["capture_effort_category"] = effort_category
                
                logger.debug(f"Calculated capture effort for {graph.nodes[node]['solar_system_name']}: {capture_effort:.2f} ({effort_category})")
    
    def _find_system_by_name(self, graph: nx.Graph, system_name: str) -> Optional[str]:
        """
        Find a system node ID by its name.
        
        Args:
            graph (nx.Graph): The NetworkX graph to search.
            system_name (str): The name of the system to find.
            
        Returns:
            Optional[str]: The node ID of the system, or None if not found.
        """
        for node in graph.nodes:
            if graph.nodes[node].get("solar_system_name") == system_name:
                return node
        return None
    
    def _calculate_capture_effort(self, graph: nx.Graph, node: str) -> float:
        """
        Calculate the capture effort for a specific Amarr system.
        
        The capture effort is a value between 0 and 100, where:
        - 0 means very easy to capture
        - 100 means extremely difficult to capture
        
        Args:
            graph (nx.Graph): The NetworkX graph.
            node (str): The node ID of the system to calculate capture effort for.
            
        Returns:
            float: The calculated capture effort value.
        """
        # Initialize base effort
        base_effort = 50.0  # Start at a neutral point
        
        # 1. Distance from Vard factor (0-30 points)
        distance_factor = self._calculate_distance_factor(graph, node)
        
        # 2. Advantage factor (0-30 points)
        advantage_factor = self._calculate_advantage_factor(graph, node)
        
        # 3. Victory Points factor (-20 to 0 points, more VPs = easier to capture)
        vp_factor = self._calculate_vp_factor(graph, node)
        
        # 4. Adjacency factor (0-40 points)
        adjacency_factor = self._calculate_adjacency_factor(graph, node)
        
        # Calculate total effort
        total_effort = base_effort + distance_factor + advantage_factor + vp_factor + adjacency_factor
        
        # Ensure the result is between 0 and 100
        total_effort = max(0, min(100, total_effort))
        
        return total_effort
    
    def _calculate_distance_factor(self, graph: nx.Graph, node: str) -> float:
        """
        Calculate the distance factor for capture effort.
        Systems farther from Vard are harder to capture.
        
        Args:
            graph (nx.Graph): The NetworkX graph.
            node (str): The node ID of the system.
            
        Returns:
            float: The distance factor (0-30).
        """
        if not self.vard_system_id:
            return 15.0  # Default middle value if Vard is not found
        
        try:
            # Calculate shortest path length
            path_length = nx.shortest_path_length(graph, source=self.vard_system_id, target=node)
            
            # Normalize to a 0-30 scale
            # Assuming maximum reasonable distance is 15 jumps
            max_distance = 15
            distance_factor = (path_length / max_distance) * 30
            
            # Cap at 30
            return min(30, distance_factor)
        
        except nx.NetworkXNoPath:
            logger.warning(f"No path found from Vard to {graph.nodes[node]['solar_system_name']}. Using maximum distance factor.")
            return 30.0  # Maximum difficulty if no path exists
        except Exception as e:
            logger.error(f"Error calculating distance factor: {e}", exc_info=True)
            return 15.0  # Default middle value on error
    
    def _calculate_advantage_factor(self, graph: nx.Graph, node: str) -> float:
        """
        Calculate the advantage factor for capture effort.
        Systems with higher Amarr advantage are harder to capture.
        
        Args:
            graph (nx.Graph): The NetworkX graph.
            node (str): The node ID of the system.
            
        Returns:
            float: The advantage factor (0-30).
        """
        try:
            # Get advantage values
            amarr_advantage = graph.nodes[node].get("amarr_advantage", 0.0)
            minmatar_advantage = graph.nodes[node].get("minmatar_advantage", 0.0)
            
            # Calculate net advantage (positive means Amarr advantage)
            net_advantage = amarr_advantage - minmatar_advantage
            
            # Scale to 0-30 range
            # Net advantage ranges from -1 to 1, so we scale and shift
            advantage_factor = (net_advantage + 1) * 15
            
            return advantage_factor
        
        except Exception as e:
            logger.error(f"Error calculating advantage factor: {e}", exc_info=True)
            return 15.0  # Default middle value on error
    
    def _calculate_vp_factor(self, graph: nx.Graph, node: str) -> float:
        """
        Calculate the Victory Points factor for capture effort.
        Systems with more VPs are easier to capture (negative factor).
        
        Args:
            graph (nx.Graph): The NetworkX graph.
            node (str): The node ID of the system.
            
        Returns:
            float: The VP factor (-20 to 0).
        """
        try:
            # Get VP values
            victory_points = graph.nodes[node].get("victory_points", 0)
            victory_points_threshold = graph.nodes[node].get("victory_points_threshold", 3000)
            
            # Calculate VP percentage
            if victory_points_threshold > 0:
                vp_percentage = victory_points / victory_points_threshold
            else:
                vp_percentage = 0
            
            # Scale to -20 to 0 range (more VPs = easier to capture)
            vp_factor = -20 * vp_percentage
            
            return vp_factor
        
        except Exception as e:
            logger.error(f"Error calculating VP factor: {e}", exc_info=True)
            return -10.0  # Default middle value on error
    
    def _calculate_adjacency_factor(self, graph: nx.Graph, node: str) -> float:
        """
        Calculate the adjacency factor for capture effort.
        Frontlines are easier to capture, Command Ops are hard, Rearguards are almost impossible.
        
        Args:
            graph (nx.Graph): The NetworkX graph.
            node (str): The node ID of the system.
            
        Returns:
            float: The adjacency factor (0-40).
        """
        try:
            # Get adjacency type
            adjacency = graph.nodes[node].get("adjacency", "rearguard")
            
            # Assign factor based on adjacency type
            if adjacency == "frontline":
                return 0.0  # Easiest to capture
            elif adjacency == "command_ops":
                return 20.0  # Harder to capture
            else:  # rearguard
                return 40.0  # Hardest to capture
        
        except Exception as e:
            logger.error(f"Error calculating adjacency factor: {e}", exc_info=True)
            return 20.0  # Default middle value on error
    
    def _categorize_capture_effort(self, effort: float) -> str:
        """
        Categorize the capture effort into a human-readable category.
        
        Args:
            effort (float): The calculated capture effort value.
            
        Returns:
            str: The capture effort category.
        """
        if effort < 20:
            return "Very Easy"
        elif effort < 40:
            return "Easy"
        elif effort < 60:
            return "Moderate"
        elif effort < 80:
            return "Hard"
        else:
            return "Very Hard"


# Create a singleton instance
capture_effort_analyzer = CaptureEffortAnalyzer()

def get_capture_effort_analyzer() -> CaptureEffortAnalyzer:
    """
    Get the capture effort analyzer instance.
    
    Returns:
        CaptureEffortAnalyzer: The capture effort analyzer instance.
    """
    return capture_effort_analyzer

