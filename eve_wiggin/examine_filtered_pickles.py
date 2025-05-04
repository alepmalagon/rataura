#!/usr/bin/env python3
"""
Script to examine the filtered pickle files to verify they contain the expected data.
"""

import pickle
import os
import json
import logging
from typing import Dict, Any
from pprint import pformat

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to filtered solar systems data files
AMA_MIN_FILE = "eve_wiggin/data/ama_min.pickle"
CAL_GAL_FILE = "eve_wiggin/data/cal_gal.pickle"

def dump_all_pickle_data(solar_systems: Dict[int, Dict[str, Any]], warzone_name: str):
    """
    Dump all information contained in the pickle file to the logs.
    
    Args:
        solar_systems (Dict[int, Dict[str, Any]]): Dictionary of solar systems.
        warzone_name (str): The name of the warzone.
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"COMPLETE DATA DUMP FOR {warzone_name}")
    logger.info(f"{'='*80}")
    
    # Convert to list of dictionaries for easier reading
    systems_list = []
    for system_id, system_data in solar_systems.items():
        system_copy = system_data.copy()
        system_copy['system_id'] = system_id
        systems_list.append(system_copy)
    
    # Sort by system name for easier reading
    systems_list.sort(key=lambda x: x.get('name', ''))
    
    # Log the complete data
    for i, system in enumerate(systems_list):
        logger.info(f"\nSystem #{i+1}: {system.get('name', 'Unknown')} (ID: {system.get('system_id', 'Unknown')})")
        # Format the system data for better readability
        formatted_data = pformat(system, indent=2, width=100)
        logger.info(formatted_data)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"END OF DATA DUMP FOR {warzone_name}")
    logger.info(f"{'='*80}")

def examine_pickle(file_path: str, warzone_name: str):
    """
    Examine the structure of a filtered pickle file.
    
    Args:
        file_path (str): The path to the pickle file.
        warzone_name (str): The name of the warzone.
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                solar_systems = pickle.load(f)
            
            logger.info(f"Loaded {len(solar_systems)} solar systems from {file_path}")
            
            # Check if the dictionary is empty
            if not solar_systems:
                logger.warning(f"No systems found in {warzone_name}. The pickle file is empty.")
                return
            
            # Get a sample system
            sample_id = next(iter(solar_systems))
            sample_system = solar_systems[sample_id]
            
            logger.info(f"\nSample system structure for {warzone_name}:")
            logger.info(json.dumps(sample_system, indent=2))
            
            # Check how many adjacent systems each system has
            adjacent_counts = {system_id: len(system.get("adjacent", [])) for system_id, system in solar_systems.items()}
            max_adjacent = max(adjacent_counts.values())
            min_adjacent = min(adjacent_counts.values())
            avg_adjacent = sum(adjacent_counts.values()) / len(adjacent_counts)
            
            logger.info(f"\nAdjacent systems statistics for {warzone_name}:")
            logger.info(f"Min: {min_adjacent}, Max: {max_adjacent}, Avg: {avg_adjacent:.2f}")
            
            # Find a system with many adjacent systems
            many_adjacent_id = max(adjacent_counts, key=adjacent_counts.get)
            many_adjacent_system = solar_systems[many_adjacent_id]
            
            logger.info(f"\nSystem with most adjacent systems ({adjacent_counts[many_adjacent_id]}) in {warzone_name}:")
            logger.info(f"Name: {many_adjacent_system.get('name', 'Unknown')}")
            
            # Get adjacent system names
            adjacent_names = []
            for adj_id in many_adjacent_system.get("adjacent", []):
                if adj_id in solar_systems:
                    adjacent_names.append(solar_systems[adj_id].get("name", f"ID: {adj_id}"))
                else:
                    adjacent_names.append(f"ID: {adj_id} (not in filtered systems)")
            
            logger.info(f"Adjacent systems: {', '.join(adjacent_names[:10])}...")
            
            # Check for systems with missing adjacent systems in the filtered data
            missing_adjacents = 0
            for system_id, system in solar_systems.items():
                for adj_id in system.get("adjacent", []):
                    if adj_id not in solar_systems:
                        missing_adjacents += 1
                        break
            
            logger.info(f"\nSystems with missing adjacent systems in {warzone_name}: {missing_adjacents}")
            
            # Check regions
            regions = set()
            for system in solar_systems.values():
                region = system.get("region", "Unknown")
                regions.add(region)
            
            logger.info(f"\nRegions in {warzone_name}: {', '.join(sorted(regions))}")
            
            # Dump all information contained in the pickle file
            dump_all_pickle_data(solar_systems, warzone_name)
            
        else:
            logger.error(f"Solar systems file not found: {file_path}")
    except Exception as e:
        logger.error(f"Error examining pickle file: {e}", exc_info=True)

def main():
    """
    Main function to examine both filtered pickle files.
    """
    try:
        # Examine Amarr-Minmatar pickle
        examine_pickle(AMA_MIN_FILE, "Amarr-Minmatar Warzone")
        
        # Examine Caldari-Gallente pickle
        examine_pickle(CAL_GAL_FILE, "Caldari-Gallente Warzone")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)

if __name__ == "__main__":
    main()
