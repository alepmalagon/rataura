"""
Test script for the web scraper.

This script tests the web scraper's ability to fetch advantage data from the EVE Online website.
"""

import asyncio
import logging
from eve_wiggin.api.web_scraper import get_web_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_web_scraper():
    """
    Test the web scraper by fetching advantage data from the EVE Online website.
    """
    print("Testing web scraper...")
    
    # Get web scraper instance
    scraper = get_web_scraper()
    
    # Get advantage data
    advantage_data = await scraper.get_advantage_data(force_refresh=True)
    
    # Print results
    print(f"Fetched advantage data for {len(advantage_data)} systems")
    
    # Print some sample data
    print("\nSample advantage data:")
    count = 0
    for system_name, advantage in advantage_data.items():
        print(f"{system_name}: {advantage:.2f}")
        count += 1
        if count >= 10:
            break
    
    # Print total number of systems
    print(f"\nTotal systems: {len(advantage_data)}")
    
    return advantage_data

if __name__ == "__main__":
    # Run the test
    advantage_data = asyncio.run(test_web_scraper())

