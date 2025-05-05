"""
Web scraper for EVE Online faction warfare data using Selenium with fallback to requests/BeautifulSoup.

This module scrapes the EVE Online website to get advantage data for faction warfare systems,
which is not available through the ESI API.
"""

import logging
import asyncio
import time
import os
from typing import Dict, Any, List, Optional
import re
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online Frontlines URL
MINMATAR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/minmatar"
AMARR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/amarr"

# Debug folder for saving raw HTML
DEBUG_FOLDER = "./eve_wiggin/debug_html"

class WebScraperSelenium:
    """
    Scraper for EVE Online faction warfare data using Selenium with fallback to requests/BeautifulSoup.
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
        self._use_fallback = False
        
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
        
        # If we've already determined we need to use the fallback, skip trying Selenium
        if self._use_fallback:
            return await self._scrape_frontlines_page_fallback(url)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping {url} (attempt {attempt + 1}/{max_retries})")
                
                # Set up Chrome options
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument(f"user-agent={self.user_agent}")
                chrome_options.add_argument("--window-size=1920,1080")  # Larger window size
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-gpu")
                
                try:
                    # Try to use ChromeDriverManager
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                except (WebDriverException, Exception) as e:
                    logger.warning(f"Failed to initialize Chrome with ChromeDriverManager: {e}")
                    logger.info("Falling back to direct Chrome initialization")
                    
                    # Try direct initialization without ChromeDriverManager
                    driver = webdriver.Chrome(options=chrome_options)
                
                # Navigate to the page
                driver.get(url)
                
                # Wait for the page to load (increased timeout)
                wait = WebDriverWait(driver, 60)
                
                # Wait for the initial page load
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Execute JavaScript to scroll down the page to trigger lazy loading
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                driver.execute_script("window.scrollTo(0, 0);")
                
                # Wait for the table to appear with a longer timeout
                try:
                    logger.info("Waiting for warzone table to appear...")
                    table_element = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, "mantine-WarzoneTable-root"))
                    )
                    logger.info("Warzone table found!")
                except TimeoutException:
                    logger.warning(f"Timed out waiting for warzone table on attempt {attempt + 1}")
                    
                    # Save the page source for debugging
                    page_source = driver.page_source
                    faction = "amarr" if "amarr" in url else "minmatar"
                    timestamp = int(time.time())
                    html_file_path = os.path.join(DEBUG_FOLDER, f"{faction}_timeout_{timestamp}_attempt{attempt+1}.html")
                    
                    with open(html_file_path, "w", encoding="utf-8") as f:
                        f.write(page_source)
                    
                    logger.info(f"Saved timeout page source to {html_file_path}")
                    
                    # Close the driver and try again
                    driver.quit()
                    continue
                
                # Give the page extra time to fully render
                logger.info("Waiting for page to fully render...")
                time.sleep(10)
                
                # Save the page source to a file for debugging
                page_source = driver.page_source
                faction = "amarr" if "amarr" in url else "minmatar"
                timestamp = int(time.time())
                html_file_path = os.path.join(DEBUG_FOLDER, f"{faction}_page_source_{timestamp}.html")
                
                with open(html_file_path, "w", encoding="utf-8") as f:
                    f.write(page_source)
                
                logger.info(f"Saved page source to {html_file_path}")
                
                # Check if the table is actually populated
                try:
                    # Find the warzone table
                    warzone_table = driver.find_element(By.CLASS_NAME, "mantine-WarzoneTable-root")
                    
                    # Check if the table has rows
                    rows = warzone_table.find_elements(By.TAG_NAME, "tr")
                    
                    if not rows:
                        logger.warning(f"Warzone table found but contains no rows on attempt {attempt + 1}")
                        driver.quit()
                        continue
                    
                    logger.info(f"Found {len(rows)} rows in the warzone table")
                    
                    # Process each row in the table
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
                    
                    # If we successfully scraped data, break the retry loop
                    if advantage_data:
                        logger.info(f"Successfully scraped advantage data for {len(advantage_data)} systems")
                        break
                    else:
                        logger.warning("No advantage data found in the table")
                
                except NoSuchElementException:
                    logger.warning(f"Could not find warzone table on {url} on attempt {attempt + 1}")
                
                # Close the driver
                driver.quit()
                
            except Exception as e:
                logger.error(f"Error scraping {url} with Selenium on attempt {attempt + 1}: {e}")
                
                # If this was the last attempt, fall back to the alternative method
                if attempt == max_retries - 1:
                    logger.info("All Selenium attempts failed. Falling back to requests/BeautifulSoup method")
                    self._use_fallback = True
                    return await self._scrape_frontlines_page_fallback(url)
        
        return advantage_data
    
    async def _scrape_frontlines_page_fallback(self, url: str) -> Dict[str, float]:
        """
        Fallback method to scrape a frontlines page using requests and BeautifulSoup.
        
        Args:
            url (str): The URL of the frontlines page.
        
        Returns:
            Dict[str, float]: Dictionary mapping system names to advantage values.
        """
        advantage_data = {}
        
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Save the raw HTML to a file for debugging
            faction = "amarr" if "amarr" in url else "minmatar"
            timestamp = int(time.time())
            html_file_path = os.path.join(DEBUG_FOLDER, f"{faction}_fallback_{timestamp}.html")
            
            with open(html_file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            logger.info(f"Saved fallback HTML to {html_file_path}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the table with the warzone data
            table = soup.find('table', class_='mantine-WarzoneTable-root')
            
            if table:
                # Process each row in the table
                rows = table.find_all('tr')
                
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
                                logger.debug(f"Scraped advantage for {system_name}: {advantage_value} (fallback)")
                    except Exception as e:
                        logger.error(f"Error processing row (fallback): {e}")
            else:
                logger.warning(f"Could not find warzone table on {url} (fallback)")
                
        except Exception as e:
            logger.error(f"Error scraping {url} with fallback method: {e}")
        
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

# Create a global web scraper instance
web_scraper_selenium = WebScraperSelenium()

def get_web_scraper_selenium() -> WebScraperSelenium:
    """
    Get a web scraper instance.
    
    Returns:
        WebScraperSelenium: A web scraper instance.
    """
    return web_scraper_selenium
