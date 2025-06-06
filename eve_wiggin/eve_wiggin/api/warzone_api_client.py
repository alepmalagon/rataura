"""
Warzone API client for EVE Online.

This module provides a client for the EVE Online warzone status API.
"""

import logging
import aiohttp
import json
import os
import time
import asyncio
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online Warzone API URL
WARZONE_API_URL = "https://www.eveonline.com/api/warzone/status"

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../data/cache")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Faction IDs
AMARR_FACTION_ID = 500003
MINMATAR_FACTION_ID = 500002


class WarzoneAPIClient:
    """
    Client for the EVE Online warzone status API.
    """
    
    def __init__(self):
        """
        Initialize the warzone API client.
        """
        self.user_agent = "EVE Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)"
        self._cache_file = os.path.join(CACHE_DIR, "warzone_status.json")
        self._cache_ttl = 600  # 10 minutes
        self._lock = asyncio.Lock()
        self._system_names_cache = {}  # In-memory cache for system names
    
    async def get_warzone_status(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get the current warzone status.
        
        Args:
            force_refresh (bool, optional): Force a refresh of the cache. Defaults to False.
        
        Returns:
            List[Dict[str, Any]]: A list of warzone system status data.
        """
        async with self._lock:
            # Check if cache is valid
            if not force_refresh and os.path.exists(self._cache_file):
                cache_age = time.time() - os.path.getmtime(self._cache_file)
                if cache_age < self._cache_ttl:
                    try:
                        with open(self._cache_file, "r") as f:
                            data = json.load(f)
                        logger.debug("Using cached warzone status data")
                        return data
                    except Exception as e:
                        logger.warning(f"Error reading cache: {e}")
            
            # Fetch fresh data
            try:
                logger.info("Fetching warzone status data from API")
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "application/json",
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(WARZONE_API_URL, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Cache the data
                            with open(self._cache_file, "w") as f:
                                json.dump(data, f)
                            
                            logger.info(f"Fetched warzone status data for {len(data)} systems")
                            return data
                        else:
                            error_text = await response.text()
                            logger.error(f"Warzone API error: {response.status} - {error_text}")
                            raise Exception(f"Warzone API error: {response.status} - {error_text}")
            except Exception as e:
                logger.error(f"Error accessing warzone API: {e}")
                
                # If we have a cache file, use it as a fallback
                if os.path.exists(self._cache_file):
                    try:
                        with open(self._cache_file, "r") as f:
                            data = json.load(f)
                        logger.warning("Using cached warzone status data as fallback")
                        return data
                    except Exception as cache_error:
                        logger.error(f"Error reading cache fallback: {cache_error}")
                
                # If all else fails, return an empty list
                return []
    
    async def get_system_advantage_data(self, force_refresh: bool = False) -> Dict[str, Dict[str, float]]:
        """
        Get advantage data for all systems in the warzone.
        
        Args:
            force_refresh (bool, optional): Force a refresh of the cache. Defaults to False.
        
        Returns:
            Dict[str, Dict[str, float]]: Dictionary mapping system IDs to advantage data.
            The advantage data is a dictionary with keys 'amarr', 'minmatar', and 'net_advantage'.
        """
        warzone_data = await self.get_warzone_status(force_refresh)
        
        # Process the data to extract advantage information
        advantage_data = {}
        
        for system in warzone_data:
            try:
                system_id = system.get("solarsystemID")
                if not system_id:
                    logger.warning(f"System missing ID in warzone data: {system}")
                    continue
                
                # Convert to string for consistent dictionary keys
                system_id_str = str(system_id)
                
                # Extract advantage data for each faction
                advantage_info = system.get("advantage", [])
                amarr_advantage = 0.0
                minmatar_advantage = 0.0
                
                for faction_advantage in advantage_info:
                    faction_id = faction_advantage.get("factionID")
                    total_amount = faction_advantage.get("totalAmount", 0)
                    
                    if faction_id == AMARR_FACTION_ID:
                        amarr_advantage = total_amount / 100.0  # Convert to a 0-1 scale
                    elif faction_id == MINMATAR_FACTION_ID:
                        minmatar_advantage = total_amount / 100.0  # Convert to a 0-1 scale
                
                # Calculate net advantage (Minmatar - Amarr)
                net_advantage = minmatar_advantage - amarr_advantage
                
                advantage_data[system_id_str] = {
                    "amarr": amarr_advantage,
                    "minmatar": minmatar_advantage,
                    "net_advantage": net_advantage
                }
                
                logger.debug(f"Processed advantage for system ID {system_id_str}: Amarr={amarr_advantage}, Minmatar={minmatar_advantage}, Net={net_advantage}")
                
            except Exception as e:
                logger.error(f"Error processing system advantage data: {e}")
        
        logger.info(f"Processed advantage data for {len(advantage_data)} systems")
        return advantage_data
    
    async def _get_system_name(self, system_id: int) -> Optional[str]:
        """
        Get the name of a solar system from its ID.
        
        This method uses a combination of in-memory cache and file cache to map system IDs to names.
        It also loads system names from the pickle file if available.
        
        Args:
            system_id (int): The ID of the solar system.
        
        Returns:
            Optional[str]: The name of the solar system, or None if not found.
        """
        # Convert system_id to string for dictionary lookup
        system_id_str = str(system_id)
        
        # Check in-memory cache first
        if system_id_str in self._system_names_cache:
            return self._system_names_cache[system_id_str]
        
        # Try to load from file cache
        cache_file = os.path.join(CACHE_DIR, "system_names.json")
        
        # Load the cache if it exists
        system_names = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    system_names = json.load(f)
                
                # Update in-memory cache
                self._system_names_cache.update(system_names)
                
                # If we have the system name in the cache, return it
                if system_id_str in system_names:
                    return system_names[system_id_str]
            except Exception as e:
                logger.warning(f"Error reading system names cache: {e}")
        
        # If not found in cache, try to load from the pickle file
        try:
            # Path to the pickle file
            pickle_file = os.path.join(os.path.dirname(__file__), "..", "data", "ama_min.pickle")
            
            if os.path.exists(pickle_file):
                import pickle
                with open(pickle_file, "rb") as f:
                    systems_data = pickle.load(f)
                
                # Check if systems_data is a dictionary
                if isinstance(systems_data, dict):
                    # Try to find the system in the pickle data
                    if system_id_str in systems_data:
                        system_name = systems_data[system_id_str].get("solar_system_name")
                        if system_name:
                            # Update caches
                            self._system_names_cache[system_id_str] = system_name
                            system_names[system_id_str] = system_name
                            
                            # Save to file cache
                            with open(cache_file, "w") as f:
                                json.dump(system_names, f)
                            
                            return system_name
                    
                    # If not found by ID, try to find by solar_system_id
                    for sys_id, system in systems_data.items():
                        if str(system.get("solar_system_id")) == system_id_str:
                            system_name = system.get("solar_system_name")
                            if system_name:
                                # Update caches
                                self._system_names_cache[system_id_str] = system_name
                                system_names[system_id_str] = system_name
                                
                                # Save to file cache
                                with open(cache_file, "w") as f:
                                    json.dump(system_names, f)
                                
                                return system_name
        except Exception as e:
            logger.warning(f"Error loading system name from pickle: {e}")
        
        # If all else fails, return a placeholder
        placeholder = f"System {system_id}"
        self._system_names_cache[system_id_str] = placeholder
        system_names[system_id_str] = placeholder
        
        # Save to file cache
        with open(cache_file, "w") as f:
            json.dump(system_names, f)
        
        return placeholder


# Create a global warzone API client instance
warzone_api_client = WarzoneAPIClient()


def get_warzone_api_client() -> WarzoneAPIClient:
    """
    Get a warzone API client instance.
    
    Returns:
        WarzoneAPIClient: A warzone API client instance.
    """
    return warzone_api_client
