"""
Web scraper for EVE Online faction warfare data using Selenium.

This module scrapes the EVE Online website to get advantage data for faction warfare systems,
which is not available through the ESI API.
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online Frontlines URL
MINMATAR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/minmatar"
AMARR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/amarr"

class WebScraperSelenium:
    """
    Scraper for EVE Online faction warfare data using Selenium.
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
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.user_agent}")
            
            # Set up the driver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            # Navigate to the page
            driver.get(url)
            
            # Wait for the page to load (adjust timeout as needed)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mantine-WarzoneTable-root"))
            )
            
            # Give the page a moment to fully render
            time.sleep(5)
            
            # Find the warzone table
            warzone_table = driver.find_element(By.CLASS_NAME, "mantine-WarzoneTable-root")
            
            if warzone_table:
                # Process each row in the table
                rows = warzone_table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows:
                    try:
                        # Extract system ID from the row ID
                        system_id = row.get_attribute("id")
                        if not system_id or not system_id.startswith("solarsystem-"):
                            continue
                        
                        # Get system name from the first cell
                        cells = row.find_elements(By.TAG_NAME, "td")
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
            else:
                logger.warning(f"Could not find warzone table on {url}")
            
            # Close the driver
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return advantage_data

# Create a global web scraper instance
web_scraper_selenium = WebScraperSelenium()

def get_web_scraper_selenium() -> WebScraperSelenium:
    """
    Get a web scraper instance.
    
    Returns:
        WebScraperSelenium: A web scraper instance.
    """
    return web_scraper_selenium

