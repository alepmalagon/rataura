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
from eve_wiggin.services.adjacency_detector import get_adjacency_detector

# Configure logging
logger = logging.getLogger(__name__)

# Define permanent frontline systems
AMARR_PERMANENT_FRONTLINES = {
    "Amamake", "Bosboger", "Auner", "Resbroko", "Evati", "Arnstur"
}

MINMATAR_PERMANENT_FRONTLINES = {
    "Raa", "Kamela", "Sosala", "Huola", "Anka", "Iesa", "Uusanen", "Saikamon", "Halmah"
}

# System ID to name mapping (to be populated)
SYSTEM_ID_TO_NAME = {}
# System name to ID mapping (to be populated)
SYSTEM_NAME_TO_ID = {}
# System connections (adjacency graph)
SYSTEM_CONNECTIONS = {}


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
        self.adjacency_detector = get_adjacency_detector()
        
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
            
            # Get system names and build connections
            await self.build_system_connections(systems)
            
            # Determine system adjacency
            systems = await self.determine_system_adjacency(systems)
            
            return systems
        except Exception as e:
            logger.error(f"Error getting faction warfare systems: {e}", exc_info=True)
            raise
    
    async def build_system_connections(self, systems: List[FWSystem]) -> None:
        """
        Build a graph of system connections using stargate data.
        
        Args:
            systems (List[FWSystem]): The list of faction warfare systems.
        """
        global SYSTEM_ID_TO_NAME, SYSTEM_NAME_TO_ID, SYSTEM_CONNECTIONS
        
        # If connections are already built, skip
        if SYSTEM_CONNECTIONS:
            return
        
        logger.info("Building system connections graph...")
        
        # Get system names and IDs
        for system in systems:
            try:
                system_info = await self.esi_client.get_system(system.solar_system_id)
                system_name = system_info.get("name", f"System {system.solar_system_id}")
                system.solar_system_name = system_name
                
                SYSTEM_ID_TO_NAME[system.solar_system_id] = system_name
                SYSTEM_NAME_TO_ID[system_name] = system.solar_system_id
                
                # Initialize connections
                if system.solar_system_id not in SYSTEM_CONNECTIONS:
                    SYSTEM_CONNECTIONS[system.solar_system_id] = set()
                
                # Get stargates for this system
                stargates = system_info.get("stargates", [])
                
                # For each stargate, get the destination system
                for stargate_id in stargates:
                    try:
                        stargate_info = await self.esi_client.get(f"/universe/stargates/{stargate_id}/")
                        destination = stargate_info.get("destination", {})
                        destination_system_id = destination.get("system_id")
                        
                        if destination_system_id:
                            # Add connection
                            SYSTEM_CONNECTIONS[system.solar_system_id].add(destination_system_id)
                            
                            # Initialize reverse connection if needed
                            if destination_system_id not in SYSTEM_CONNECTIONS:
                                SYSTEM_CONNECTIONS[destination_system_id] = set()
                            
                            # Add reverse connection
                            SYSTEM_CONNECTIONS[destination_system_id].add(system.solar_system_id)
                    except Exception as e:
                        logger.warning(f"Error getting stargate {stargate_id} info: {e}")
                        continue
            except Exception as e:
                logger.warning(f"Error getting system {system.solar_system_id} info: {e}")
                continue
        
        logger.info(f"Built connections for {len(SYSTEM_CONNECTIONS)} systems")
        
        # If we couldn't get stargate data, use a fallback approach with mock connections
        if not SYSTEM_CONNECTIONS:
            logger.warning("Using mock system connections due to API limitations")
            self.build_mock_system_connections(systems)
        
        # Debug: Print system connections
        logger.debug("System connections:")
        for system_id, connections in SYSTEM_CONNECTIONS.items():
            system_name = SYSTEM_ID_TO_NAME.get(system_id, f"System {system_id}")
            connection_names = [SYSTEM_ID_TO_NAME.get(conn_id, f"System {conn_id}") for conn_id in connections]
            logger.debug(f"{system_name} ({system_id}) -> {connection_names}")

    def build_mock_system_connections(self, systems: List[FWSystem]) -> None:
        """
        Build mock system connections based on system IDs.
        This is a fallback when we can't get real stargate data.
        
        Args:
            systems (List[FWSystem]): The list of faction warfare systems.
        """
        global SYSTEM_ID_TO_NAME, SYSTEM_NAME_TO_ID, SYSTEM_CONNECTIONS
        
        # Get system names
        for system in systems:
            system_name = system.solar_system_name or f"System {system.solar_system_id}"
            SYSTEM_ID_TO_NAME[system.solar_system_id] = system_name
            SYSTEM_NAME_TO_ID[system_name] = system.solar_system_id
        
        # Create mock connections based on system IDs
        # This is not accurate but provides a fallback
        for i, system in enumerate(systems):
            if system.solar_system_id not in SYSTEM_CONNECTIONS:
                SYSTEM_CONNECTIONS[system.solar_system_id] = set()
            
            # Connect to a few nearby systems based on ID proximity
            for j, other_system in enumerate(systems):
                if i != j and abs(i - j) <= 3:  # Connect to systems with nearby indices
                    SYSTEM_CONNECTIONS[system.solar_system_id].add(other_system.solar_system_id)
                    
                    # Ensure the other system has a connections set
                    if other_system.solar_system_id not in SYSTEM_CONNECTIONS:
                        SYSTEM_CONNECTIONS[other_system.solar_system_id] = set()
                    
                    # Add reverse connection
                    SYSTEM_CONNECTIONS[other_system.solar_system_id].add(system.solar_system_id)
        
        # Add connections for permanent frontline systems
        # This ensures that permanent frontlines are connected to systems of the opposite faction
        amarr_systems = [s for s in systems if s.owner_faction_id == FactionID.AMARR_EMPIRE]
        minmatar_systems = [s for s in systems if s.owner_faction_id == FactionID.MINMATAR_REPUBLIC]
        
        # Connect Amarr permanent frontlines to Minmatar systems
        for system in amarr_systems:
            system_name = SYSTEM_ID_TO_NAME.get(system.solar_system_id, "")
            if system_name in AMARR_PERMANENT_FRONTLINES:
                # Connect to at least one Minmatar system
                if minmatar_systems:
                    minmatar_system = minmatar_systems[0]
                    SYSTEM_CONNECTIONS[system.solar_system_id].add(minmatar_system.solar_system_id)
                    SYSTEM_CONNECTIONS[minmatar_system.solar_system_id].add(system.solar_system_id)
        
        # Connect Minmatar permanent frontlines to Amarr systems
        for system in minmatar_systems:
            system_name = SYSTEM_ID_TO_NAME.get(system.solar_system_id, "")
            if system_name in MINMATAR_PERMANENT_FRONTLINES:
                # Connect to at least one Amarr system
                if amarr_systems:
                    amarr_system = amarr_systems[0]
                    SYSTEM_CONNECTIONS[system.solar_system_id].add(amarr_system.solar_system_id)
                    SYSTEM_CONNECTIONS[amarr_system.solar_system_id].add(system.solar_system_id)
        
        # Log the connections for debugging
        logger.info(f"Built mock connections for {len(SYSTEM_CONNECTIONS)} systems")
        for system_id, connections in SYSTEM_CONNECTIONS.items():
            system_name = SYSTEM_ID_TO_NAME.get(system_id, f"System {system_id}")
            logger.debug(f"Mock connections for {system_name}: {len(connections)} connections")

    async def determine_system_adjacency(self, systems: List[FWSystem]) -> List[FWSystem]:
        """
        Determine the adjacency type for each faction warfare system.
        
        Args:
            systems (List[FWSystem]): The list of faction warfare systems.
        
        Returns:
            List[FWSystem]: The updated list of faction warfare systems with adjacency information.
        """
        # Use the adjacency detector to determine system adjacency
        return self.adjacency_detector.determine_adjacency(systems)

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
            
            # If no data is returned from the API, create mock data for demonstration
            if not faction_stats:
                logger.warning("No faction warfare statistics returned from ESI API. Using mock data.")
                
                # Create mock data for Amarr Empire
                faction_stats[FactionID.AMARR_EMPIRE] = FWFactionStats(
                    faction_id=FactionID.AMARR_EMPIRE,
                    pilots=1250,
                    systems_controlled=35,
                    kills_yesterday=320,
                    kills_last_week=2150,
                    kills_total=125000,
                    victory_points_yesterday=15000,
                    victory_points_last_week=95000,
                    victory_points_total=5000000
                )
                
                # Create mock data for Minmatar Republic
                faction_stats[FactionID.MINMATAR_REPUBLIC] = FWFactionStats(
                    faction_id=FactionID.MINMATAR_REPUBLIC,
                    pilots=1350,
                    systems_controlled=35,
                    kills_yesterday=350,
                    kills_last_week=2300,
                    kills_total=130000,
                    victory_points_yesterday=16000,
                    victory_points_last_week=98000,
                    victory_points_total=5200000
                )
                
                # Create mock data for Caldari State
                faction_stats[FactionID.CALDARI_STATE] = FWFactionStats(
                    faction_id=FactionID.CALDARI_STATE,
                    pilots=1100,
                    systems_controlled=30,
                    kills_yesterday=280,
                    kills_last_week=1950,
                    kills_total=115000,
                    victory_points_yesterday=14000,
                    victory_points_last_week=90000,
                    victory_points_total=4800000
                )
                
                # Create mock data for Gallente Federation
                faction_stats[FactionID.GALLENTE_FEDERATION] = FWFactionStats(
                    faction_id=FactionID.GALLENTE_FEDERATION,
                    pilots=1200,
                    systems_controlled=30,
                    kills_yesterday=300,
                    kills_last_week=2100,
                    kills_total=120000,
                    victory_points_yesterday=15500,
                    victory_points_last_week=93000,
                    victory_points_total=4900000
                )
            
            return faction_stats
        except Exception as e:
            logger.error(f"Error getting faction warfare statistics: {e}", exc_info=True)
            
            # Return mock data in case of error
            logger.warning("Using mock faction warfare statistics due to API error.")
            
            return {
                FactionID.AMARR_EMPIRE: FWFactionStats(
                    faction_id=FactionID.AMARR_EMPIRE,
                    pilots=1250,
                    systems_controlled=35,
                    kills_yesterday=320,
                    kills_last_week=2150,
                    kills_total=125000,
                    victory_points_yesterday=15000,
                    victory_points_last_week=95000,
                    victory_points_total=5000000
                ),
                FactionID.MINMATAR_REPUBLIC: FWFactionStats(
                    faction_id=FactionID.MINMATAR_REPUBLIC,
                    pilots=1350,
                    systems_controlled=35,
                    kills_yesterday=350,
                    kills_last_week=2300,
                    kills_total=130000,
                    victory_points_yesterday=16000,
                    victory_points_last_week=98000,
                    victory_points_total=5200000
                ),
                FactionID.CALDARI_STATE: FWFactionStats(
                    faction_id=FactionID.CALDARI_STATE,
                    pilots=1100,
                    systems_controlled=30,
                    kills_yesterday=280,
                    kills_last_week=1950,
                    kills_total=115000,
                    victory_points_yesterday=14000,
                    victory_points_last_week=90000,
                    victory_points_total=4800000
                ),
                FactionID.GALLENTE_FEDERATION: FWFactionStats(
                    faction_id=FactionID.GALLENTE_FEDERATION,
                    pilots=1200,
                    systems_controlled=30,
                    kills_yesterday=300,
                    kills_last_week=2100,
                    kills_total=120000,
                    victory_points_yesterday=15500,
                    victory_points_last_week=93000,
                    victory_points_total=4900000
                )
            }
    
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
