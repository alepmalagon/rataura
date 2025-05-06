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
        
        # Define capture effort colors
        self.capture_effort_colors = {
            "Very Easy": "#32CD32",  # Lime Green
            "Easy": "#98FB98",  # Pale Green
            "Moderate": "#FFD700",  # Gold
            "Hard": "#FFA500",  # Orange
            "Very Hard": "#FF4500",  # Red-Orange
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
        
        # Create a row for both charts
        self.html_output.append('<div class="row">')
        
        # First column for Systems Control
        self.html_output.append('<div class="col-md-6 mb-3">')
        self.html_output.append('<h5>Systems Control</h5>')
        
        # Add canvas for systems control pie chart
        self.html_output.append('<div class="row">')
        self.html_output.append('<div class="col-md-12 mb-3">')
        self.html_output.append('<canvas id="systemsControlChart" width="400" height="300"></canvas>')
        self.html_output.append('</div>')
        
        # Add the data for the systems control chart as a data attribute
        systems_control_data = {}
        for faction_id, count in warzone_data['systems'].items():
            faction_id_int = int(faction_id)
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            systems_control_data[faction_name] = count
        
        self.html_output.append(f'<div id="systemsControlData" data-systems=\'{json.dumps(systems_control_data)}\' style="display: none;"></div>')
        
        # Add faction details in cards
        self.html_output.append('<div class="col-md-12">')
        for faction_id, count in warzone_data['systems'].items():
            faction_id_int = int(faction_id)
            percentage = warzone_data['control_percentages'].get(faction_id_int, 0)
            faction_color = self.faction_colors.get(faction_id_int, "#FFFFFF")
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            self.html_output.append(f'<div class="card mb-2" style="border-left: 5px solid {faction_color};">')
            self.html_output.append('<div class="card-body py-2">')
            self.html_output.append(f'<h6 class="card-title mb-0">{html.escape(faction_name)}: {count} systems ({percentage:.1f}%)</h6>')
            self.html_output.append('</div>')
            self.html_output.append('</div>')
        self.html_output.append('</div>')
        
        self.html_output.append('</div>')  # End row
        self.html_output.append('</div>')  # End first column
        
        # Second column for Contested Systems
        self.html_output.append('<div class="col-md-6 mb-3">')
        self.html_output.append('<h5>Contested Systems</h5>')
        
        # Add canvas for contested systems pie chart
        self.html_output.append('<div class="row">')
        self.html_output.append('<div class="col-md-12 mb-3">')
        self.html_output.append('<canvas id="contestedSystemsChart" width="400" height="300"></canvas>')
        self.html_output.append('</div>')
        
        # Calculate uncontested systems
        total_contested = sum(warzone_data['contested'].values())
        uncontested_systems = warzone_data['total_systems'] - total_contested
        
        # Add the data for the contested systems chart as a data attribute
        contested_systems_data = {}
        for faction_id, count in warzone_data['contested'].items():
            faction_id_int = int(faction_id)
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            contested_systems_data[faction_name] = count
        
        # Add uncontested systems to the data
        contested_systems_data["Uncontested"] = uncontested_systems
        
        self.html_output.append(f'<div id="contestedSystemsData" data-systems=\'{json.dumps(contested_systems_data)}\' style="display: none;"></div>')
        
        # Add faction details in cards
        self.html_output.append('<div class="col-md-12">')
        for faction_id, count in warzone_data['contested'].items():
            faction_id_int = int(faction_id)
            faction_color = self.faction_colors.get(faction_id_int, "#FFFFFF")
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            self.html_output.append(f'<div class="card mb-2" style="border-left: 5px solid {faction_color};">')
            self.html_output.append('<div class="card-body py-2">')
            self.html_output.append(f'<h6 class="card-title mb-0">Contested by {html.escape(faction_name)}: {count} systems</h6>')
            self.html_output.append('</div>')
            self.html_output.append('</div>')
        
        # Add uncontested systems card
        self.html_output.append(f'<div class="card mb-2" style="border-left: 5px solid #28a745;">')
        self.html_output.append('<div class="card-body py-2">')
        self.html_output.append(f'<h6 class="card-title mb-0">Uncontested: {uncontested_systems} systems</h6>')
        self.html_output.append('</div>')
        self.html_output.append('</div>')
        
        self.html_output.append('</div>')  # End col
        
        self.html_output.append('</div>')  # End row
        self.html_output.append('</div>')  # End second column
        
        self.html_output.append('</div>')  # End main row
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
        elif sort_by == "contest":
            sorted_systems = sorted(systems, key=lambda s: s["system"]["contest_percent"], reverse=True)
        elif sort_by == "region":
            sorted_systems = sorted(systems, key=lambda s: (s["system_info"]["region_name"] or "", s["system_info"]["name"]))
        else:
            sorted_systems = systems
        
        # Create table
        self.html_output.append('<div class="table-responsive">')
        self.html_output.append('<table class="table table-striped table-hover">')
        self.html_output.append('<thead class="thead-dark">')
        self.html_output.append('<tr>')
        self.html_output.append('<th>System</th>')
        self.html_output.append('<th>Region</th>')
        self.html_output.append('<th>Occupier</th>')
        self.html_output.append('<th>Adjacency</th>')
        self.html_output.append('<th>Progress</th>')
        self.html_output.append('<th>Victory Points</th>')
        self.html_output.append('<th>Amarr Adv.</th>')
        self.html_output.append('<th>Minmatar Adv.</th>')
        self.html_output.append('<th>Net Adv.</th>')
        self.html_output.append('</tr>')
        self.html_output.append('</thead>')
        self.html_output.append('<tbody>')
        
        # Group systems by region for better organization
        regions = {}
        for system in sorted_systems:
            region_name = system["system_info"]["region_name"] or "Unknown Region"
            if region_name not in regions:
                regions[region_name] = []
            regions[region_name].append(system)
        
        # Display systems by region
        for region_name, region_systems in regions.items():
            # Add region header
            self.html_output.append(f'<tr class="table-secondary"><td colspan="10"><strong>{html.escape(region_name)}</strong></td></tr>')
            
            # Add systems in this region
            for system in region_systems:
                system_data = system["system"]
                system_info = system["system_info"]
                
                # Get system name
                system_name = system_info["name"]
                
                # Get owner and occupier faction names
                owner_faction_id = system_data["owner_faction_id"]
                occupier_faction_id = system_data["occupier_faction_id"]
                owner_faction_name = system.get("owner_faction_name", f"Faction {owner_faction_id}")
                occupier_faction_name = system.get("occupier_faction_name", f"Faction {occupier_faction_id}")
                
                # Get owner and occupier faction colors
                owner_color = self.faction_colors.get(owner_faction_id, "#FFFFFF")
                occupier_color = self.faction_colors.get(occupier_faction_id, "#FFFFFF")
                
                # Get adjacency type and badge color
                adjacency = system_data["adjacency"]
                badge_color = self._get_adjacency_badge_color(adjacency)
                
                # Get contested status
                contested = system_data["contested"]
                contest_percent = system_data["contest_percent"]
                
                # Get victory points
                victory_points = system_data["victory_points"]
                victory_points_threshold = system_data["victory_points_threshold"]
                
                # Get advantage data
                amarr_advantage = system_data.get("amarr_advantage", 0.0)
                minmatar_advantage = system_data.get("minmatar_advantage", 0.0)
                net_advantage = system_data.get("net_advantage", 0.0)
                
                # Determine advantage color
                if net_advantage > 0.1:
                    advantage_color = "#FF4500"  # Red-Orange for Minmatar advantage
                elif net_advantage < -0.1:
                    advantage_color = "#FFD700"  # Gold for Amarr advantage
                else:
                    advantage_color = "#FFFFFF"  # White for neutral
                
                # Add system row
                self.html_output.append('<tr>')
                
                # System name
                self.html_output.append(f'<td><a href="#" class="system-link" data-system="{html.escape(system_name)}">{html.escape(system_name)}</a></td>')
                
                # Region
                self.html_output.append(f'<td>{html.escape(system_info["region_name"] or "")}</td>')
                
                # Occupier faction
                self.html_output.append(f'<td><span style="color: {occupier_color};">{html.escape(occupier_faction_name)}</span></td>')
                
                # Adjacency
                self.html_output.append(f'<td><span class="badge bg-{badge_color}">{adjacency}</span></td>')
                
                # Contested status
                if contested:
                    contest_color = "danger" if contest_percent > 50 else "warning"
                    self.html_output.append(f'<td><div class="progress" style="height: 20px;"><div class="progress-bar bg-{contest_color}" role="progressbar" style="width: {contest_percent}%;" aria-valuenow="{contest_percent}" aria-valuemin="0" aria-valuemax="100">{contest_percent:.1f}%</div></div></td>')
                else:
                    self.html_output.append('<td><span class="badge bg-success">Uncontested</span></td>')
                
                # Victory points
                self.html_output.append(f'<td>{victory_points}</td>')
            
                
                # Amarr advantage
                self.html_output.append(f'<td>{amarr_advantage:.2f}</td>')
                
                # Minmatar advantage
                self.html_output.append(f'<td>{minmatar_advantage:.2f}</td>')
                
                # Net advantage
                self.html_output.append(f'<td><span style="color: {advantage_color};">{net_advantage:.2f}</span></td>')
                
                self.html_output.append('</tr>')
        
        self.html_output.append('</tbody>')
        self.html_output.append('</table>')
        self.html_output.append('</div>')  # End table-responsive
        self.html_output.append('</div>')  # End card-body
        self.html_output.append('</div>')  # End card
    
    def _get_adjacency_badge_color(self, adjacency: str) -> str:
        """
        Get the badge color for an adjacency type.
        
        Args:
            adjacency (str): The adjacency type.
        
        Returns:
            str: The badge color.
        """
        if adjacency == SystemAdjacency.FRONTLINE:
            return "danger"
        elif adjacency == SystemAdjacency.COMMAND_OPERATIONS:
            return "warning"
        elif adjacency == SystemAdjacency.REARGUARD:
            return "success"
        else:
            return "secondary"
    
    def _get_contest_color(self, contest_percent: float) -> str:
        """
        Get the color for a contest percentage.
        
        Args:
            contest_percent (float): The contest percentage.
        
        Returns:
            str: The color.
        """
        if contest_percent > 75:
            return "#FF6347"  # Tomato
        elif contest_percent > 50:
            return "#FFD700"  # Gold
        elif contest_percent > 25:
            return "#32CD32"  # Lime Green
        else:
            return "#FFFFFF"  # White
    
    def display_system_details(self, system: Dict[str, Any]) -> None:
        """
        Display detailed information about a system.
        
        Args:
            system (Dict[str, Any]): The system data to display.
        """
        system_data = system["system"]
        system_info = system["system_info"]
        
        self.html_output.append('<div class="card mb-4">')
        self.html_output.append('<div class="card-header bg-primary text-white">')
        self.html_output.append(f'<h3>{html.escape(system_info["name"])}</h3>')
        self.html_output.append('</div>')
        self.html_output.append('<div class="card-body">')
        
        # System information
        self.html_output.append('<div class="row">')
        self.html_output.append('<div class="col-md-6">')
        
        # Basic system info
        self.html_output.append('<div class="card mb-3">')
        self.html_output.append('<div class="card-body">')
        self.html_output.append('<h5>System Information</h5>')
        self.html_output.append(f'<p>Region: {html.escape(system_info["region_name"])}</p>')
        self.html_output.append(f'<p>Constellation: {html.escape(system_info["constellation_name"])}</p>')
        
        # Owner and occupier
        owner_faction_id = system_data["owner_faction_id"]
        occupier_faction_id = system_data["occupier_faction_id"]
        owner_name = self.faction_names.get(owner_faction_id, f"Faction {owner_faction_id}")
        occupier_name = self.faction_names.get(occupier_faction_id, f"Faction {occupier_faction_id}")
        
        self.html_output.append(f'<p>Owner: {html.escape(owner_name)}</p>')
        self.html_output.append(f'<p>Occupier: {html.escape(occupier_name)}</p>')
        
        # Victory points
        victory_points = system_data["victory_points"]
        victory_points_threshold = system_data["victory_points_threshold"]
        contest_percent = system_data["contest_percent"]
        
        self.html_output.append('<h5>Victory Points</h5>')
        self.html_output.append(f'<p>{victory_points} / {victory_points_threshold} ({contest_percent:.1f}%)</p>')
        
        # Progress bar for victory points
        progress_color = "success"
        if contest_percent > 50:
            progress_color = "warning"
        if contest_percent > 75:
            progress_color = "danger"
        
        self.html_output.append('<div class="progress mb-3">')
        self.html_output.append(f'<div class="progress-bar bg-{progress_color}" role="progressbar" style="width: {contest_percent}%" aria-valuenow="{contest_percent}" aria-valuemin="0" aria-valuemax="100"></div>')
        self.html_output.append('</div>')
        
        # Advantage information
        amarr_advantage = system_data.get("amarr_advantage", 0.0)
        minmatar_advantage = system_data.get("minmatar_advantage", 0.0)
        net_advantage = system_data.get("net_advantage", 0.0)
        
        amarr_color = "#FFD700"  # Gold for Amarr
        minmatar_color = "#FF4500"  # Red-Orange for Minmatar
        
        # Determine net advantage color
        if net_advantage > 0.1:
            net_advantage_color = "#FF4500"  # Red-Orange for Minmatar advantage
        elif net_advantage < -0.1:
            net_advantage_color = "#FFD700"  # Gold for Amarr advantage
        else:
            net_advantage_color = "#FFFFFF"  # White for neutral
        
        self.html_output.append('<h5>Advantage</h5>')
        self.html_output.append('<div class="row">')
        
        # Amarr advantage
        self.html_output.append('<div class="col-md-4">')
        self.html_output.append(f'<p>Amarr: <span style="color: {amarr_color}">{amarr_advantage:.2f}</span></p>')
        self.html_output.append('</div>')
        
        # Minmatar advantage
        self.html_output.append('<div class="col-md-4">')
        self.html_output.append(f'<p>Minmatar: <span style="color: {minmatar_color}">{minmatar_advantage:.2f}</span></p>')
        self.html_output.append('</div>')
        
        # Net advantage
        self.html_output.append('<div class="col-md-4">')
        self.html_output.append(f'<p>Net: <span style="color: {net_advantage_color}">{net_advantage:.2f}</span></p>')
        self.html_output.append('</div>')
        
        self.html_output.append('</div>')  # End row
        
        # Adjacency information
        adjacency = system_data["adjacency"]
        badge_color = self._get_adjacency_badge_color(adjacency)
        
        self.html_output.append(f'<p>Adjacency Type: <span class="badge bg-{badge_color}">{adjacency}</span></p>')
        
        # Explain what the adjacency type means
        if adjacency == SystemAdjacency.FRONTLINE:
            self.html_output.append('<p><small class="text-muted">Frontline systems allow the fastest contestation rate</small></p>')
        elif adjacency == SystemAdjacency.COMMAND_OPERATIONS:
            self.html_output.append('<p><small class="text-muted">Command Operations systems have a medium contestation rate</small></p>')
        elif adjacency == SystemAdjacency.REARGUARD:
            self.html_output.append('<p><small class="text-muted">Rearguard systems have the slowest contestation rate</small></p>')
        
        # Capture Effort information (only for Amarr systems)
        if occupier_faction_id == 500003:  # Amarr Empire
            capture_effort = system_data.get("capture_effort", 0.0)
            capture_effort_category = system_data.get("capture_effort_category", "Unknown")
            
            # Get the color for the capture effort category
            category_color = self.capture_effort_colors.get(capture_effort_category, "#FFFFFF")
            
            self.html_output.append('<h5>Capture Effort (Minmatar)</h5>')
            self.html_output.append(f'<p>Effort: <span style="color: {category_color}">{capture_effort:.2f}</span></p>')
            self.html_output.append(f'<p>Category: <span style="color: {category_color}">{capture_effort_category}</span></p>')
            
            # Progress bar for capture effort
            self.html_output.append('<div class="progress mb-3">')
            
            # Determine progress bar color based on category
            progress_color = "success"  # Default green for Very Easy
            if capture_effort_category == "Easy":
                progress_color = "info"
            elif capture_effort_category == "Moderate":
                progress_color = "warning"
            elif capture_effort_category in ["Hard", "Very Hard"]:
                progress_color = "danger"
            
            self.html_output.append(f'<div class="progress-bar bg-{progress_color}" role="progressbar" style="width: {capture_effort}%" aria-valuenow="{capture_effort}" aria-valuemin="0" aria-valuemax="100"></div>')
            self.html_output.append('</div>')
            
            # Explain what the capture effort means
            self.html_output.append('<p><small class="text-muted">Capture Effort represents how difficult it would be for Minmatar forces to capture this Amarr system.</small></p>')
            self.html_output.append('<p><small class="text-muted">Factors: Distance from Vard, Faction Advantage, Victory Points, and Adjacency Type</small></p>')
        
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
                system_id = str(system.get("solar_system_id", ""))
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
            occupier_faction_id = system_data["occupier_faction_id"]
            owner_color = self.faction_colors.get(owner_faction_id, "#FFFFFF")
            occupier_color = self.faction_colors.get(occupier_faction_id, "#FFFFFF")
            
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
                    "owner_faction_id": owner_faction_id,
                    "owner_faction_name": self.faction_names.get(owner_faction_id, f"Faction {owner_faction_id}"),
                    "occupier_faction_id": occupier_faction_id,
                    "occupier_faction_name": self.faction_names.get(occupier_faction_id, f"Faction {occupier_faction_id}"),
                    "adjacency": system_data["adjacency"],
                    "contested": system_data["contested"],
                    "contest_percent": system_data["contest_percent"],
                    "amarr_advantage": system_data.get("amarr_advantage", 0.0),
                    "minmatar_advantage": system_data.get("minmatar_advantage", 0.0),
                    "net_advantage": system_data.get("net_advantage", 0.0),
                    "capture_effort": system_data.get("capture_effort", 0.0),
                    "capture_effort_category": system_data.get("capture_effort_category", "Unknown"),
                    "region_name": system_info["region_name"]
                },
                "style": {
                    "background-color": occupier_color,  # Use occupier color for node
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
                    source_system["occupier_faction_id"] != target_system["occupier_faction_id"]
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
