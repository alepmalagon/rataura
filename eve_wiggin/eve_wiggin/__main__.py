"""
Main entry point for EVE Wiggin.
"""

import asyncio
import logging
import json
import argparse
from typing import Dict, Any

from eve_wiggin.api.fw_api import FWApi
from eve_wiggin.config import settings
from eve_wiggin.models.faction_warfare import Warzone, FactionID
from eve_wiggin.visualization.console import ConsoleVisualizer

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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="EVE Wiggin - Faction Warfare Analysis Tool")
    parser.add_argument("--system", help="Display details for a specific system")
    parser.add_argument("--sort", choices=["name", "security", "contest", "region"], default="name",
                        help="Sort systems by this field")
    parser.add_argument("--warzone", choices=["amarr_minmatar", "caldari_gallente"], default="amarr_minmatar",
                        help="Warzone to analyze")
    parser.add_argument("--full", action="store_true", help="Display full system details")
    args = parser.parse_args()
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    try:
        # Initialize the API and visualizer
        fw_api = FWApi()
        visualizer = ConsoleVisualizer()
        
        # If a specific system was requested
        if args.system:
            logger.info(f"Getting system details for {args.system}...")
            system_details = await fw_api.search_system(args.system)
            
            if "error" in system_details:
                print(f"Error: {system_details['error']}")
            else:
                visualizer.display_system_details(system_details)
            
            return
        
        # Get warzone status
        logger.info("Getting warzone status...")
        warzone_status = await fw_api.get_warzone_status()
        
        # Focus on the selected warzone
        warzone_key = getattr(Warzone, args.warzone.upper())
        warzone_data = warzone_status["warzones"].get(warzone_key)
        
        if warzone_data:
            # Display warzone summary
            visualizer.display_warzone_summary(warzone_data)
            
            # Display faction statistics
            faction_stats = {}
            for faction_id in warzone_data["factions"]:
                faction_stats[str(faction_id)] = warzone_status["faction_stats"].get(str(faction_id), {})
            
            visualizer.display_faction_stats(faction_stats)
            
            # Get and display all systems in the warzone
            logger.info(f"Getting systems for {args.warzone} warzone...")
            warzone_systems = await fw_api.get_warzone_systems(warzone_key)
            
            # Display systems table
            visualizer.display_systems_table(warzone_systems, sort_by=args.sort)
            
            # If full details requested, display details for each system
            if args.full:
                for system in warzone_systems:
                    visualizer.display_system_details(system)
        else:
            print(f"Warzone data not available for {args.warzone}")
            print(json.dumps(warzone_status, indent=2))
    
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    asyncio.run(main())
