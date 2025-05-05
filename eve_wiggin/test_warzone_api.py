#!/usr/bin/env python3
"""
Test script for the warzone API client.
"""

import asyncio
import logging
import json
from eve_wiggin.api.warzone_api_client import get_warzone_api_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_warzone_api():
    """
    Test the warzone API client.
    """
    logger.info("Testing warzone API client...")
    
    # Get the warzone API client
    client = get_warzone_api_client()
    
    # Get warzone status data
    logger.info("Getting warzone status data...")
    warzone_data = await client.get_warzone_status(force_refresh=True)
    
    # Log the number of systems
    logger.info(f"Got data for {len(warzone_data)} systems")
    
    # Log the first system as an example
    if warzone_data:
        logger.info(f"Example system data: {json.dumps(warzone_data[0], indent=2)}")
    
    # Get advantage data
    logger.info("Getting advantage data...")
    advantage_data = await client.get_system_advantage_data(force_refresh=True)
    
    # Log the number of systems with advantage data
    logger.info(f"Got advantage data for {len(advantage_data)} systems")
    
    # Log a few examples
    if advantage_data:
        systems = list(advantage_data.keys())
        for i in range(min(5, len(systems))):
            system_name = systems[i]
            system_advantage = advantage_data[system_name]
            logger.info(f"System: {system_name}, Amarr: {system_advantage['amarr']:.2f}, Minmatar: {system_advantage['minmatar']:.2f}, Net: {system_advantage['net_advantage']:.2f}")
    
    return advantage_data

if __name__ == "__main__":
    advantage_data = asyncio.run(test_warzone_api())
    
    # Save the advantage data to a file for reference
    with open("advantage_data.json", "w") as f:
        json.dump(advantage_data, f, indent=2)
    
    logger.info("Saved advantage data to advantage_data.json")

