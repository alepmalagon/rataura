#!/usr/bin/env python3
"""
Debug script to test the web scraper and save HTML files for inspection.
"""

import asyncio
import logging
import os
import sys

# Add the eve_wiggin directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eve_wiggin.api.web_scraper_selenium import get_web_scraper_selenium, DEBUG_FOLDER

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """
    Main function to test the web scraper.
    """
    logger.info(f"Debug folder: {DEBUG_FOLDER}")
    logger.info("Creating debug folder if it doesn't exist...")
    os.makedirs(DEBUG_FOLDER, exist_ok=True)
    
    logger.info("Getting web scraper instance...")
    scraper = get_web_scraper_selenium()
    
    logger.info("Fetching advantage data (force refresh)...")
    advantage_data = await scraper.get_advantage_data(force_refresh=True)
    
    logger.info(f"Fetched advantage data for {len(advantage_data)} systems")
    
    # Print the advantage data
    logger.info("Advantage data:")
    for system_name, advantage in sorted(advantage_data.items()):
        logger.info(f"  {system_name}: {advantage:.2f}")
    
    # List the saved HTML files
    logger.info("Saved HTML files:")
    for filename in os.listdir(DEBUG_FOLDER):
        file_path = os.path.join(DEBUG_FOLDER, filename)
        file_size = os.path.getsize(file_path)
        logger.info(f"  {filename} ({file_size} bytes)")

if __name__ == "__main__":
    asyncio.run(main())

