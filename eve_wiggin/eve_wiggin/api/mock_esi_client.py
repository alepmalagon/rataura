"""
Mock ESI client module for EVE Wiggin.
This module provides a mock implementation of the rataura.esi.client module.
"""

import logging
import aiohttp
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

# ESI API base URL
ESI_BASE_URL = "https://esi.evetech.net/latest"


class ESIClient:
    """
    Client for the EVE Online ESI API.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the ESI client.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.access_token = access_token
        self.user_agent = "EVE Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)"
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the ESI API.
        
        Args:
            endpoint (str): The API endpoint to request.
            params (Optional[Dict[str, Any]], optional): Query parameters for the request.
        
        Returns:
            Dict[str, Any]: The response data.
        
        Raises:
            Exception: If the request fails.
        """
        url = f"{ESI_BASE_URL}{endpoint}"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"ESI API error: {response.status} - {error_text}")
                    raise Exception(f"ESI API error: {response.status} - {error_text}")
    
    async def post(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the ESI API.
        
        Args:
            endpoint (str): The API endpoint to request.
            data (Dict[str, Any]): The data to send in the request body.
            params (Optional[Dict[str, Any]], optional): Query parameters for the request.
        
        Returns:
            Dict[str, Any]: The response data.
        
        Raises:
            Exception: If the request fails.
        """
        url = f"{ESI_BASE_URL}{endpoint}"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=headers, json=data) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"ESI API error: {response.status} - {error_text}")
                    raise Exception(f"ESI API error: {response.status} - {error_text}")
    
    # Faction Warfare endpoints
    
    async def get_fw_systems(self) -> List[Dict[str, Any]]:
        """
        Get faction warfare solar systems.
        
        Returns:
            List[Dict[str, Any]]: A list of faction warfare solar systems.
        """
        return await self.get("/fw/systems/")
    
    async def get_fw_wars(self) -> List[Dict[str, Any]]:
        """
        Get faction warfare wars.
        
        Returns:
            List[Dict[str, Any]]: A list of faction warfare wars.
        """
        return await self.get("/fw/wars/")
    
    async def get_fw_stats(self) -> List[Dict[str, Any]]:
        """
        Get faction warfare statistics.
        
        Returns:
            List[Dict[str, Any]]: A list of faction warfare statistics.
        """
        return await self.get("/fw/stats/")
    
    async def get_system(self, system_id: int) -> Dict[str, Any]:
        """
        Get information about a solar system.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Dict[str, Any]: Information about the solar system.
        """
        return await self.get(f"/universe/systems/{system_id}/")
    
    async def get_constellation(self, constellation_id: int) -> Dict[str, Any]:
        """
        Get information about a constellation.
        
        Args:
            constellation_id (int): The ID of the constellation.
        
        Returns:
            Dict[str, Any]: Information about the constellation.
        """
        return await self.get(f"/universe/constellations/{constellation_id}/")
    
    async def get_region(self, region_id: int) -> Dict[str, Any]:
        """
        Get information about a region.
        
        Args:
            region_id (int): The ID of the region.
        
        Returns:
            Dict[str, Any]: Information about the region.
        """
        return await self.get(f"/universe/regions/{region_id}/")
    
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
        # Use the universe/ids endpoint instead of /search/
        data = [search]
        
        try:
            result = await self.post("/universe/ids/", data=data)
            
            # Filter results by requested categories
            filtered_result = {}
            for category in categories:
                category_key = category
                # Map category names to the response format
                if category == 'alliance':
                    category_key = 'alliances'
                elif category == 'character':
                    category_key = 'characters'
                elif category == 'corporation':
                    category_key = 'corporations'
                elif category == 'inventory_type':
                    category_key = 'inventory_types'
                elif category == 'region':
                    category_key = 'regions'
                elif category == 'solar_system':
                    category_key = 'systems'
                
                # Initialize the category in the result
                filtered_result[category] = []
                
                # Check if the category exists in the result
                if category_key in result and result[category_key]:
                    filtered_result[category] = [item['id'] for item in result[category_key]]
                    logger.info(f"Found {len(filtered_result[category])} results for '{search}' in category '{category}'")
                else:
                    logger.info(f"No results found for '{search}' in category '{category}'")
            
            return filtered_result
        except Exception as e:
            logger.error(f"Error searching for '{search}' in categories {categories}: {e}")
            # Return empty result on error
            return {category: [] for category in categories}


# Create a global ESI client instance
esi_client = ESIClient()


def get_esi_client(access_token: Optional[str] = None) -> ESIClient:
    """
    Get an ESI client instance.
    
    Args:
        access_token (Optional[str], optional): The access token for authenticated requests.
    
    Returns:
        ESIClient: An ESI client instance.
    """
    if access_token:
        return ESIClient(access_token)
    return esi_client

