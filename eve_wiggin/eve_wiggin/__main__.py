"""
Main entry point for EVE Wiggin.
"""

import asyncio
import logging
import json
from typing import Dict, Any

from eve_wiggin.api.fw_api import FWApi
from eve_wiggin.config import settings
from eve_wiggin.models.faction_warfare import Warzone, FactionID

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
        
        # Focus on Amarr/Minmatar warzone
        amarr_minmatar_warzone = warzone_status["warzones"].get(Warzone.AMARR_MINMATAR)
        
        if amarr_minmatar_warzone:
            print("\n=== AMARR/MINMATAR WARZONE STATUS ===")
            print(f"Name: {amarr_minmatar_warzone['name']}")
            print(f"Total Systems: {amarr_minmatar_warzone['total_systems']}")
            
            # Display systems controlled by each faction
            # Convert faction IDs to strings for dictionary lookup
            amarr_systems = amarr_minmatar_warzone['systems'].get(FactionID.AMARR_EMPIRE, 0)
            minmatar_systems = amarr_minmatar_warzone['systems'].get(FactionID.MINMATAR_REPUBLIC, 0)
            
            amarr_percentage = amarr_minmatar_warzone['control_percentages'].get(FactionID.AMARR_EMPIRE, 0)
            minmatar_percentage = amarr_minmatar_warzone['control_percentages'].get(FactionID.MINMATAR_REPUBLIC, 0)
            
            print(f"Amarr Empire: {amarr_systems} systems ({amarr_percentage:.1f}%)")
            print(f"Minmatar Republic: {minmatar_systems} systems ({minmatar_percentage:.1f}%)")
            
            # Display contested systems
            amarr_contested = amarr_minmatar_warzone['contested'].get(FactionID.AMARR_EMPIRE, 0)
            minmatar_contested = amarr_minmatar_warzone['contested'].get(FactionID.MINMATAR_REPUBLIC, 0)
            
            print(f"Contested by Amarr: {amarr_contested} systems")
            print(f"Contested by Minmatar: {minmatar_contested} systems")
            
            # Display faction statistics
            print("\n=== FACTION STATISTICS ===")
            
            amarr_stats = warzone_status["faction_stats"].get(str(FactionID.AMARR_EMPIRE), {})
            minmatar_stats = warzone_status["faction_stats"].get(str(FactionID.MINMATAR_REPUBLIC), {})
            
            if amarr_stats:
                print(f"Amarr Empire:")
                print(f"  Pilots: {amarr_stats.get('pilots', 0)}")
                print(f"  Victory Points (yesterday): {amarr_stats.get('victory_points_yesterday', 0)}")
                print(f"  Kills (yesterday): {amarr_stats.get('kills_yesterday', 0)}")
            
            if minmatar_stats:
                print(f"Minmatar Republic:")
                print(f"  Pilots: {minmatar_stats.get('pilots', 0)}")
                print(f"  Victory Points (yesterday): {minmatar_stats.get('victory_points_yesterday', 0)}")
                print(f"  Kills (yesterday): {minmatar_stats.get('kills_yesterday', 0)}")
        else:
            print("Amarr/Minmatar warzone data not available")
            print(json.dumps(warzone_status, indent=2))
        
        # Example: Get details for a specific system (Huola - an important Amarr/Minmatar warzone system)
        logger.info("Getting system details for Huola...")
        system_details = await fw_api.search_system("Huola")
        
        # Pretty print the system details
        print("\n=== SYSTEM DETAILS: HUOLA ===")
        print(json.dumps(system_details, indent=2))
        
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    asyncio.run(main())
