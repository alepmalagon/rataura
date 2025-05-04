"""
Web-based visualization for EVE Wiggin.
"""

import logging
import json
from typing import Dict, List, Any, Optional
import html

from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency, SystemStatus

# Configure logging
logger = logging.getLogger(__name__)


class WebVisualizer:
    """
    Web-based visualizer for faction warfare data.
    """
    
    def __init__(self):
        """
        Initialize the web visualizer.
        """
        # Define faction colors
        self.faction_colors = {
            FactionID.AMARR_EMPIRE: "#FFD700",  # Gold
            FactionID.MINMATAR_REPUBLIC: "#FF4500",  # Red-Orange
            FactionID.CALDARI_STATE: "#1E90FF",  # Dodger Blue
            FactionID.GALLENTE_FEDERATION: "#32CD32",  # Lime Green
        }
        
        # Define adjacency colors
        self.adjacency_colors = {
            SystemAdjacency.FRONTLINE: "#FF6347",  # Tomato
            SystemAdjacency.COMMAND_OPERATIONS: "#FFD700",  # Gold
            SystemAdjacency.REARGUARD: "#32CD32",  # Lime Green
        }
        
        # Define faction names
        self.faction_names = {
            FactionID.AMARR_EMPIRE: "Amarr Empire",
            FactionID.MINMATAR_REPUBLIC: "Minmatar Republic",
            FactionID.CALDARI_STATE: "Caldari State",
            FactionID.GALLENTE_FEDERATION: "Gallente Federation",
        }
        
        # Initialize HTML output
        self.html_output = []
    
    def reset_output(self):
        """Reset the HTML output."""
        self.html_output = []
    
    def get_html(self) -> str:
        """
        Get the complete HTML output.
        
        Returns:
            str: The HTML output.
        """
        return "\n".join(self.html_output)
    
    def display_warzone_summary(self, warzone_data: Dict[str, Any]) -> None:
        """
        Display a summary of the warzone status.
        
        Args:
            warzone_data (Dict[str, Any]): The warzone data to display.
        """
        self.html_output.append('<div class="card mb-4">')
        self.html_output.append('<div class="card-header bg-primary text-white">')
        self.html_output.append(f'<h3>Warzone Summary</h3>')
        self.html_output.append('</div>')
        self.html_output.append('<div class="card-body">')
        
        self.html_output.append(f'<h4>{html.escape(warzone_data["name"])}</h4>')
        self.html_output.append(f'<p>Total Systems: {warzone_data["total_systems"]}</p>')
        
        # Display systems controlled by each faction
        self.html_output.append('<h5>Systems Control</h5>')
        self.html_output.append('<div class="row">')
        
        for faction_id, count in warzone_data['systems'].items():
            faction_id_int = int(faction_id)
            percentage = warzone_data['control_percentages'].get(faction_id_int, 0)
            faction_color = self.faction_colors.get(faction_id_int, "#FFFFFF")
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            self.html_output.append('<div class="col-md-6 mb-3">')
            self.html_output.append(f'<div class="card" style="border-left: 5px solid {faction_color};">')
            self.html_output.append('<div class="card-body">')
            self.html_output.append(f'<h5 class="card-title">{html.escape(faction_name)}</h5>')
            self.html_output.append(f'<p class="card-text">{count} systems ({percentage:.1f}%)</p>')
            
            # Add progress bar
            self.html_output.append(f'<div class="progress">')
            self.html_output.append(f'<div class="progress-bar" role="progressbar" style="width: {percentage}%; background-color: {faction_color};" aria-valuenow="{percentage}" aria-valuemin="0" aria-valuemax="100"></div>')
            self.html_output.append('</div>')
            
            self.html_output.append('</div>')
            self.html_output.append('</div>')
            self.html_output.append('</div>')
        
        self.html_output.append('</div>')  # End row
        
        # Display contested systems
        self.html_output.append('<h5>Contested Systems</h5>')
        self.html_output.append('<div class="row">')
        
        for faction_id, count in warzone_data['contested'].items():
            faction_id_int = int(faction_id)
            faction_color = self.faction_colors.get(faction_id_int, "#FFFFFF")
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            self.html_output.append('<div class="col-md-6 mb-3">')
            self.html_output.append(f'<div class="card" style="border-left: 5px solid {faction_color};">')
            self.html_output.append('<div class="card-body">')
            self.html_output.append(f'<h5 class="card-title">Contested by {html.escape(faction_name)}</h5>')
            self.html_output.append(f'<p class="card-text">{count} systems</p>')
            self.html_output.append('</div>')
            self.html_output.append('</div>')
            self.html_output.append('</div>')
        
        self.html_output.append('</div>')  # End row
        self.html_output.append('</div>')  # End card-body
        self.html_output.append('</div>')  # End card
    
    def display_faction_stats(self, faction_stats: Dict[str, Any]) -> None:
        """
        Display faction warfare statistics.
        
        Args:
            faction_stats (Dict[str, Any]): The faction statistics to display.
        """
        self.html_output.append('<div class="card mb-4">')
        self.html_output.append('<div class="card-header bg-primary text-white">')
        self.html_output.append('<h3>Faction Statistics</h3>')
        self.html_output.append('</div>')
        self.html_output.append('<div class="card-body">')
        
        self.html_output.append('<div class="row">')
        
        for faction_id_str, stats in faction_stats.items():
            # Convert faction_id to integer if it's a string
            faction_id_int = int(faction_id_str) if isinstance(faction_id_str, str) else faction_id_str
            
            # Get faction color and name
            faction_color = self.faction_colors.get(faction_id_int, "#FFFFFF")
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id_str}")
            
            # Create faction stats card
            self.html_output.append('<div class="col-md-6 mb-3">')
            self.html_output.append(f'<div class="card" style="border-left: 5px solid {faction_color};">')
            self.html_output.append('<div class="card-body">')
            self.html_output.append(f'<h5 class="card-title">{html.escape(faction_name)}</h5>')
            
            # Display stats
            self.html_output.append('<ul class="list-group list-group-flush">')
            
            # Handle both dictionary and object access patterns
            if isinstance(stats, dict):
                pilots = stats.get("pilots", 0)
                systems_controlled = stats.get("systems_controlled", 0)
                victory_points_yesterday = stats.get("victory_points_yesterday", 0)
                kills_yesterday = stats.get("kills_yesterday", 0)
            else:
                pilots = getattr(stats, "pilots", 0)
                systems_controlled = getattr(stats, "systems_controlled", 0)
                victory_points_yesterday = getattr(stats, "victory_points_yesterday", 0)
                kills_yesterday = getattr(stats, "kills_yesterday", 0)
            
            self.html_output.append(f'<li class="list-group-item">Pilots: {pilots}</li>')
            self.html_output.append(f'<li class="list-group-item">Systems Controlled: {systems_controlled}</li>')
            self.html_output.append(f'<li class="list-group-item">Victory Points (yesterday): {victory_points_yesterday}</li>')
            self.html_output.append(f'<li class="list-group-item">Kills (yesterday): {kills_yesterday}</li>')
            self.html_output.append('</ul>')
            
            self.html_output.append('</div>')
            self.html_output.append('</div>')
            self.html_output.append('</div>')
        
        self.html_output.append('</div>')  # End row
        self.html_output.append('</div>')  # End card-body
        self.html_output.append('</div>')  # End card
    
    def display_systems_table(self, systems: List[Dict[str, Any]], sort_by: str = "name") -> None:
        """
        Display a table of faction warfare systems.
        
        Args:
            systems (List[Dict[str, Any]]): The systems to display.
            sort_by (str, optional): The field to sort by. Defaults to "name".
        """
        self.html_output.append('<div class="card mb-4">')
        self.html_output.append('<div class="card-header bg-primary text-white">')
        self.html_output.append('<h3>Faction Warfare Systems</h3>')
        self.html_output.append('</div>')
        self.html_output.append('<div class="card-body">')
        
        # Sort systems by the specified field
        if sort_by == "name":
            sorted_systems = sorted(systems, key=lambda s: s["system_info"]["name"])
        elif sort_by == "security":
            sorted_systems = sorted(systems, key=lambda s: s["system_info"]["security_status"])
        elif sort_by == "contest":
            sorted_systems = sorted(systems, key=lambda s: s["system"]["contest_percent"], reverse=True)
        elif sort_by == "region":
            sorted_systems = sorted(systems, key=lambda s: (s["system_info"]["region_name"], s["system_info"]["name"]))
        else:
            sorted_systems = systems
        
        # Create table
        self.html_output.append('<div class="table-responsive">')
        self.html_output.append('<table class="table table-striped table-hover">')
        self.html_output.append('<thead class="thead-dark">')
        self.html_output.append('<tr>')
        self.html_output.append('<th>System</th>')
        self.html_output.append('<th>Security</th>')
        self.html_output.append('<th>Region</th>')
        self.html_output.append('<th>Owner</th>')
        self.html_output.append('<th>Occupier</th>')
        self.html_output.append('<th>Contest %</th>')
        self.html_output.append('<th>Adjacency</th>')
        self.html_output.append('<th>Status</th>')
        self.html_output.append('</tr>')
        self.html_output.append('</thead>')
        self.html_output.append('<tbody>')
        
        for system in sorted_systems:
            system_data = system["system"]
            system_info = system["system_info"]
            
            # Get faction colors
            owner_faction_id = system_data["owner_faction_id"]
            owner_color = self.faction_colors.get(owner_faction_id, "#FFFFFF")
            owner_name = system["owner_faction_name"]
            
            occupier_faction_id = system_data["occupier_faction_id"]
            occupier_color = self.faction_colors.get(occupier_faction_id, "#FFFFFF")
            occupier_name = system["occupier_faction_name"]
            
            # Get adjacency color
            adjacency = system_data["adjacency"]
            adjacency_color = self.adjacency_colors.get(adjacency, "#FFFFFF")
            
            # Format contest percentage
            contest_percent = system_data["contest_percent"]
            if contest_percent > 75:
                contest_color = "#FF6347"  # Tomato
            elif contest_percent > 50:
                contest_color = "#FFD700"  # Gold
            elif contest_percent > 25:
                contest_color = "#32CD32"  # Lime Green
            else:
                contest_color = "#FFFFFF"  # White
            
            # Format security status
            security = system_info["security_status"]
            if security >= 0.5:
                security_color = "#32CD32"  # Lime Green
            elif security >= 0.1:
                security_color = "#FFD700"  # Gold
            else:
                security_color = "#FF6347"  # Tomato
            
            # Add row to table
            self.html_output.append('<tr>')
            self.html_output.append(f'<td><a href="#" class="system-link" data-system="{html.escape(system_info["name"])}">{html.escape(system_info["name"])}</a></td>')
            self.html_output.append(f'<td><span style="color: {security_color}">{security:.2f}</span></td>')
            self.html_output.append(f'<td>{html.escape(system_info["region_name"])}</td>')
            self.html_output.append(f'<td><span style="color: {owner_color}">{html.escape(owner_name)}</span></td>')
            self.html_output.append(f'<td><span style="color: {occupier_color}">{html.escape(occupier_name)}</span></td>')
            self.html_output.append(f'<td><span style="color: {contest_color}">{contest_percent:.1f}%</span></td>')
            
            # Adjacency with badge
            badge_color = "primary"
            if adjacency == SystemAdjacency.FRONTLINE:
                badge_color = "danger"
            elif adjacency == SystemAdjacency.COMMAND_OPERATIONS:
                badge_color = "warning"
            elif adjacency == SystemAdjacency.REARGUARD:
                badge_color = "success"
            
            self.html_output.append(f'<td><span class="badge bg-{badge_color}">{adjacency}</span></td>')
            
            # Status with badge
            status_color = "success" if system_data["contested"] == SystemStatus.UNCONTESTED else "danger"
            self.html_output.append(f'<td><span class="badge bg-{status_color}">{system_data["contested"]}</span></td>')
            
            self.html_output.append('</tr>')
        
        self.html_output.append('</tbody>')
        self.html_output.append('</table>')
        self.html_output.append('</div>')  # End table-responsive
        
        self.html_output.append('</div>')  # End card-body
        self.html_output.append('</div>')  # End card
    
    def display_system_details(self, system: Dict[str, Any]) -> None:
        """
        Display detailed information about a faction warfare system.
        
        Args:
            system (Dict[str, Any]): The system details to display.
        """
        system_data = system["system"]
        system_info = system["system_info"]
        
        self.html_output.append('<div class="card mb-4">')
        self.html_output.append('<div class="card-header bg-primary text-white">')
        self.html_output.append(f'<h3>System Details: {html.escape(system_info["name"].upper())}</h3>')
        self.html_output.append('</div>')
        self.html_output.append('<div class="card-body">')
        
        # Basic system information
        self.html_output.append(f'<h4>{html.escape(system_info["name"])} <small class="text-muted">({html.escape(system_info["region_name"])})</small></h4>')
        
        security = system_info['security_status']
        if security >= 0.5:
            security_color = "#32CD32"  # Lime Green
        elif security >= 0.1:
            security_color = "#FFD700"  # Gold
        else:
            security_color = "#FF6347"  # Tomato
        
        self.html_output.append(f'<p>Security: <span style="color: {security_color}">{security:.2f}</span> ({system_info["security_class"]})</p>')
        
        # Faction information
        owner_faction_id = system_data["owner_faction_id"]
        owner_color = self.faction_colors.get(owner_faction_id, "#FFFFFF")
        owner_name = system["owner_faction_name"]
        
        occupier_faction_id = system_data["occupier_faction_id"]
        occupier_color = self.faction_colors.get(occupier_faction_id, "#FFFFFF")
        occupier_name = system["occupier_faction_name"]
        
        self.html_output.append(f'<p>Owner Faction: <span style="color: {owner_color}">{html.escape(owner_name)}</span></p>')
        self.html_output.append(f'<p>Occupier Faction: <span style="color: {occupier_color}">{html.escape(occupier_name)}</span></p>')
        
        # Contest information
        contest_status = system_data["contested"]
        status_color = "danger" if contest_status == SystemStatus.CONTESTED else "success"
        
        self.html_output.append(f'<p>Contested Status: <span class="badge bg-{status_color}">{contest_status}</span></p>')
        
        # Victory points
        vp = system_data["victory_points"]
        vp_threshold = system_data["victory_points_threshold"]
        contest_percent = system_data["contest_percent"]
        
        if contest_percent > 75:
            contest_color = "#FF6347"  # Tomato
        elif contest_percent > 50:
            contest_color = "#FFD700"  # Gold
        elif contest_percent > 25:
            contest_color = "#32CD32"  # Lime Green
        else:
            contest_color = "#FFFFFF"  # White
        
        self.html_output.append(f'<p>Victory Points: {vp}/{vp_threshold} (<span style="color: {contest_color}">{contest_percent:.1f}%</span>)</p>')
        
        # Add progress bar for victory points
        self.html_output.append('<div class="progress mb-3">')
        self.html_output.append(f'<div class="progress-bar" role="progressbar" style="width: {contest_percent}%; background-color: {contest_color};" aria-valuenow="{contest_percent}" aria-valuemin="0" aria-valuemax="100">{contest_percent:.1f}%</div>')
        self.html_output.append('</div>')
        
        # Adjacency information
        adjacency = system_data["adjacency"]
        badge_color = "primary"
        if adjacency == SystemAdjacency.FRONTLINE:
            badge_color = "danger"
        elif adjacency == SystemAdjacency.COMMAND_OPERATIONS:
            badge_color = "warning"
        elif adjacency == SystemAdjacency.REARGUARD:
            badge_color = "success"
        
        self.html_output.append(f'<p>Adjacency Type: <span class="badge bg-{badge_color}">{adjacency}</span></p>')
        
        # Explain what the adjacency type means
        if adjacency == SystemAdjacency.FRONTLINE:
            self.html_output.append('<p><small class="text-muted">Frontline systems allow the fastest contestation rate</small></p>')
        elif adjacency == SystemAdjacency.COMMAND_OPERATIONS:
            self.html_output.append('<p><small class="text-muted">Command Operations systems have a medium contestation rate</small></p>')
        elif adjacency == SystemAdjacency.REARGUARD:
            self.html_output.append('<p><small class="text-muted">Rearguard systems have the slowest contestation rate</small></p>')
        
        self.html_output.append('</div>')  # End card-body
        self.html_output.append('</div>')  # End card
    
    def generate_graph_data(self, warzone_systems: List[Dict[str, Any]], solar_systems: List[Dict[str, Any]], filter_type: str = "all") -> Dict[str, Any]:
        """
        Generate graph data for visualization.
        
        Args:
            warzone_systems (List[Dict[str, Any]]): The systems in the warzone.
            solar_systems (List[Dict[str, Any]]): The solar systems data from the pickle file.
                This can be either a dictionary (old format) or a list of dictionaries (new format).
            filter_type (str, optional): The type of filter to apply. Defaults to "all".
                Options: "all", "frontline", "contested"
        
        Returns:
            Dict[str, Any]: The graph data for visualization.
        """
        nodes = []
        edges = []
        
        # Check if solar_systems is a dictionary (old format) or a list (new format)
        is_dict_format = isinstance(solar_systems, dict)
        
        # Create a mapping of system IDs to warzone system data
        system_map = {}
        for system in warzone_systems:
            system_id = str(system["system"]["solar_system_id"])
            system_map[system_id] = system
        
        # Create a mapping of system IDs to solar system data
        solar_system_map = {}
        if is_dict_format:
            # Old format: solar_systems is already a dictionary
            solar_system_map = solar_systems
        else:
            # New format: solar_systems is a list of dictionaries
            for system in solar_systems:
                system_id = str(system.get("system_id", ""))
                if system_id:
                    solar_system_map[system_id] = system
        
        # Process each system in the warzone
        for system in warzone_systems:
            system_data = system["system"]
            system_info = system["system_info"]
            system_id = str(system_data["solar_system_id"])
            
            # Apply filters
            if filter_type == "frontline" and system_data["adjacency"] != SystemAdjacency.FRONTLINE:
                continue
            if filter_type == "contested" and system_data["contested"] != SystemStatus.CONTESTED:
                continue
            
            # Get faction color
            owner_faction_id = system_data["owner_faction_id"]
            owner_color = self.faction_colors.get(owner_faction_id, "#FFFFFF")
            
            # Determine node shape based on adjacency
            node_shape = "diamond"  # Default for rearguard
            if system_data["adjacency"] == SystemAdjacency.FRONTLINE:
                node_shape = "square"
            elif system_data["adjacency"] == SystemAdjacency.COMMAND_OPERATIONS:
                node_shape = "ellipse"
            
            # Create node
            node = {
                "data": {
                    "id": system_id,
                    "label": system_info["name"],
                    "faction": owner_faction_id,
                    "faction_name": self.faction_names.get(owner_faction_id, f"Faction {owner_faction_id}"),
                    "adjacency": system_data["adjacency"],
                    "contested": system_data["contested"],
                    "contest_percent": system_data["contest_percent"],
                    "region": system_info["region_name"],
                    "security": system_info["security_status"]
                },
                "style": {
                    "background-color": owner_color,
                    "shape": node_shape,
                    "width": 30,
                    "height": 30,
                    "border-width": 2,
                    "border-color": "#000",
                    "label": system_info["name"]
                }
            }
            
            # Add highlight for contested systems
            if system_data["contested"] == SystemStatus.CONTESTED:
                node["style"]["border-width"] = 4
                node["style"]["border-color"] = "#FF0000"
            
            nodes.append(node)
        
        # Create edges for all system connections from the solar systems data
        processed_edges = set()  # Track processed edges to avoid duplicates
        
        for system_id, system in system_map.items():
            # Get the adjacent systems
            adjacent_systems = []
            
            # Get adjacent systems from the solar_system_map
            if system_id in solar_system_map:
                if is_dict_format:
                    # Old format: adjacent is a list of system IDs
                    adjacent_systems = solar_system_map[system_id].get("adjacent", [])
                else:
                    # New format: adjacent is a list of system IDs
                    adjacent_systems = solar_system_map[system_id].get("adjacent", [])
            
            # Create edges for each adjacent system
            for adjacent_id in adjacent_systems:
                # Convert adjacent_id to string if it's an integer (new format)
                if isinstance(adjacent_id, int):
                    adjacent_id = str(adjacent_id)
                
                # Skip if the adjacent system is not in the warzone or filtered out
                if adjacent_id not in system_map:
                    continue
                
                # Create a unique edge ID (sort IDs to avoid duplicates)
                edge_pair = tuple(sorted([system_id, adjacent_id]))
                if edge_pair in processed_edges:
                    continue  # Skip if we've already processed this edge
                
                processed_edges.add(edge_pair)
                
                # Get system data for both systems
                source_system = system_map[system_id]["system"]
                target_system = system_map[adjacent_id]["system"]
                
                # Determine if this is a frontline connection
                is_frontline = (
                    source_system["adjacency"] == SystemAdjacency.FRONTLINE and 
                    target_system["adjacency"] == SystemAdjacency.FRONTLINE and
                    source_system["owner_faction_id"] != target_system["owner_faction_id"]
                )
                
                edge = {
                    "data": {
                        "id": f"{system_id}-{adjacent_id}",
                        "source": system_id,
                        "target": adjacent_id,
                        "is_frontline": is_frontline
                    },
                    "style": {
                        "width": 3 if is_frontline else 1,
                        "line-color": "#FF0000" if is_frontline else "#999999",
                        "line-style": "solid" if is_frontline else "solid"
                    }
                }
                
                edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
