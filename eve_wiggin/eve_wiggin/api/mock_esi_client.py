"""
Mock ESI client module for EVE Wiggin.
This module provides a mock implementation of the rataura.esi.client module.
"""

import logging
import aiohttp
import json
import os
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

# ESI API base URL
ESI_BASE_URL = "https://esi.evetech.net/latest"

# Mock data directory
MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/mock")

# Ensure mock data directory exists
os.makedirs(MOCK_DATA_DIR, exist_ok=True)

# Define permanent frontline systems for reference
AMARR_PERMANENT_FRONTLINES = {
    "Amamake", "Bosboger", "Auner", "Resbroko", "Evati", "Arnstur"
}

MINMATAR_PERMANENT_FRONTLINES = {
    "Raa", "Kamela", "Sosala", "Huola", "Anka", "Iesa", "Uusanen", "Saikamon", "Halmah"
}

# Mock stargate connections for key systems in Amarr/Minmatar warzone
MOCK_STARGATES = {
    # Huola connections
    30003067: [
        {"destination": {"system_id": 30003068}},  # Huola -> Kourmonen
        {"destination": {"system_id": 30003069}}   # Huola -> Kamela
    ],
    # Kamela connections
    30003069: [
        {"destination": {"system_id": 30003067}},  # Kamela -> Huola
        {"destination": {"system_id": 30003070}}   # Kamela -> Sosala
    ],
    # Amamake connections
    30002537: [
        {"destination": {"system_id": 30002538}},  # Amamake -> Vard
        {"destination": {"system_id": 30002539}}   # Amamake -> Siseide
    ],
    # Add more connections for other permanent frontline systems
    # Amarr permanent frontlines
    30002538: [  # Vard
        {"destination": {"system_id": 30002537}},  # Vard -> Amamake
        {"destination": {"system_id": 30002540}}   # Vard -> Some Minmatar system
    ],
    30002539: [  # Siseide
        {"destination": {"system_id": 30002537}},  # Siseide -> Amamake
        {"destination": {"system_id": 30002541}}   # Siseide -> Some Minmatar system
    ],
    # Minmatar permanent frontlines
    30003068: [  # Kourmonen
        {"destination": {"system_id": 30003067}},  # Kourmonen -> Huola
        {"destination": {"system_id": 30003071}}   # Kourmonen -> Some Amarr system
    ],
    30003070: [  # Sosala
        {"destination": {"system_id": 30003069}},  # Sosala -> Kamela
        {"destination": {"system_id": 30003072}}   # Sosala -> Some Amarr system
    ]
}

# Mock system names for key systems
MOCK_SYSTEM_NAMES = {
    30003067: "Huola",
    30003068: "Kourmonen",
    30003069: "Kamela",
    30003070: "Sosala",
    30002537: "Amamake",
    30002538: "Vard",
    30002539: "Siseide",
    30002540: "Minmatar System 1",
    30002541: "Minmatar System 2",
    30003071: "Amarr System 1",
    30003072: "Amarr System 2",
    # Add more permanent frontline systems
    30002542: "Bosboger",
    30002543: "Auner",
    30002544: "Resbroko",
    30002545: "Evati",
    30002546: "Arnstur",
    30003073: "Raa",
    30003074: "Anka",
    30003075: "Iesa",
    30003076: "Uusanen",
    30003077: "Saikamon",
    30003078: "Halmah"
}


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
        # Check if this is a stargate endpoint
        if endpoint.startswith("/universe/stargates/"):
            try:
                stargate_id = int(endpoint.split("/")[-1])
                return self.get_mock_stargate(stargate_id)
            except ValueError as e:
                logger.error(f"Invalid stargate ID in endpoint {endpoint}: {e}")
                return self.get_mock_stargate(0)  # Return a default stargate
        
        url = f"{ESI_BASE_URL}{endpoint}"
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"ESI API error: {response.status} - {error_text}")
                        raise Exception(f"ESI API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error accessing ESI API: {e}")
            # Return mock data for specific endpoints
            if endpoint == "/fw/systems/":
                return self.get_mock_fw_systems()
            elif endpoint.startswith("/universe/systems/"):
                try:
                    system_id = int(endpoint.split("/")[-1])
                    return self.get_mock_system(system_id)
                except ValueError as e:
                    logger.error(f"Invalid system ID in endpoint {endpoint}: {e}")
                    return self.get_mock_system(0)  # Return a default system
            else:
                raise
    
    def get_mock_stargate(self, stargate_id: int) -> Dict[str, Any]:
        """
        Get mock stargate information.
        
        Args:
            stargate_id (int): The ID of the stargate.
        
        Returns:
            Dict[str, Any]: Mock stargate information.
        """
        # Extract system ID from stargate ID (our convention: system_id * 10 + index)
        system_id = stargate_id // 10
        index = stargate_id % 10
        
        # Check if we have predefined stargates for this system
        if system_id in MOCK_STARGATES and index < len(MOCK_STARGATES[system_id]):
            destination = MOCK_STARGATES[system_id][index]["destination"]
            return {
                "stargate_id": stargate_id,
                "name": f"Stargate {stargate_id}",
                "destination": destination
            }
        
        # For simplicity, we'll just return a mock destination
        # In a real implementation, we would have a mapping of stargate IDs to destinations
        return {
            "stargate_id": stargate_id,
            "name": f"Stargate {stargate_id}",
            "destination": {
                "stargate_id": stargate_id + 1000,
                "system_id": stargate_id + 2000
            }
        }
    
    def get_mock_system(self, system_id: int) -> Dict[str, Any]:
        """
        Get mock system information.
        
        Args:
            system_id (int): The ID of the system.
        
        Returns:
            Dict[str, Any]: Mock system information.
        """
        # Check if we have a predefined name for this system
        system_name = MOCK_SYSTEM_NAMES.get(system_id, f"System {system_id}")
        
        # Check if we have predefined stargates for this system
        stargates = []
        if system_id in MOCK_STARGATES:
            # In a real implementation, we would generate stargate IDs
            # For simplicity, we'll use system_id * 10 + index
            for i in range(len(MOCK_STARGATES[system_id])):
                stargates.append(system_id * 10 + i)
        else:
            # Generate some random stargates
            for i in range(3):  # Most systems have 3-4 stargates
                stargates.append(system_id * 10 + i)
        
        return {
            "system_id": system_id,
            "name": system_name,
            "security_status": 0.5,
            "security_class": "C",
            "constellation_id": system_id // 100,
            "stargates": stargates
        }
    
    def get_mock_fw_systems(self) -> List[Dict[str, Any]]:
        """
        Get mock faction warfare systems.
        
        Returns:
            List[Dict[str, Any]]: A list of mock faction warfare systems.
        """
        # Path to mock data file
        mock_file = os.path.join(MOCK_DATA_DIR, "fw_systems.json")
        
        # Check if mock data file exists
        if os.path.exists(mock_file):
            try:
                with open(mock_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading mock data: {e}")
        
        # Generate mock data
        systems = []
        
        # Amarr systems
        for i in range(30):
            system_id = 30003000 + i
            systems.append({
                "solar_system_id": system_id,
                "owner_faction_id": 500003,  # Amarr Empire
                "occupier_faction_id": 500003,
                "contested": "uncontested" if i % 3 != 0 else "contested",
                "victory_points": 1000 * (i % 10),
                "victory_points_threshold": 20000,
                "advantage": 0.0
            })
        
        # Minmatar systems
        for i in range(30):
            system_id = 30002500 + i
            systems.append({
                "solar_system_id": system_id,
                "owner_faction_id": 500002,  # Minmatar Republic
                "occupier_faction_id": 500002,
                "contested": "uncontested" if i % 3 != 0 else "contested",
                "victory_points": 1000 * (i % 10),
                "victory_points_threshold": 20000,
                "advantage": 0.0
            })
        
        # Add specific systems with known names
        for system_id, name in MOCK_SYSTEM_NAMES.items():
            # Find if system already exists in the list
            existing = next((s for s in systems if s["solar_system_id"] == system_id), None)
            
            if existing:
                # Update existing system
                if name in AMARR_PERMANENT_FRONTLINES:
                    existing["owner_faction_id"] = 500003  # Amarr Empire
                    existing["occupier_faction_id"] = 500003
                    existing["contested"] = "contested"
                elif name in MINMATAR_PERMANENT_FRONTLINES:
                    existing["owner_faction_id"] = 500002  # Minmatar Republic
                    existing["occupier_faction_id"] = 500002
                    existing["contested"] = "contested"
            else:
                # Add new system
                if name in AMARR_PERMANENT_FRONTLINES:
                    systems.append({
                        "solar_system_id": system_id,
                        "owner_faction_id": 500003,  # Amarr Empire
                        "occupier_faction_id": 500003,
                        "contested": "contested",
                        "victory_points": 5000,
                        "victory_points_threshold": 20000,
                        "advantage": 0.0
                    })
                elif name in MINMATAR_PERMANENT_FRONTLINES:
                    systems.append({
                        "solar_system_id": system_id,
                        "owner_faction_id": 500002,  # Minmatar Republic
                        "occupier_faction_id": 500002,
                        "contested": "contested",
                        "victory_points": 5000,
                        "victory_points_threshold": 20000,
                        "advantage": 0.0
                    })
        
        # Save mock data for future use
        try:
            os.makedirs(os.path.dirname(mock_file), exist_ok=True)
            with open(mock_file, "w") as f:
                json.dump(systems, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving mock data: {e}")
        
        return systems
    
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
        try:
            return await self.get("/fw/systems/")
        except Exception as e:
            logger.error(f"Error getting faction warfare systems: {e}")
            return self.get_mock_fw_systems()
    
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
        try:
            # Ensure system_id is an integer
            if not isinstance(system_id, int):
                try:
                    system_id = int(system_id)
                except (ValueError, TypeError) as e:
                    logger.error(f"Error getting system {system_id}: {e}")
                    # Return a default system with the provided ID
                    return self.get_mock_system(0)  # Use a default ID if conversion fails
            
            return await self.get(f"/universe/systems/{system_id}/")
        except Exception as e:
            logger.error(f"Error getting system {system_id}: {e}")
            return self.get_mock_system(system_id)
    
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
