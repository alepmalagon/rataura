"""
Faction Warfare API module.
"""

import logging
from typing import Dict, List, Optional, Any

from eve_wiggin.services.fw_analyzer import FWAnalyzer
from eve_wiggin.models.faction_warfare import Warzone

# Configure logging
logger = logging.getLogger(__name__)


class FWApi:
    """
    API for faction warfare data.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the faction warfare API.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.analyzer = FWAnalyzer(access_token)
    
    async def get_warzone_status(self) -> Dict[str, Any]:
        """
        Get the status of all faction warfare warzones.
        
        Returns:
            Dict[str, Any]: The status of all faction warfare warzones.
        """
        try:
            warzone_status = await self.analyzer.get_warzone_status()
            return warzone_status.dict()
        except Exception as e:
            logger.error(f"Error in get_warzone_status API: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def get_system_details(self, system_id: int) -> Dict[str, Any]:
        """
        Get detailed information about a faction warfare system.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Dict[str, Any]: Detailed information about the system.
        """
        try:
            system_details = await self.analyzer.get_system_details(system_id)
            return system_details
        except Exception as e:
            logger.error(f"Error in get_system_details API: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def search_system(self, system_name: str) -> Dict[str, Any]:
        """
        Search for a solar system by name and get its details if it's part of faction warfare.
        
        Args:
            system_name (str): The name of the solar system.
        
        Returns:
            Dict[str, Any]: Detailed information about the system if found.
        """
        try:
            # Search for the system
            search_result = await self.analyzer.esi_client.search(system_name, ["solar_system"], strict=True)
            
            if "solar_system" in search_result and search_result["solar_system"]:
                system_id = search_result["solar_system"][0]
                return await self.get_system_details(system_id)
            else:
                return {"error": f"Solar system '{system_name}' not found"}
        except Exception as e:
            logger.error(f"Error in search_system API: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def get_warzone_systems(self, warzone: str = Warzone.AMARR_MINMATAR) -> List[Dict[str, Any]]:
        """
        Get all systems in a specific warzone.
        
        Args:
            warzone (str, optional): The warzone to get systems for. Defaults to Warzone.AMARR_MINMATAR.
        
        Returns:
            List[Dict[str, Any]]: A list of systems in the warzone.
        """
        try:
            # Get all faction warfare systems
            systems = await self.analyzer.get_fw_systems()
            
            # Filter systems by warzone
            warzone_systems = []
            for system in systems:
                if system.warzone == warzone:
                    # Get detailed information for each system
                    system_details = await self.get_system_details(system.solar_system_id)
                    warzone_systems.append(system_details)
            
            return warzone_systems
        except Exception as e:
            logger.error(f"Error in get_warzone_systems API: {e}", exc_info=True)
            return [{"error": str(e)}]
