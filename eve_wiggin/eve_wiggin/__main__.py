"""
Main entry point for EVE Wiggin.
"""

import asyncio
import logging
import json
from typing import Dict, Any

from eve_wiggin.api.fw_api import FWApi
from eve_wiggin.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main entry point for the application.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    try:
        # Initialize the API
        fw_api = FWApi()
        
        # Get warzone status
        logger.info("Getting warzone status...")
        warzone_status = await fw_api.get_warzone_status()
        
        # Pretty print the warzone status
        print(json.dumps(warzone_status, indent=2))
        
        # Example: Get details for a specific system (Tama)
        logger.info("Getting system details for Tama...")
        system_details = await fw_api.search_system("Tama")
        
        # Pretty print the system details
        print(json.dumps(system_details, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    asyncio.run(main())

