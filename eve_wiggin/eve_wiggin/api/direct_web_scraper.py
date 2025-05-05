"""
Direct web scraper for EVE Online faction warfare data using requests and BeautifulSoup.

This module provides a simpler, more reliable approach to scraping the EVE Online website
for advantage data without relying on external tools like Puppeteer or Selenium.
"""

import logging
import asyncio
import time
import os
import json
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online Frontlines URL
MINMATAR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/minmatar"
AMARR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/amarr"

# Debug folder for saving raw HTML
DEBUG_FOLDER = "./eve_wiggin/debug_html"

class DirectWebScraper:
    """
    Direct web scraper for EVE Online faction warfare data using requests and BeautifulSoup.
    """
    
    def __init__(self):
        """
        Initialize the direct web scraper.
        """
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self._advantage_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 600  # 10 minutes
        self._lock = asyncio.Lock()
        
        # Create debug folder if it doesn't exist
        os.makedirs(DEBUG_FOLDER, exist_ok=True)
    
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
            
            # If we didn't get any data, use default values
            if not combined_data:
                logger.warning("Could not scrape advantage data, using default values")
                combined_data = self._get_default_advantage_data()
            
            # Update cache
            self._advantage_cache = combined_data
            self._cache_timestamp = current_time
            
            logger.info(f"Scraped advantage data for {len(combined_data)} systems")
            return combined_data
    
    async def _scrape_frontlines_page(self, url: str, max_retries: int = 3) -> Dict[str, float]:
        """
        Scrape a frontlines page for advantage data with retry mechanism.
        
        Args:
            url (str): The URL of the frontlines page.
            max_retries (int): Maximum number of retry attempts.
        
        Returns:
            Dict[str, float]: Dictionary mapping system names to advantage values.
        """
        advantage_data = {}
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping {url} (attempt {attempt + 1}/{max_retries})")
                
                headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'text/html,application/xhtml+xml,application/xml',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                }
                
                # Add a random delay between attempts to avoid rate limiting
                if attempt > 0:
                    delay = 2 + attempt * 3  # Increasing delay with each retry
                    logger.info(f"Waiting {delay} seconds before retry...")
                    await asyncio.sleep(delay)
                
                # Make the request
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                # Save the raw HTML to a file for debugging
                faction = "amarr" if "amarr" in url else "minmatar"
                timestamp = int(time.time())
                html_file_path = os.path.join(DEBUG_FOLDER, f"{faction}_direct_{timestamp}.html")
                
                with open(html_file_path, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                logger.info(f"Saved HTML to {html_file_path}")
                
                # Parse the HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for the table with the warzone data
                table = soup.find('table', class_='mantine-WarzoneTable-root')
                
                if table:
                    # Process each row in the table
                    rows = table.find_all('tr')
                    logger.info(f"Found {len(rows)} rows in the table")
                    
                    for row in rows:
                        try:
                            # Check if this is a system row
                            system_id = row.get('id')
                            if not system_id or not system_id.startswith('solarsystem-'):
                                continue
                            
                            # Get system name from the first cell
                            cells = row.find_all('td')
                            if not cells:
                                continue
                            
                            system_name = cells[0].text.strip()
                            
                            # Find the advantage column (5th column)
                            if len(cells) >= 5:
                                advantage_cell = cells[4]
                                advantage_text = advantage_cell.text.strip()
                                advantage_match = re.search(r'(\d+)%', advantage_text)
                                
                                if advantage_match:
                                    advantage_value = float(advantage_match.group(1)) / 100.0
                                    advantage_data[system_name] = advantage_value
                                    logger.debug(f"Scraped advantage for {system_name}: {advantage_value}")
                        except Exception as e:
                            logger.error(f"Error processing row: {e}")
                    
                    # If we successfully scraped data, break the retry loop
                    if advantage_data:
                        logger.info(f"Successfully scraped advantage data for {len(advantage_data)} systems")
                        break
                    else:
                        logger.warning("No advantage data found in the table")
                        
                        # Check if we need to parse the HTML differently
                        # Sometimes the data might be in a different format or loaded via JavaScript
                        logger.info("Attempting to extract data from JavaScript variables...")
                        
                        # Look for JavaScript data in the page
                        script_data = self._extract_data_from_scripts(response.text)
                        if script_data:
                            advantage_data = script_data
                            logger.info(f"Successfully extracted advantage data from scripts for {len(advantage_data)} systems")
                            break
                else:
                    logger.warning(f"Could not find warzone table on {url}")
                    
                    # Try to extract data from JavaScript variables
                    logger.info("Attempting to extract data from JavaScript variables...")
                    script_data = self._extract_data_from_scripts(response.text)
                    if script_data:
                        advantage_data = script_data
                        logger.info(f"Successfully extracted advantage data from scripts for {len(advantage_data)} systems")
                        break
                
            except Exception as e:
                logger.error(f"Error scraping {url} on attempt {attempt + 1}: {e}")
                
                # If this was the last attempt, use default values
                if attempt == max_retries - 1:
                    logger.warning("All scraping attempts failed")
        
        return advantage_data
    
    def _extract_data_from_scripts(self, html_content: str) -> Dict[str, float]:
        """
        Extract advantage data from JavaScript variables in the HTML.
        
        Args:
            html_content (str): The HTML content of the page.
        
        Returns:
            Dict[str, float]: Dictionary mapping system names to advantage values.
        """
        advantage_data = {}
        
        try:
            # Look for JavaScript data in the page
            # This is a simplified approach - in a real implementation, you might need
            # to use a more sophisticated method to extract data from JavaScript
            
            # Example pattern: "systemName":"Amamake","advantage":0.49
            pattern = r'"systemName":"([^"]+)"[^}]*"advantage":([0-9.]+)'
            matches = re.findall(pattern, html_content)
            
            for system_name, advantage in matches:
                try:
                    advantage_value = float(advantage)
                    advantage_data[system_name] = advantage_value
                    logger.debug(f"Extracted advantage for {system_name}: {advantage_value} from script")
                except ValueError:
                    logger.warning(f"Could not convert advantage value '{advantage}' to float for {system_name}")
        
        except Exception as e:
            logger.error(f"Error extracting data from scripts: {e}")
        
        return advantage_data
    
    def _get_default_advantage_data(self) -> Dict[str, float]:
        """
        Get default advantage data for systems when scraping fails.
        
        Returns:
            Dict[str, float]: Dictionary with default advantage values.
        """
        # This is a simplified approach - in a real implementation, you might want to
        # use more sophisticated default values based on historical data or other factors
        return {
            # Amarr systems
            "Arzad": 0.5,
            "Kamela": 0.5,
            "Huola": 0.5,
            "Kourmonen": 0.5,
            "Aset": 0.5,
            "Siseide": 0.5,
            
            # Minmatar systems
            "Amamake": 0.5,
            "Teonusude": 0.5,
            "Eszur": 0.5,
            "Vard": 0.5,
            "Eytjangard": 0.5,
            "Floseswin": 0.5,
            
            # Add more systems as needed
        }

# Create a global direct web scraper instance
direct_web_scraper = DirectWebScraper()

def get_direct_web_scraper() -> DirectWebScraper:
    """
    Get a direct web scraper instance.
    
    Returns:
        DirectWebScraper: A direct web scraper instance.
    """
    return direct_web_scraper

