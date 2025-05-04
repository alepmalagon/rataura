"""
Cached ESI client module for EVE Wiggin.
This module provides a cached implementation of the rataura.esi.client module with rate limiting.
"""

import logging
import aiohttp
import json
import os
import time
import asyncio
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import pickle

# Configure logging
logger = logging.getLogger(__name__)

# ESI API base URL
ESI_BASE_URL = "https://esi.evetech.net/latest"

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(__file__), "../data/cache")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Rate limiting settings
# ESI API has a rate limit of 100 requests per second per IP
# We'll be more conservative and limit to 20 requests per second
MAX_REQUESTS_PER_SECOND = 20
REQUEST_WINDOW = 1.0  # 1 second window


class RateLimiter:
    """
    Rate limiter for API requests.
    """
    
    def __init__(self, max_requests: int = MAX_REQUESTS_PER_SECOND, window: float = REQUEST_WINDOW):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests (int): Maximum number of requests allowed in the window.
            window (float): Time window in seconds.
        """
        self.max_requests = max_requests
        self.window = window
        self.request_timestamps = []
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """
        Acquire permission to make a request, waiting if necessary.
        """
        async with self._lock:
            now = time.time()
            
            # Remove timestamps older than the window
            self.request_timestamps = [ts for ts in self.request_timestamps if now - ts <= self.window]
            
            # If we've reached the limit, wait until we can make another request
            if len(self.request_timestamps) >= self.max_requests:
                oldest = min(self.request_timestamps)
                wait_time = self.window - (now - oldest)
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            
            # Add the current timestamp and proceed
            self.request_timestamps.append(time.time())


class Cache:
    """
    Cache for API responses.
    """
    
    def __init__(self, cache_dir: str = CACHE_DIR):
        """
        Initialize the cache.
        
        Args:
            cache_dir (str): Directory to store cache files.
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a cache key for the request.
        
        Args:
            endpoint (str): API endpoint.
            params (Optional[Dict[str, Any]]): Request parameters.
        
        Returns:
            str: Cache key.
        """
        if params:
            param_str = json.dumps(params, sort_keys=True)
            return f"{endpoint}_{param_str}"
        return endpoint
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get the file path for a cache key.
        
        Args:
            key (str): Cache key.
        
        Returns:
            str: File path.
        """
        # Create a filename-safe version of the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return os.path.join(self.cache_dir, f"{safe_key}.pickle")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get a cached response.
        
        Args:
            endpoint (str): API endpoint.
            params (Optional[Dict[str, Any]]): Request parameters.
        
        Returns:
            Optional[Dict[str, Any]]: Cached response or None if not found or expired.
        """
        key = self._get_cache_key(endpoint, params)
        path = self._get_cache_path(key)
        
        if not os.path.exists(path):
            return None
        
        try:
            with open(path, "rb") as f:
                cached_data = pickle.load(f)
            
            # Check if the cache has expired
            if datetime.now() > cached_data["expires"]:
                logger.debug(f"Cache expired for {endpoint}")
                return None
            
            logger.debug(f"Cache hit for {endpoint}")
            return cached_data["data"]
        except Exception as e:
            logger.warning(f"Error reading cache for {endpoint}: {e}")
            return None
    
    def set(self, endpoint: str, params: Optional[Dict[str, Any]], data: Dict[str, Any], ttl: int = 300):
        """
        Cache a response.
        
        Args:
            endpoint (str): API endpoint.
            params (Optional[Dict[str, Any]]): Request parameters.
            data (Dict[str, Any]): Response data.
            ttl (int): Time to live in seconds. Default is 5 minutes.
        """
        key = self._get_cache_key(endpoint, params)
        path = self._get_cache_path(key)
        
        try:
            cached_data = {
                "data": data,
                "expires": datetime.now() + timedelta(seconds=ttl),
                "endpoint": endpoint,
                "params": params
            }
            
            with open(path, "wb") as f:
                pickle.dump(cached_data, f)
            
            logger.debug(f"Cached response for {endpoint} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"Error caching response for {endpoint}: {e}")


class ESIClient:
    """
    Client for the EVE Online ESI API with caching and rate limiting.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the ESI client.
        
        Args:
            access_token (Optional[str], optional): The access token for authenticated requests.
        """
        self.access_token = access_token
        self.user_agent = "EVE Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)"
        self.cache = Cache()
        self.rate_limiter = RateLimiter()
        
        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            # Default TTL for all endpoints
            "default": 300,  # 5 minutes
            
            # Specific TTLs for different endpoint types
            "/fw/systems/": 600,  # 10 minutes for FW systems
            "/fw/stats/": 600,  # 10 minutes for FW stats
            "/universe/systems/": 86400,  # 24 hours for system info (rarely changes)
            "/universe/constellations/": 86400,  # 24 hours for constellation info
            "/universe/regions/": 86400,  # 24 hours for region info
            "/universe/stargates/": 86400,  # 24 hours for stargate info
        }
    
    def _get_ttl(self, endpoint: str) -> int:
        """
        Get the TTL for an endpoint.
        
        Args:
            endpoint (str): The API endpoint.
        
        Returns:
            int: TTL in seconds.
        """
        # Check for exact matches
        if endpoint in self.ttl_settings:
            return self.ttl_settings[endpoint]
        
        # Check for prefix matches
        for prefix, ttl in self.ttl_settings.items():
            if endpoint.startswith(prefix):
                return ttl
        
        # Return default TTL
        return self.ttl_settings["default"]
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to the ESI API with caching and rate limiting.
        
        Args:
            endpoint (str): The API endpoint to request.
            params (Optional[Dict[str, Any]], optional): Query parameters for the request.
        
        Returns:
            Dict[str, Any]: The response data.
        
        Raises:
            Exception: If the request fails.
        """
        # Check cache first
        cached_response = self.cache.get(endpoint, params)
        if cached_response is not None:
            return cached_response
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
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
                        data = await response.json()
                        
                        # Cache the response
                        ttl = self._get_ttl(endpoint)
                        self.cache.set(endpoint, params, data, ttl)
                        
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"ESI API error: {response.status} - {error_text}")
                        raise Exception(f"ESI API error: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"Error accessing ESI API: {e}")
            raise
    
    async def post(self, endpoint: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a POST request to the ESI API with rate limiting.
        
        Args:
            endpoint (str): The API endpoint to request.
            data (Dict[str, Any]): The data to send in the request body.
            params (Optional[Dict[str, Any]], optional): Query parameters for the request.
        
        Returns:
            Dict[str, Any]: The response data.
        
        Raises:
            Exception: If the request fails.
        """
        # POST requests are not cached as they typically modify data
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
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
        # Ensure system_id is an integer
        if not isinstance(system_id, int):
            try:
                system_id = int(system_id)
            except (ValueError, TypeError) as e:
                logger.error(f"Error getting system {system_id}: {e}")
                raise ValueError(f"Invalid system ID: {system_id}")
        
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

