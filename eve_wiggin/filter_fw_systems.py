#!/usr/bin/env python3
"""
Script to filter the original pickle file to extract only the Faction Warfare systems
for each warzone and save them to separate pickle files.

This version uses a text file with system names to filter the systems.
"""

import pickle
import os
import logging
from typing import Dict, List, Set, Any, TypedDict

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to solar systems data file
SOLAR_SYSTEMS_FILE = "eve_wiggin/data/solar_systems.pickle"
AMA_MIN_OUTPUT_FILE = "eve_wiggin/data/ama_min.pickle"
CAL_GAL_OUTPUT_FILE = "eve_wiggin/data/cal_gal.pickle"

# Path to the text file containing Amarr/Minmatar system names
AMA_MIN_SYSTEMS_FILE = "eve_wiggin/data/ama_min.txt"


class SolarSystem(TypedDict):
    """Type definition for solar system data."""
    solar_system_name: str
    solar_system_id: str
    region_name: str
    region_id: str
    constellation_name: str
    constellation_id: str
    adjacent: List[str]  # list of all adjacent Solar Systems in the network

def load_solar_systems(filepath: str) -> Dict[int, SolarSystem]:
    """
    Load solar system data from a pickle file.
    
    Args:
        filepath: Path to the pickle file containing solar system data
        
    Returns:
        Dictionary mapping solar system IDs to solar system data
    """
    try:
        logger.info(f"Attempting to load solar system data from {filepath}")
        with open(filepath, 'rb') as f:
            solar_systems = pickle.load(f)
        
        # Log some sample data to verify structure
        if solar_systems:
            sample_key = next(iter(solar_systems))
            logger.info(f"Sample solar system key type: {type(sample_key).__name__}")
            logger.info(f"Sample solar system data structure: {list(solar_systems[sample_key].keys())}")
            
        logger.info(f"Successfully loaded {len(solar_systems)} solar systems from {filepath}")
        return solar_systems
    except FileNotFoundError:
        logger.error(f"Solar system data file not found at {filepath}")
        return {}
    except pickle.UnpicklingError:
        logger.error(f"Error unpickling solar system data from {filepath}. File may be corrupted.")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading solar system data from {filepath}: {e}")
        return {}

def load_system_names_from_file(file_path: str) -> Set[str]:
    """
    Load system names from a text file.
    
    Args:
        file_path (str): Path to the text file containing system names.
        
    Returns:
        Set[str]: Set of system names.
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                # Read each line, strip whitespace, and filter out empty lines
                system_names = {line.strip() for line in f if line.strip()}
            logger.info(f"Loaded {len(system_names)} system names from {file_path}")
            return system_names
        else:
            logger.error(f"System names file not found: {file_path}")
            return set()
    except Exception as e:
        logger.error(f"Error loading system names: {e}", exc_info=True)
        return set()

def filter_systems_by_name(solar_systems: Dict[str, Any], system_names: Set[str]) -> Dict[str, Any]:
    """
    Filter solar systems by name.
    
    Args:
        solar_systems (Dict[str, Any]): The solar systems data.
        system_names (Set[str]): The set of system names to filter by.
    
    Returns:
        Dict[str, Any]: The filtered solar systems data.
    """
    filtered_systems = {}
    
    for system_id, system_data in solar_systems.items():
        system_name = system_data.get("solar_system_name", "")
        logger.info(f"Checking system name: {system_name}")
        if system_name in system_names:
            logger.info(f"System name matches: {system_name}")
            filtered_systems[system_id] = system_data
    
    return filtered_systems

def ensure_connected_systems(solar_systems: Dict[str, Any], filtered_systems: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure that all adjacent systems are included in the filtered systems.
    
    Args:
        solar_systems (Dict[str, Any]): The original solar systems data.
        filtered_systems (Dict[str, Any]): The initially filtered solar systems data.
    
    Returns:
        Dict[str, Any]: The filtered solar systems data with all adjacent systems included.
    """
    result = filtered_systems.copy()
    
    # Keep track of systems to process
    to_process = list(filtered_systems.keys())
    processed = set()
    
    while to_process:
        system_id = to_process.pop(0)
        
        if system_id in processed:
            continue
        
        processed.add(system_id)
        
        # Get the system data
        system_data = solar_systems.get(system_id)
        if not system_data:
            continue
        
        # Get adjacent systems
        adjacent_systems = system_data.get("adjacent", [])
        
        for adjacent_id in adjacent_systems:
            # If the adjacent system is not already in the result, add it
            if adjacent_id not in result and adjacent_id in solar_systems:
                result[adjacent_id] = solar_systems[adjacent_id]
                to_process.append(adjacent_id)
    
    return result

def filter_fw_systems():
    """
    Filter the original pickle file to extract only the Faction Warfare systems
    for each warzone and save them to separate pickle files.
    
    This version uses a text file with system names to filter the systems.
    """
    try:
        # Load solar systems data
        solar_systems = load_solar_systems(SOLAR_SYSTEMS_FILE)
        if not solar_systems:
            logger.error("Failed to load solar systems data")
            return
        
        # Load Amarr/Minmatar system names from text file
        ama_min_system_names = load_system_names_from_file(AMA_MIN_SYSTEMS_FILE)
        logger.info(f"Loaded Amarr/Minmatar system names \n {ama_min_system_names}")
        if not ama_min_system_names:
            logger.error("Failed to load Amarr/Minmatar system names")
            return
        
        # Filter systems for Amarr-Minmatar warzone based on system names
        ama_min_systems = filter_systems_by_name(solar_systems, ama_min_system_names)
        logger.info(f"Filtered {len(ama_min_systems)} systems for Amarr-Minmatar warzone based on system names")
              
        # Save filtered systems to pickle file
        with open(AMA_MIN_OUTPUT_FILE, 'wb') as f:
            pickle.dump(ama_min_systems, f)
        logger.info(f"Saved {len(ama_min_systems)} Amarr-Minmatar systems to {AMA_MIN_OUTPUT_FILE}")
        
        # Print some statistics
        logger.info(f"Original solar systems: {len(solar_systems)}")
        logger.info(f"Amarr-Minmatar systems: {len(ama_min_systems)} ({len(ama_min_systems)/len(solar_systems)*100:.2f}%)")
        
        # Note: We're not handling Caldari-Gallente systems in this version
        # If needed, a similar approach can be used with a separate text file
        
    except Exception as e:
        logger.error(f"Error filtering FW systems: {e}", exc_info=True)

if __name__ == "__main__":
    filter_fw_systems()

