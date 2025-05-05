"""
Web scraper for EVE Online faction warfare data using Puppeteer via Node.js.

This module uses Node.js and Puppeteer to scrape the EVE Online website for advantage data,
which is not available through the ESI API. Puppeteer is better at handling modern JavaScript-heavy
websites than Selenium in some cases.
"""

import logging
import asyncio
import time
import os
import json
import re
import subprocess
import tempfile
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online Frontlines URL
MINMATAR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/minmatar"
AMARR_FRONTLINES_URL = "https://www.eveonline.com/frontlines/amarr"

# Debug folder for saving raw HTML
DEBUG_FOLDER = "./eve_wiggin/debug_html"

# Puppeteer script template
PUPPETEER_SCRIPT = """
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  // Create debug folder if it doesn't exist
  const debugFolder = '{debug_folder}';
  if (!fs.existsSync(debugFolder)) {{
    fs.mkdirSync(debugFolder, {{ recursive: true }});
  }}

  // Launch browser
  const browser = await puppeteer.launch({{
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  }});
  
  try {{
    const page = await browser.newPage();
    
    // Set viewport size
    await page.setViewport({{ width: 1920, height: 1080 }});
    
    // Set user agent
    await page.setUserAgent('EVE Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)');
    
    console.log(`Navigating to {{url}}...`);
    await page.goto('{url}', {{ waitUntil: 'networkidle2', timeout: 60000 }});
    
    // Wait for initial page load
    await page.waitForSelector('body', {{ timeout: 60000 }});
    
    // Scroll down to trigger lazy loading
    await page.evaluate(() => {{
      window.scrollTo(0, document.body.scrollHeight);
    }});
    
    // Wait a bit for lazy loading to complete
    await page.waitForTimeout(2000);
    
    // Scroll back to top
    await page.evaluate(() => {{
      window.scrollTo(0, 0);
    }});
    
    // Wait for the warzone table to appear
    console.log('Waiting for warzone table to appear...');
    await page.waitForSelector('.mantine-WarzoneTable-root', {{ timeout: 60000 }});
    
    // Wait extra time for the table to fully render
    console.log('Waiting for table to fully render...');
    await page.waitForTimeout(5000);
    
    // Save the page HTML for debugging
    const html = await page.content();
    const faction = '{url}'.includes('amarr') ? 'amarr' : 'minmatar';
    const timestamp = Math.floor(Date.now() / 1000);
    const htmlFilePath = path.join(debugFolder, `${{faction}}_puppeteer_${{timestamp}}.html`);
    fs.writeFileSync(htmlFilePath, html);
    console.log(`Saved HTML to ${{htmlFilePath}}`);
    
    // Extract advantage data from the table
    console.log('Extracting advantage data...');
    const advantageData = await page.evaluate(() => {{
      const data = {{}};
      const table = document.querySelector('.mantine-WarzoneTable-root');
      
      if (!table) {{
        console.error('Could not find warzone table');
        return data;
      }}
      
      const rows = table.querySelectorAll('tr');
      console.log(`Found ${{rows.length}} rows in the table`);
      
      rows.forEach(row => {{
        const systemId = row.getAttribute('id');
        if (!systemId || !systemId.startsWith('solarsystem-')) {{
          return;
        }}
        
        const cells = row.querySelectorAll('td');
        if (cells.length < 5) {{
          return;
        }}
        
        const systemName = cells[0].textContent.trim();
        const advantageCell = cells[4];
        const advantageText = advantageCell.textContent.trim();
        const advantageMatch = advantageText.match(/(\\d+)%/);
        
        if (advantageMatch) {{
          const advantageValue = parseFloat(advantageMatch[1]) / 100.0;
          data[systemName] = advantageValue;
        }}
      }});
      
      return data;
    }});
    
    console.log(`Extracted advantage data for ${{Object.keys(advantageData).length}} systems`);
    
    // Save the advantage data to a JSON file
    const dataFilePath = path.join(debugFolder, `${{faction}}_advantage_data_${{timestamp}}.json`);
    fs.writeFileSync(dataFilePath, JSON.stringify(advantageData, null, 2));
    console.log(`Saved advantage data to ${{dataFilePath}}`);
    
    // Output the data for the Python script to read
    console.log('ADVANTAGE_DATA_START');
    console.log(JSON.stringify(advantageData));
    console.log('ADVANTAGE_DATA_END');
    
  }} catch (error) {{
    console.error(`Error: ${{error.message}}`);
  }} finally {{
    await browser.close();
  }}
}})();
"""

class PuppeteerScraper:
    """
    Scraper for EVE Online faction warfare data using Puppeteer via Node.js.
    """
    
    def __init__(self):
        """
        Initialize the Puppeteer scraper.
        """
        self.user_agent = "EVE Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)"
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
                logger.info(f"Scraping {url} with Puppeteer (attempt {attempt + 1}/{max_retries})")
                
                # Create a temporary file for the Puppeteer script
                with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as script_file:
                    script_path = script_file.name
                    script_content = PUPPETEER_SCRIPT.format(
                        url=url,
                        debug_folder=DEBUG_FOLDER
                    )
                    script_file.write(script_content.encode('utf-8'))
                
                # Run the Puppeteer script
                logger.info(f"Running Puppeteer script from {script_path}")
                process = subprocess.Popen(
                    ['node', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = process.communicate()
                
                # Clean up the temporary script file
                os.unlink(script_path)
                
                # Check for errors
                if process.returncode != 0:
                    logger.error(f"Puppeteer script failed with return code {process.returncode}")
                    logger.error(f"Stderr: {stderr}")
                    
                    if attempt == max_retries - 1:
                        logger.warning("All Puppeteer attempts failed, using default values")
                        return {}
                    
                    continue
                
                # Log the output for debugging
                logger.debug(f"Puppeteer stdout: {stdout}")
                if stderr:
                    logger.warning(f"Puppeteer stderr: {stderr}")
                
                # Extract the advantage data from the output
                advantage_data = self._extract_advantage_data_from_output(stdout)
                
                if advantage_data:
                    logger.info(f"Successfully scraped advantage data for {len(advantage_data)} systems")
                    break
                else:
                    logger.warning(f"No advantage data found in Puppeteer output on attempt {attempt + 1}")
                    
                    if attempt == max_retries - 1:
                        logger.warning("All Puppeteer attempts failed, using default values")
                        return {}
            
            except Exception as e:
                logger.error(f"Error running Puppeteer script on attempt {attempt + 1}: {e}")
                
                if attempt == max_retries - 1:
                    logger.warning("All Puppeteer attempts failed, using default values")
                    return {}
        
        return advantage_data
    
    def _extract_advantage_data_from_output(self, output: str) -> Dict[str, float]:
        """
        Extract advantage data from the Puppeteer script output.
        
        Args:
            output (str): The output from the Puppeteer script.
        
        Returns:
            Dict[str, float]: Dictionary mapping system names to advantage values.
        """
        advantage_data = {}
        
        # Find the advantage data in the output
        start_marker = 'ADVANTAGE_DATA_START'
        end_marker = 'ADVANTAGE_DATA_END'
        
        start_index = output.find(start_marker)
        end_index = output.find(end_marker)
        
        if start_index != -1 and end_index != -1:
            json_str = output[start_index + len(start_marker):end_index].strip()
            
            try:
                advantage_data = json.loads(json_str)
                logger.info(f"Extracted advantage data for {len(advantage_data)} systems from Puppeteer output")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing advantage data JSON: {e}")
                logger.debug(f"JSON string: {json_str}")
        else:
            logger.warning("Could not find advantage data markers in Puppeteer output")
        
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

# Create a global Puppeteer scraper instance
puppeteer_scraper = PuppeteerScraper()

def get_puppeteer_scraper() -> PuppeteerScraper:
    """
    Get a Puppeteer scraper instance.
    
    Returns:
        PuppeteerScraper: A Puppeteer scraper instance.
    """
    return puppeteer_scraper

