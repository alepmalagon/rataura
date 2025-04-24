"""
ESI API client module for the Rataura application.
"""

import logging
import aiohttp
import json
from typing import Dict, Any, Optional, List, Union
from rataura.config import settings

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
        self.user_agent = settings.eve_user_agent
    
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
    
    # Alliance endpoints
    
    async def get_alliances(self) -> List[int]:
        """
        Get a list of all alliances.
        
        Returns:
            List[int]: A list of alliance IDs.
        """
        return await self.get("/alliances/")
    
    async def get_alliance(self, alliance_id: int) -> Dict[str, Any]:
        """
        Get information about an alliance.
        
        Args:
            alliance_id (int): The ID of the alliance.
        
        Returns:
            Dict[str, Any]: Information about the alliance.
        """
        return await self.get(f"/alliances/{alliance_id}/")
    
    # Character endpoints
    
    async def get_character(self, character_id: int) -> Dict[str, Any]:
        """
        Get information about a character.
        
        Args:
            character_id (int): The ID of the character.
        
        Returns:
            Dict[str, Any]: Information about the character.
        """
        return await self.get(f"/characters/{character_id}/")
    
    async def get_character_skills(self, character_id: int) -> Dict[str, Any]:
        """
        Get a character's skills.
        
        Args:
            character_id (int): The ID of the character.
        
        Returns:
            Dict[str, Any]: The character's skills.
        """
        return await self.get(f"/characters/{character_id}/skills/")
    
    # Corporation endpoints
    
    async def get_corporation(self, corporation_id: int) -> Dict[str, Any]:
        """
        Get information about a corporation.
        
        Args:
            corporation_id (int): The ID of the corporation.
        
        Returns:
            Dict[str, Any]: Information about the corporation.
        """
        return await self.get(f"/corporations/{corporation_id}/")
    
    # Universe endpoints
    
    async def get_types(self, page: int = 1) -> List[int]:
        """
        Get a list of type IDs.
        
        Args:
            page (int, optional): The page number. Defaults to 1.
        
        Returns:
            List[int]: A list of type IDs.
        """
        return await self.get("/universe/types/", params={"page": page})
    
    async def get_type(self, type_id: int) -> Dict[str, Any]:
        """
        Get information about a type.
        
        Args:
            type_id (int): The ID of the type.
        
        Returns:
            Dict[str, Any]: Information about the type.
        """
        return await self.get(f"/universe/types/{type_id}/")
    
    async def get_system(self, system_id: int) -> Dict[str, Any]:
        """
        Get information about a solar system.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Dict[str, Any]: Information about the solar system.
        """
        return await self.get(f"/universe/systems/{system_id}/")
    
    async def get_region(self, region_id: int) -> Dict[str, Any]:
        """
        Get information about a region.
        
        Args:
            region_id (int): The ID of the region.
        
        Returns:
            Dict[str, Any]: Information about the region.
        """
        return await self.get(f"/universe/regions/{region_id}/")
    
    # Market endpoints
    
    async def get_market_prices(self) -> List[Dict[str, Any]]:
        """
        Get market prices for all items.
        
        Returns:
            List[Dict[str, Any]]: A list of market prices.
        """
        return await self.get("/markets/prices/")
    
    async def get_market_orders(self, region_id: int, type_id: Optional[int] = None, order_type: str = "all", page: int = 1) -> List[Dict[str, Any]]:
        """
        Get market orders in a region.
        
        Args:
            region_id (int): The ID of the region.
            type_id (Optional[int], optional): The ID of the type to filter by.
            order_type (str, optional): The type of order to filter by. Defaults to "all".
            page (int, optional): The page number. Defaults to 1.
        
        Returns:
            List[Dict[str, Any]]: A list of market orders.
        """
        params = {
            "order_type": order_type,
            "page": page,
        }
        
        if type_id:
            params["type_id"] = type_id
        
        return await self.get(f"/markets/{region_id}/orders/", params=params)
    
    # Search endpoint
    
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
        params = {
            "search": search,
            "categories": ",".join(categories),
            "strict": str(strict).lower(),
        }
        
        return await self.get("/search/", params=params)
    
    # Utility methods
    
    async def resolve_ids(self, ids: List[int]) -> List[Dict[str, Any]]:
        """
        Resolve a list of IDs to names and categories.
        
        Args:
            ids (List[int]): The IDs to resolve.
        
        Returns:
            List[Dict[str, Any]]: The resolved names and categories.
        """
        return await self.post("/universe/names/", data=ids)


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
