"""
Console-based visualization for EVE Wiggin.
"""

import logging
from typing import Dict, List, Any, Optional
from tabulate import tabulate
import colorama
from colorama import Fore, Back, Style

from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency, SystemStatus

# Initialize colorama
colorama.init(autoreset=True)

# Configure logging
logger = logging.getLogger(__name__)


class ConsoleVisualizer:
    """
    Console-based visualizer for faction warfare data.
    """
    
    def __init__(self):
        """
        Initialize the console visualizer.
        """
        # Define faction colors
        self.faction_colors = {
            FactionID.AMARR_EMPIRE: Fore.YELLOW,
            FactionID.MINMATAR_REPUBLIC: Fore.RED,
            FactionID.CALDARI_STATE: Fore.BLUE,
            FactionID.GALLENTE_FEDERATION: Fore.GREEN,
        }
        
        # Define adjacency colors
        self.adjacency_colors = {
            SystemAdjacency.FRONTLINE: Back.RED,
            SystemAdjacency.COMMAND_OPERATIONS: Back.YELLOW,
            SystemAdjacency.REARGUARD: Back.GREEN,
        }
        
        # Define faction names
        self.faction_names = {
            FactionID.AMARR_EMPIRE: "Amarr Empire",
            FactionID.MINMATAR_REPUBLIC: "Minmatar Republic",
            FactionID.CALDARI_STATE: "Caldari State",
            FactionID.GALLENTE_FEDERATION: "Gallente Federation",
        }
    
    def display_warzone_summary(self, warzone_data: Dict[str, Any]) -> None:
        """
        Display a summary of the warzone status.
        
        Args:
            warzone_data (Dict[str, Any]): The warzone data to display.
        """
        print(f"\n{Style.BRIGHT}{Fore.CYAN}=== WARZONE SUMMARY ===")
        print(f"{Fore.CYAN}Name: {warzone_data['name']}")
        print(f"{Fore.CYAN}Total Systems: {warzone_data['total_systems']}")
        
        # Display systems controlled by each faction
        for faction_id, count in warzone_data['systems'].items():
            faction_id_int = int(faction_id)
            percentage = warzone_data['control_percentages'].get(faction_id_int, 0)
            faction_color = self.faction_colors.get(faction_id_int, Fore.WHITE)
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            print(f"{faction_color}{faction_name}: {count} systems ({percentage:.1f}%)")
        
        # Display contested systems
        print(f"\n{Fore.CYAN}Contested Systems:")
        for faction_id, count in warzone_data['contested'].items():
            faction_id_int = int(faction_id)
            faction_color = self.faction_colors.get(faction_id_int, Fore.WHITE)
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            print(f"{faction_color}Contested by {faction_name}: {count} systems")
    
    def display_faction_stats(self, faction_stats: Dict[str, Any]) -> None:
        """
        Display faction warfare statistics.
        
        Args:
            faction_stats (Dict[str, Any]): The faction statistics to display.
        """
        print(f"\n{Style.BRIGHT}{Fore.CYAN}=== FACTION STATISTICS ===")
        
        for faction_id, stats in faction_stats.items():
            faction_id_int = int(faction_id)
            faction_color = self.faction_colors.get(faction_id_int, Fore.WHITE)
            faction_name = self.faction_names.get(faction_id_int, f"Faction {faction_id}")
            
            print(f"\n{faction_color}{faction_name}:")
            print(f"{faction_color}  Pilots: {stats.get('pilots', 0)}")
            print(f"{faction_color}  Systems Controlled: {stats.get('systems_controlled', 0)}")
            print(f"{faction_color}  Victory Points (yesterday): {stats.get('victory_points_yesterday', 0)}")
            print(f"{faction_color}  Kills (yesterday): {stats.get('kills_yesterday', 0)}")
    
    def display_systems_table(self, systems: List[Dict[str, Any]], sort_by: str = "name") -> None:
        """
        Display a table of faction warfare systems.
        
        Args:
            systems (List[Dict[str, Any]]): The systems to display.
            sort_by (str, optional): The field to sort by. Defaults to "name".
        """
        print(f"\n{Style.BRIGHT}{Fore.CYAN}=== FACTION WARFARE SYSTEMS ===")
        
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
        
        # Prepare table data
        table_data = []
        for system in sorted_systems:
            system_data = system["system"]
            system_info = system["system_info"]
            
            # Get faction colors
            owner_faction_id = system_data["owner_faction_id"]
            owner_color = self.faction_colors.get(owner_faction_id, Fore.WHITE)
            owner_name = system["owner_faction_name"]
            
            occupier_faction_id = system_data["occupier_faction_id"]
            occupier_color = self.faction_colors.get(occupier_faction_id, Fore.WHITE)
            occupier_name = system["occupier_faction_name"]
            
            # Get adjacency color
            adjacency = system_data["adjacency"]
            adjacency_color = self.adjacency_colors.get(adjacency, "")
            
            # Format contest percentage
            contest_percent = system_data["contest_percent"]
            if contest_percent > 75:
                contest_color = Fore.RED
            elif contest_percent > 50:
                contest_color = Fore.YELLOW
            elif contest_percent > 25:
                contest_color = Fore.GREEN
            else:
                contest_color = Fore.WHITE
            
            # Format security status
            security = system_info["security_status"]
            if security >= 0.5:
                security_color = Fore.GREEN
            elif security >= 0.1:
                security_color = Fore.YELLOW
            else:
                security_color = Fore.RED
            
            # Add row to table
            table_data.append([
                f"{system_info['name']}",
                f"{security_color}{security:.2f}",
                f"{system_info['region_name']}",
                f"{owner_color}{owner_name}",
                f"{occupier_color}{occupier_name}",
                f"{contest_color}{contest_percent:.1f}%",
                f"{adjacency_color}{adjacency}",
                f"{system_data['contested']}"
            ])
        
        # Display table
        headers = ["System", "Security", "Region", "Owner", "Occupier", "Contest %", "Adjacency", "Status"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    def display_system_details(self, system: Dict[str, Any]) -> None:
        """
        Display detailed information about a faction warfare system.
        
        Args:
            system (Dict[str, Any]): The system details to display.
        """
        system_data = system["system"]
        system_info = system["system_info"]
        
        print(f"\n{Style.BRIGHT}{Fore.CYAN}=== SYSTEM DETAILS: {system_info['name'].upper()} ===")
        
        # Basic system information
        print(f"{Fore.CYAN}Name: {system_info['name']} ({system_info['region_name']})")
        
        security = system_info['security_status']
        if security >= 0.5:
            security_color = Fore.GREEN
        elif security >= 0.1:
            security_color = Fore.YELLOW
        else:
            security_color = Fore.RED
        
        print(f"{Fore.CYAN}Security: {security_color}{security:.2f} ({system_info['security_class']})")
        
        # Faction information
        owner_faction_id = system_data["owner_faction_id"]
        owner_color = self.faction_colors.get(owner_faction_id, Fore.WHITE)
        owner_name = system["owner_faction_name"]
        
        occupier_faction_id = system_data["occupier_faction_id"]
        occupier_color = self.faction_colors.get(occupier_faction_id, Fore.WHITE)
        occupier_name = system["occupier_faction_name"]
        
        print(f"{Fore.CYAN}Owner Faction: {owner_color}{owner_name}")
        print(f"{Fore.CYAN}Occupier Faction: {occupier_color}{occupier_name}")
        
        # Contest information
        contest_status = system_data["contested"]
        if contest_status == SystemStatus.CONTESTED:
            status_color = Fore.RED
        else:
            status_color = Fore.GREEN
        
        print(f"{Fore.CYAN}Contested Status: {status_color}{contest_status}")
        
        # Victory points
        vp = system_data["victory_points"]
        vp_threshold = system_data["victory_points_threshold"]
        contest_percent = system_data["contest_percent"]
        
        if contest_percent > 75:
            contest_color = Fore.RED
        elif contest_percent > 50:
            contest_color = Fore.YELLOW
        elif contest_percent > 25:
            contest_color = Fore.GREEN
        else:
            contest_color = Fore.WHITE
        
        print(f"{Fore.CYAN}Victory Points: {vp}/{vp_threshold} ({contest_color}{contest_percent:.1f}%)")
        
        # Adjacency information
        adjacency = system_data["adjacency"]
        adjacency_color = self.adjacency_colors.get(adjacency, "")
        
        print(f"{Fore.CYAN}Adjacency Type: {adjacency_color}{adjacency}")
        
        # Explain what the adjacency type means
        if adjacency == SystemAdjacency.FRONTLINE:
            print(f"{Fore.CYAN}  (Frontline systems allow the fastest contestation rate)")
        elif adjacency == SystemAdjacency.COMMAND_OPERATIONS:
            print(f"{Fore.CYAN}  (Command Operations systems have a medium contestation rate)")
        elif adjacency == SystemAdjacency.REARGUARD:
            print(f"{Fore.CYAN}  (Rearguard systems have the slowest contestation rate)")

