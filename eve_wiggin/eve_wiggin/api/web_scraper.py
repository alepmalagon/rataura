"""
Web scraper for EVE Online faction warfare data.

This module scrapes the EVE Online website to get advantage data for faction warfare systems,
which is not available through the ESI API.
"""

import logging
import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online Frontlines URL
MINMATAR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/minmatar"
AMARR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/amarr"

class WebScraper:
    """
    Scraper for EVE Online faction warfare data.
    """
    
    def __init__(self):
        """
        Initialize the web scraper.
        """
        self.user_agent = "EVE Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)"
        self._advantage_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 600  # 10 minutes
        self._lock = asyncio.Lock()
    
    async def get_advantage_data(self, force_refresh: bool = False) -> Dict[str, float]:
        """
        Get advantage data for faction warfare systems.
        
        Args:
            force_refresh (bool, optional): Force a refresh of the cache. Defaults to False.
        
        Returns:
            Dict[str, float]: Dictionary mapping system names to advantage values.
        """
        async with self._lock:
            current_time = asyncio.get_event_loop().time()
            
            # Check if cache is valid
            if not force_refresh and self._advantage_cache and (current_time - self._cache_timestamp) < self._cache_ttl:
                logger.debug("Using cached advantage data")
                return self._advantage_cache
            
            # Scrape both Amarr and Minmatar frontlines pages
            amarr_data = await self._scrape_frontlines_page(AMARR_FRONTLINES_URL)
            minmatar_data = await self._scrape_frontlines_page(MINMATAR_FRONTLINES_URL)
            
            # Merge the data, with Minmatar data taking precedence in case of duplicates
            combined_data = {**amarr_data, **minmatar_data}
            
            # Update cache
            self._advantage_cache = combined_data
            self._cache_timestamp = current_time
            
            logger.info(f"Scraped advantage data for {len(combined_data)} systems")
            return combined_data
    
    async def _scrape_frontlines_page(self, url: str) -> Dict[str, float]:
        """
        Scrape a frontlines page for advantage data.
        
        Args:
            url (str): The URL of the frontlines page.
        
        Returns:
            Dict[str, float]: Dictionary mapping system names to advantage values.
        """
        advantage_data = {}
        
        try:
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Parse HTML
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Find the warzone table
                        warzone_table = soup.find('table', class_='mantine-WarzoneTable-root')
                        
                        if warzone_table:
                            # Process each row in the table
                            for row in warzone_table.find_all('tr'):
                                # Extract system ID from the row ID
                                system_id_match = re.search(r'solarsystem-(\d+)', row.get('id', ''))
                                if not system_id_match:
                                    continue
                                
                                # Get system name from the first cell
                                system_name_cell = row.find('td')
                                if not system_name_cell:
                                    continue
                                
                                system_name = system_name_cell.text.strip()
                                
                                # Find the advantage column (5th column)
                                advantage_cell = row.find('td', class_='mantine-WarzoneTable-columnAdvantage')
                                if not advantage_cell:
                                    continue
                                
                                # Extract the advantage value
                                advantage_text = advantage_cell.text.strip()
                                advantage_match = re.search(r'(\d+)%', advantage_text)
                                
                                if advantage_match:
                                    advantage_value = float(advantage_match.group(1)) / 100.0
                                    advantage_data[system_name] = advantage_value
                                    logger.debug(f"Scraped advantage for {system_name}: {advantage_value}")
                        else:
                            logger.warning(f"Could not find warzone table on {url}")
                    else:
                        logger.error(f"Error scraping {url}: {response.status}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return advantage_data

# Create a global web scraper instance
web_scraper = WebScraper()

def get_web_scraper() -> WebScraper:
    """
    Get a web scraper instance.
    
    Returns:
        WebScraper: A web scraper instance.
    """
    return web_scraper

