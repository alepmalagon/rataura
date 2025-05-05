"""
Debug script for testing the Selenium-based web scraper.

This script tests the web scraper's ability to fetch advantage data from the EVE Online website
and logs the results for debugging purposes.
"""

import asyncio
import logging
import json
from eve_wiggin.api.web_scraper_selenium import get_web_scraper_selenium

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def debug_advantage_data():
    """
    Debug the Selenium-based web scraper by fetching advantage data from the EVE Online website.
    """
    print("Debugging Selenium-based web scraper...")
    
    # Get web scraper instance
    scraper = get_web_scraper_selenium()
    
    # Get advantage data
    advantage_data = await scraper.get_advantage_data(force_refresh=True)
    
    # Print results
    print(f"Fetched advantage data for {len(advantage_data)} systems")
    
    # Print all data
    print("\nAll advantage data:")
    for system_name, advantage in sorted(advantage_data.items()):
        print(f"{system_name}: {advantage:.2f}")
    
    # Save to a JSON file for reference
    with open('advantage_data.json', 'w') as f:
        json.dump(advantage_data, f, indent=2)
    
    print(f"\nTotal systems: {len(advantage_data)}")
    print(f"Data saved to advantage_data.json")
    
    return advantage_data

if __name__ == "__main__":
    # Run the debug script
    advantage_data = asyncio.run(debug_advantage_data())

