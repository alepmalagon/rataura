"""
Faction Warfare analyzer service.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set

from eve_wiggin.api.esi_client import get_esi_client
from eve_wiggin.models.faction_warfare import (
    FWSystem, FWFactionStats, FWWarzone, FWWarzoneStatus,
    FactionID, Warzone, SystemStatus, SystemAdjacency
)

# Configure logging
logger = logging.getLogger(__name__)


class FWAnalyzer:
    """
    Service for analyzing faction warfare data.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the faction warfare analyzer.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.esi_client = get_esi_client(access_token)
        
        # Define faction names
        self.faction_names = {
            FactionID.CALDARI_STATE: "Caldari State",
            FactionID.MINMATAR_REPUBLIC: "Minmatar Republic",
            FactionID.AMARR_EMPIRE: "Amarr Empire",
            FactionID.GALLENTE_FEDERATION: "Gallente Federation",
            FactionID.GURISTAS_PIRATES: "Guristas Pirates",
            FactionID.ANGEL_CARTEL: "Angel Cartel"
        }
        
        # Define warzone factions
        self.warzone_factions = {
            Warzone.CALDARI_GALLENTE: [FactionID.CALDARI_STATE, FactionID.GALLENTE_FEDERATION],
            Warzone.AMARR_MINMATAR: [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC]
        }
    
    async def get_fw_systems(self) -> List[FWSystem]:
        """
        Get and process faction warfare systems.
        
        Returns:
            List[FWSystem]: A list of processed faction warfare systems.
        """
        try:
            # Get faction warfare systems from ESI
            raw_systems = await self.esi_client.get_fw_systems()
            
            # Process systems
            systems = []
            for raw_system in raw_systems:
                # Calculate contest percentage
                victory_points = raw_system["victory_points"]
                victory_points_threshold = raw_system["victory_points_threshold"]
                contest_percent = 0.0
                if victory_points_threshold > 0:
                    contest_percent = (victory_points / victory_points_threshold) * 100
                
                # Determine warzone
                owner_faction_id = raw_system["owner_faction_id"]
                warzone = None
                if owner_faction_id in [FactionID.CALDARI_STATE, FactionID.GALLENTE_FEDERATION]:
                    warzone = Warzone.CALDARI_GALLENTE
                elif owner_faction_id in [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC]:
                    warzone = Warzone.AMARR_MINMATAR
                
                # Create system model
                system = FWSystem(
                    solar_system_id=raw_system["solar_system_id"],
                    owner_faction_id=owner_faction_id,
                    occupier_faction_id=raw_system["occupier_faction_id"],
                    contested=raw_system["contested"],
                    victory_points=victory_points,
                    victory_points_threshold=victory_points_threshold,
                    advantage=raw_system.get("advantage", 0.0),
                    contest_percent=contest_percent,
                    warzone=warzone
                )
                
                systems.append(system)
            
            # Determine system adjacency
            systems = await self.determine_system_adjacency(systems)
            
            return systems
        except Exception as e:
            logger.error(f"Error getting faction warfare systems: {e}", exc_info=True)
            raise
    
    async def determine_system_adjacency(self, systems: List[FWSystem]) -> List[FWSystem]:
        """
        Determine the adjacency type for each faction warfare system.
        
        Args:
            systems (List[FWSystem]): The list of faction warfare systems.
        
        Returns:
            List[FWSystem]: The updated list of faction warfare systems with adjacency information.
        """
        # Group systems by warzone and faction
        amarr_systems = []
        minmatar_systems = []
        caldari_systems = []
        gallente_systems = []
        
        for system in systems:
            if system.owner_faction_id == FactionID.AMARR_EMPIRE:
                amarr_systems.append(system)
            elif system.owner_faction_id == FactionID.MINMATAR_REPUBLIC:
                minmatar_systems.append(system)
            elif system.owner_faction_id == FactionID.CALDARI_STATE:
                caldari_systems.append(system)
            elif system.owner_faction_id == FactionID.GALLENTE_FEDERATION:
                gallente_systems.append(system)
        
        # In EVE Online, the adjacency type is determined by the ESI API
        # Frontline systems: Systems where the contest can move fastest
        # Command Operations: Systems where the contest moves at medium speed
        # Rearguard: Systems where the contest moves very slowly
        
        # For now, we'll use a simplified approach based on the ESI data
        # In a real implementation, we would use the actual adjacency data from ESI
        # or calculate it based on stargate connections and system positions
        
        for system in systems:
            # For demonstration purposes, we'll use a heuristic based on victory points
            # and contested status to estimate the adjacency type
            
            # Systems with high contest percentage are likely frontlines
            if system.contest_percent > 50.0:
                system.adjacency = SystemAdjacency.FRONTLINE
            # Systems with medium contest percentage are likely command operations
            elif system.contest_percent > 20.0:
                system.adjacency = SystemAdjacency.COMMAND_OPERATIONS
            # All other systems are rearguards
            else:
                system.adjacency = SystemAdjacency.REARGUARD
            
            # Note: In a production implementation, we would use the actual
            # adjacency data from the ESI API or calculate it based on the
            # system's position relative to enemy territory
        
        return systems
    
    async def get_fw_faction_stats(self) -> Dict[int, FWFactionStats]:
        """
        Get and process faction warfare statistics.
        
        Returns:
            Dict[int, FWFactionStats]: A dictionary of faction statistics by faction ID.
        """
        try:
            # Get faction warfare statistics from ESI
            raw_stats = await self.esi_client.get_fw_stats()
            
            # Process statistics
            faction_stats = {}
            for raw_stat in raw_stats:
                faction_id = raw_stat["faction_id"]
                
                # Create faction stats model
                stats = FWFactionStats(
                    faction_id=faction_id,
                    pilots=raw_stat["pilots"],
                    systems_controlled=raw_stat["systems_controlled"],
                    kills_yesterday=raw_stat["kills"]["yesterday"],
                    kills_last_week=raw_stat["kills"]["last_week"],
                    kills_total=raw_stat["kills"]["total"],
                    victory_points_yesterday=raw_stat["victory_points"]["yesterday"],
                    victory_points_last_week=raw_stat["victory_points"]["last_week"],
                    victory_points_total=raw_stat["victory_points"]["total"]
                )
                
                faction_stats[faction_id] = stats
            
            return faction_stats
        except Exception as e:
            logger.error(f"Error getting faction warfare statistics: {e}", exc_info=True)
            raise
    
    async def get_warzone_status(self) -> FWWarzoneStatus:
        """
        Get the status of all faction warfare warzones.
        
        Returns:
            FWWarzoneStatus: The status of all faction warfare warzones.
        """
        try:
            # Get faction warfare systems and statistics
            systems = await self.get_fw_systems()
            faction_stats = await self.get_fw_faction_stats()
            
            # Initialize warzones
            warzones = {
                Warzone.CALDARI_GALLENTE: FWWarzone(
                    name="Caldari-Gallente Warzone",
                    factions=[FactionID.CALDARI_STATE, FactionID.GALLENTE_FEDERATION],
                    systems={FactionID.CALDARI_STATE: 0, FactionID.GALLENTE_FEDERATION: 0},
                    contested={FactionID.CALDARI_STATE: 0, FactionID.GALLENTE_FEDERATION: 0}
                ),
                Warzone.AMARR_MINMATAR: FWWarzone(
                    name="Amarr-Minmatar Warzone",
                    factions=[FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC],
                    systems={FactionID.AMARR_EMPIRE: 0, FactionID.MINMATAR_REPUBLIC: 0},
                    contested={FactionID.AMARR_EMPIRE: 0, FactionID.MINMATAR_REPUBLIC: 0}
                )
            }
            
            # Count systems controlled by each faction
            for system in systems:
                owner_faction_id = system.owner_faction_id
                occupier_faction_id = system.occupier_faction_id
                contested = system.contested != SystemStatus.UNCONTESTED
                warzone_key = system.warzone
                
                if warzone_key and warzone_key in warzones:
                    # Count systems by owner
                    if owner_faction_id in warzones[warzone_key].systems:
                        warzones[warzone_key].systems[owner_faction_id] += 1
                    
                    # Count contested systems by occupier
                    if contested and occupier_faction_id in warzones[warzone_key].contested:
                        warzones[warzone_key].contested[occupier_faction_id] += 1
            
            # Calculate total systems and control percentages for each warzone
            for warzone_key, warzone in warzones.items():
                total_systems = sum(warzone.systems.values())
                warzone.total_systems = total_systems
                
                if total_systems > 0:
                    for faction_id, count in warzone.systems.items():
                        warzone.control_percentages[faction_id] = (count / total_systems) * 100
            
            # Create warzone status
            warzone_status = FWWarzoneStatus(
                warzones=warzones,
                faction_stats=faction_stats,
                timestamp=datetime.utcnow().isoformat()
            )
            
            return warzone_status
        except Exception as e:
            logger.error(f"Error getting warzone status: {e}", exc_info=True)
            raise
    
    async def get_system_details(self, system_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a faction warfare system.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Dict[str, Any]: Detailed information about the system.
        """
        try:
            # Get faction warfare systems
            systems = await self.get_fw_systems()
            
            # Find the system in the list
            fw_system = None
            for system in systems:
                if system.solar_system_id == system_id:
                    fw_system = system
                    break
            
            if not fw_system:
                raise ValueError(f"System with ID {system_id} is not part of faction warfare")
            
            # Get system details from ESI
            system_info = await self.esi_client.get_system(system_id)
            
            # Set system name
            fw_system.solar_system_name = system_info.get("name", f"System ID {system_id}")
            
            # Get constellation and region info
            constellation_id = system_info.get("constellation_id")
            region_name = None
            constellation_name = None
            
            if constellation_id:
                try:
                    constellation_info = await self.esi_client.get_constellation(constellation_id)
                    constellation_name = constellation_info.get("name")
                    
                    region_id = constellation_info.get("region_id")
                    if region_id:
                        region_info = await self.esi_client.get_region(region_id)
                        region_name = region_info.get("name")
                except Exception as e:
                    logger.error(f"Error getting constellation/region info: {e}")
            
            # Create result dictionary
            result = {
                "system": fw_system.dict(),
                "system_info": {
                    "name": fw_system.solar_system_name,
                    "security_status": system_info.get("security_status"),
                    "security_class": system_info.get("security_class"),
                    "constellation_id": constellation_id,
                    "constellation_name": constellation_name,
                    "region_name": region_name
                },
                "owner_faction_name": self.faction_names.get(fw_system.owner_faction_id),
                "occupier_faction_name": self.faction_names.get(fw_system.occupier_faction_id)
            }
            
            return result
        except Exception as e:
            logger.error(f"Error getting system details: {e}", exc_info=True)
            raise
