"""
ESI API client adapter for EVE Wiggin.
"""

import logging
from typing import Dict, Any, List, Optional, Union
# Replace the import from rataura with our mock implementation
from eve_wiggin.api.mock_esi_client import ESIClient, get_esi_client as get_rataura_esi_client

# Configure logging
logger = logging.getLogger(__name__)


class ESIClientAdapter:
    """
    Adapter for the Rataura ESI client to provide specific functionality for EVE Wiggin.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the ESI client adapter.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.esi_client = get_rataura_esi_client(access_token)
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the ESI API.
        
        Args:
            endpoint (str): The API endpoint to request.
            params (Optional[Dict[str, Any]], optional): Query parameters for the request.
        
        Returns:
            Dict[str, Any]: The response data.
        """
        return await self.esi_client.get(endpoint, params)
    
    async def get_fw_systems(self) -> List[Dict[str, Any]]:
        """
        Get faction warfare solar systems.
        
        Returns:
            List[Dict[str, Any]]: A list of faction warfare solar systems.
        """
        return await self.esi_client.get_fw_systems()
    
    async def get_fw_wars(self) -> List[Dict[str, Any]]:
        """
        Get faction warfare wars.
        
        Returns:
            List[Dict[str, Any]]: A list of faction warfare wars.
        """
        return await self.esi_client.get_fw_wars()
    
    async def get_fw_stats(self) -> List[Dict[str, Any]]:
        """
        Get faction warfare statistics.
        
        Returns:
            List[Dict[str, Any]]: A list of faction warfare statistics.
        """
        return await self.esi_client.get_fw_stats()
    
    async def get_system(self, system_id: int) -> Dict[str, Any]:
        """
        Get information about a solar system.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Dict[str, Any]: Information about the solar system.
        """
        return await self.esi_client.get_system(system_id)
    
    async def get_constellation(self, constellation_id: int) -> Dict[str, Any]:
        """
        Get information about a constellation.
        
        Args:
            constellation_id (int): The ID of the constellation.
        
        Returns:
            Dict[str, Any]: Information about the constellation.
        """
        return await self.esi_client.get_constellation(constellation_id)
    
    async def get_region(self, region_id: int) -> Dict[str, Any]:
        """
        Get information about a region.
        
        Args:
            region_id (int): The ID of the region.
        
        Returns:
            Dict[str, Any]: Information about the region.
        """
        return await self.esi_client.get_region(region_id)
    
    async def search(self, search: str, categories: List[str], strict: bool = False) -> Dict[str, List[int]]:
        """
        Search for entities that match a query.
        
        Args:
            search (str): The search query.
            categories (List[str]): The categories to search in.
            strict (bool, optional): Whether to perform a strict search. Defaults to False.
        
        Returns:
            Dict[str, List[int]]: The search results.
        """
        return await self.esi_client.search(search, categories, strict)


# Create a global ESI client adapter instance
esi_client_adapter = ESIClientAdapter()


def get_esi_client(access_token: Optional[str] = None) -> ESIClientAdapter:
    """
    Get an ESI client adapter instance.
    
    Args:
        access_token (Optional[str], optional): The access token for authenticated requests.
    
    Returns:
        ESIClientAdapter: An ESI client adapter instance.
    """
    if access_token:
        return ESIClientAdapter(access_token)
    return esi_client_adapter
