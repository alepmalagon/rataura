#!/usr/bin/env python3
"""
Debug script to test the Puppeteer web scraper and save HTML files for inspection.
"""

import asyncio
import logging
import os
import sys
import json

# Add the eve_wiggin directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eve_wiggin.api.puppeteer_scraper import get_puppeteer_scraper, DEBUG_FOLDER

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """
    Main function to test the Puppeteer web scraper.
    """
    logger.info(f"Debug folder: {DEBUG_FOLDER}")
    logger.info("Creating debug folder if it doesn't exist...")
    os.makedirs(DEBUG_FOLDER, exist_ok=True)
    
    logger.info("Getting Puppeteer scraper instance...")
    scraper = get_puppeteer_scraper()
    
    logger.info("Fetching advantage data (force refresh)...")
    advantage_data = await scraper.get_advantage_data(force_refresh=True)
    
    logger.info(f"Fetched advantage data for {len(advantage_data)} systems")
    
    # Print the advantage data
    logger.info("Advantage data:")
    for system_name, advantage in sorted(advantage_data.items()):
        logger.info(f"  {system_name}: {advantage:.2f}")
    
    # Save the advantage data to a JSON file
    output_file = os.path.join(DEBUG_FOLDER, "advantage_data_output.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(advantage_data, f, indent=2)
    
    logger.info(f"Saved advantage data to {output_file}")
    
    # List the saved HTML files
    logger.info("Saved HTML files:")
    for filename in os.listdir(DEBUG_FOLDER):
        file_path = os.path.join(DEBUG_FOLDER, filename)
        file_size = os.path.getsize(file_path)
        logger.info(f"  {filename} ({file_size} bytes)")
    
    return advantage_data

if __name__ == "__main__":
    advantage_data = asyncio.run(main())
    
    # Print a summary of the results
    print("\nSummary:")
    print(f"Total systems with advantage data: {len(advantage_data)}")
    
    if advantage_data:
        print("\nSample of advantage data:")
        for system_name, advantage in list(sorted(advantage_data.items()))[:5]:
            print(f"  {system_name}: {advantage:.2f}")

