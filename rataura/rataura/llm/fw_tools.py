"""
Faction Warfare function tools for the Rataura application.
"""

import logging
from typing import Dict, Any, List, Optional
from rataura.esi.client import get_esi_client

# Configure logging
logger = logging.getLogger(__name__)

# Function definitions for the LLM
FW_FUNCTION_DEFINITIONS = [
    {
        "name": "get_fw_warzone_status",
        "description": "Get information about which side is winning in each faction warfare warzone based on system control",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_fw_system_info",
        "description": "Get detailed faction warfare information about a specific solar system",
        "parameters": {
            "type": "object",
            "properties": {
                "system_id": {
                    "type": "integer",
                    "description": "The ID of the solar system"
                },
                "system_name": {
                    "type": "string",
                    "description": "The name of the solar system (will be resolved to an ID)"
                }
            },
            "required": []
        }
    }
]

async def get_fw_warzone_status() -> Dict[str, Any]:
    """
    Get information about which side is winning in each faction warfare warzone based on system control.
    
    Returns:
        Dict[str, Any]: Information about the faction warfare warzones.
    """
    esi_client = get_esi_client()
    
    try:
        # Get faction warfare systems
        fw_systems = await esi_client.get_fw_systems()
        
        # Get faction warfare statistics
        fw_stats = await esi_client.get_fw_stats()
        
        # Get faction warfare wars
        fw_wars = await esi_client.get_fw_wars()
        
        # Define faction IDs and names
        faction_names = {
            500001: "Caldari State",
            500002: "Minmatar Republic",
            500003: "Amarr Empire",
            500004: "Gallente Federation",
            500010: "Guristas Pirates",
            500011: "Angel Cartel"
        }
        
        # Define warzones
        warzones = {
            "caldari_gallente": {
                "name": "Caldari-Gallente Warzone",
                "factions": [500001, 500004],
                "systems": {500001: 0, 500004: 0},
                "contested": {500001: 0, 500004: 0}
            },
            "amarr_minmatar": {
                "name": "Amarr-Minmatar Warzone",
                "factions": [500002, 500003],
                "systems": {500002: 0, 500003: 0},
                "contested": {500002: 0, 500003: 0}
            }
        }
        
        # Count systems controlled by each faction
        for system in fw_systems:
            owner_faction_id = system["owner_faction_id"]
            occupier_faction_id = system["occupier_faction_id"]
            contested = system["contested"] != "uncontested"
            
            # Caldari-Gallente Warzone
            if owner_faction_id in [500001, 500004]:
                warzones["caldari_gallente"]["systems"][owner_faction_id] += 1
                if contested:
                    warzones["caldari_gallente"]["contested"][occupier_faction_id] += 1
            
            # Amarr-Minmatar Warzone
            elif owner_faction_id in [500002, 500003]:
                warzones["amarr_minmatar"]["systems"][owner_faction_id] += 1
                if contested:
                    warzones["amarr_minmatar"]["contested"][occupier_faction_id] += 1
        
        # Create a formatted summary
        summary = "# Faction Warfare Warzone Status\n\n"
        
        # Caldari-Gallente Warzone
        caldari_systems = warzones["caldari_gallente"]["systems"][500001]
        gallente_systems = warzones["caldari_gallente"]["systems"][500004]
        total_caldari_gallente = caldari_systems + gallente_systems
        
        if total_caldari_gallente > 0:
            caldari_percentage = (caldari_systems / total_caldari_gallente) * 100
            gallente_percentage = (gallente_systems / total_caldari_gallente) * 100
            
            summary += "## Caldari-Gallente Warzone\n\n"
            summary += f"- **Caldari State**: {caldari_systems} systems ({caldari_percentage:.1f}%)\n"
            summary += f"- **Gallente Federation**: {gallente_systems} systems ({gallente_percentage:.1f}%)\n\n"
            
            if caldari_systems > gallente_systems:
                summary += f"**Current Winner**: Caldari State (controlling {caldari_percentage:.1f}% of the warzone)\n\n"
            elif gallente_systems > caldari_systems:
                summary += f"**Current Winner**: Gallente Federation (controlling {gallente_percentage:.1f}% of the warzone)\n\n"
            else:
                summary += "**Current Status**: Even control (50% each)\n\n"
            
            # Add contested systems info
            caldari_contested = warzones["caldari_gallente"]["contested"][500001]
            gallente_contested = warzones["caldari_gallente"]["contested"][500004]
            
            if caldari_contested > 0 or gallente_contested > 0:
                summary += "### Contested Systems\n\n"
                if caldari_contested > 0:
                    summary += f"- Caldari is contesting {caldari_contested} Gallente systems\n"
                if gallente_contested > 0:
                    summary += f"- Gallente is contesting {gallente_contested} Caldari systems\n\n"
        
        # Amarr-Minmatar Warzone
        amarr_systems = warzones["amarr_minmatar"]["systems"][500003]
        minmatar_systems = warzones["amarr_minmatar"]["systems"][500002]
        total_amarr_minmatar = amarr_systems + minmatar_systems
        
        if total_amarr_minmatar > 0:
            amarr_percentage = (amarr_systems / total_amarr_minmatar) * 100
            minmatar_percentage = (minmatar_systems / total_amarr_minmatar) * 100
            
            summary += "## Amarr-Minmatar Warzone\n\n"
            summary += f"- **Amarr Empire**: {amarr_systems} systems ({amarr_percentage:.1f}%)\n"
            summary += f"- **Minmatar Republic**: {minmatar_systems} systems ({minmatar_percentage:.1f}%)\n\n"
            
            if amarr_systems > minmatar_systems:
                summary += f"**Current Winner**: Amarr Empire (controlling {amarr_percentage:.1f}% of the warzone)\n\n"
            elif minmatar_systems > amarr_systems:
                summary += f"**Current Winner**: Minmatar Republic (controlling {minmatar_percentage:.1f}% of the warzone)\n\n"
            else:
                summary += "**Current Status**: Even control (50% each)\n\n"
            
            # Add contested systems info
            amarr_contested = warzones["amarr_minmatar"]["contested"][500003]
            minmatar_contested = warzones["amarr_minmatar"]["contested"][500002]
            
            if amarr_contested > 0 or minmatar_contested > 0:
                summary += "### Contested Systems\n\n"
                if amarr_contested > 0:
                    summary += f"- Amarr is contesting {amarr_contested} Minmatar systems\n"
                if minmatar_contested > 0:
                    summary += f"- Minmatar is contesting {minmatar_contested} Amarr systems\n\n"
        
        # Add faction statistics
        summary += "## Faction Statistics\n\n"
        
        for stat in fw_stats:
            faction_id = stat["faction_id"]
            if faction_id in faction_names:
                faction_name = faction_names[faction_id]
                pilots = stat["pilots"]
                systems = stat["systems_controlled"]
                kills_yesterday = stat["kills"]["yesterday"]
                kills_week = stat["kills"]["last_week"]
                
                summary += f"### {faction_name}\n\n"
                summary += f"- **Pilots**: {pilots:,}\n"
                summary += f"- **Systems Controlled**: {systems}\n"
                summary += f"- **Kills (Yesterday)**: {kills_yesterday:,}\n"
                summary += f"- **Kills (Last Week)**: {kills_week:,}\n\n"
        
        return {
            "warzones": warzones,
            "formatted_info": summary,
            "raw_data": {
                "systems": fw_systems,
                "stats": fw_stats,
                "wars": fw_wars
            }
        }
    except Exception as e:
        logger.error(f"Error getting faction warfare warzone status: {e}", exc_info=True)
        return {"error": f"Error getting faction warfare warzone status: {str(e)}"}

async def get_fw_system_info(system_id: Optional[int] = None, system_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get detailed faction warfare information about a specific solar system.
    
    Args:
        system_id (Optional[int], optional): The ID of the solar system.
        system_name (Optional[str], optional): The name of the solar system.
    
    Returns:
        Dict[str, Any]: Detailed information about the faction warfare system.
    """
    esi_client = get_esi_client()
    
    # Resolve system name to ID if provided
    if system_name and not system_id:
        search_result = await esi_client.search(system_name, ["solar_system"], strict=True)
        if "solar_system" in search_result and search_result["solar_system"]:
            system_id = search_result["solar_system"][0]
        else:
            return {"error": f"Solar system '{system_name}' not found"}
    
    if not system_id:
        return {"error": "No solar system ID or name provided"}
    
    try:
        # Get faction warfare systems
        fw_systems = await esi_client.get_fw_systems()
        
        # Find the system in the FW systems list
        fw_system = None
        for system in fw_systems:
            if system["solar_system_id"] == system_id:
                fw_system = system
                break
        
        if not fw_system:
            return {"error": f"Solar system with ID {system_id} is not part of faction warfare"}
        
        # Get system details
        system_info = await esi_client.get_system(system_id)
        
        # Define faction IDs and names
        faction_names = {
            500001: "Caldari State",
            500002: "Minmatar Republic",
            500003: "Amarr Empire",
            500004: "Gallente Federation",
            500010: "Guristas Pirates",
            500011: "Angel Cartel"
        }
        
        # Get system data
        owner_faction_id = fw_system["owner_faction_id"]
        occupier_faction_id = fw_system["occupier_faction_id"]
        victory_points = fw_system["victory_points"]
        victory_points_threshold = fw_system["victory_points_threshold"]
        contested_status = fw_system["contested"]
        
        # Determine if the system is being contested
        is_contested = contested_status != "uncontested"
        
        # Calculate contest percentage (related to the attacking faction)
        # Contest is always related to the attacking faction (occupier if different from owner)
        contest_percent = 0
        if victory_points_threshold > 0:
            contest_percent = (victory_points / victory_points_threshold) * 100
        
        # Get advantage percentage directly from the API
        advantage_percent = fw_system.get("advantage", 0)
        
        # Determine warzone
        if owner_faction_id in [500001, 500004]:
            warzone = "Caldari-Gallente"
        elif owner_faction_id in [500002, 500003]:
            warzone = "Amarr-Minmatar"
        else:
            warzone = "Unknown"
        
        # Create a formatted summary
        system_name = system_info.get("name", f"System ID {system_id}")
        owner_faction_name = faction_names.get(owner_faction_id, f"Faction ID {owner_faction_id}")
        occupier_faction_name = faction_names.get(occupier_faction_id, f"Faction ID {occupier_faction_id}")
        
        summary = f"# Faction Warfare System: {system_name}\n\n"
        summary += f"## Warzone: {warzone}\n\n"
        summary += f"- **Owner Faction**: {owner_faction_name}\n"
        
        # Determine the attacking faction
        attacking_faction = None
        if owner_faction_id != occupier_faction_id:
            attacking_faction = occupier_faction_name
            summary += f"- **Occupier/Attacking Faction**: {occupier_faction_name}\n"
        else:
            summary += f"- **Occupier Faction**: {occupier_faction_name} (same as owner)\n"
        
        summary += f"- **Contested Status**: {contested_status.capitalize()}\n"
        
        # Add contest information (related to the attacking faction)
        if is_contested and attacking_faction:
            summary += f"- **Contest Percentage**: {contest_percent:.2f}% (progress of {attacking_faction} towards capturing this system)\n"
        elif is_contested:
            summary += f"- **Contest Percentage**: {contest_percent:.2f}% (progress towards system capture)\n"
        
        # Add advantage information (separate from contest)
        summary += f"- **Advantage Percentage**: {advantage_percent:.2f}% (affects victory point gains)\n"
        summary += f"- **Victory Points**: {victory_points:,} / {victory_points_threshold:,}\n\n"
        
        # Add system security status
        security_status = system_info.get("security_status", 0)
        security_class = system_info.get("security_class", "Unknown")
        
        summary += "## System Information\n\n"
        summary += f"- **Security Status**: {security_status:.1f}\n"
        summary += f"- **Security Class**: {security_class}\n"
        
        # Add constellation and region info if available
        constellation_id = system_info.get("constellation_id")
        if constellation_id:
            try:
                constellation_info = await esi_client.get_constellation(constellation_id)
                constellation_name = constellation_info.get("name", f"Constellation ID {constellation_id}")
                
                region_id = constellation_info.get("region_id")
                if region_id:
                    region_info = await esi_client.get_region(region_id)
                    region_name = region_info.get("name", f"Region ID {region_id}")
                    
                    summary += f"- **Constellation**: {constellation_name}\n"
                    summary += f"- **Region**: {region_name}\n"
            except Exception as e:
                logger.error(f"Error getting constellation/region info: {e}")
        
        return {
            "system_id": system_id,
            "system_name": system_name,
            "owner_faction_id": owner_faction_id,
            "owner_faction_name": owner_faction_name,
            "occupier_faction_id": occupier_faction_id,
            "occupier_faction_name": occupier_faction_name,
            "contested": contested_status,
            "victory_points": victory_points,
            "victory_points_threshold": victory_points_threshold,
            "contest_percent": contest_percent,  # New field for contest percentage
            "advantage_percent": advantage_percent,  # Using advantage directly from API
            "warzone": warzone,
            "formatted_info": summary,
            "raw_data": {
                "fw_system": fw_system,
                "system_info": system_info
            }
        }
    except Exception as e:
        logger.error(f"Error getting faction warfare system info: {e}", exc_info=True)
        return {"error": f"Error getting faction warfare system info: {str(e)}"}
