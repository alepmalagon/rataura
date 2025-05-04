#!/usr/bin/env python3
"""
Script to filter the original pickle file to extract only the Faction Warfare systems
for each warzone and save them to separate pickle files.
"""

import pickle
import os
import logging
from typing import Dict, List, Set, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to solar systems data file
SOLAR_SYSTEMS_FILE = "eve_wiggin/data/solar_systems.pickle"
AMA_MIN_OUTPUT_FILE = "eve_wiggin/data/ama_min.pickle"
CAL_GAL_OUTPUT_FILE = "eve_wiggin/data/cal_gal.pickle"

# Faction IDs
AMARR_EMPIRE = 500003
MINMATAR_REPUBLIC = 500002
CALDARI_STATE = 500001
GALLENTE_FEDERATION = 500004

# Define permanent frontline systems for Amarr-Minmatar warzone
AMARR_PERMANENT_FRONTLINES = {
    "Amamake", "Bosboger", "Auner", "Resbroko", "Evati", "Arnstur"
}

MINMATAR_PERMANENT_FRONTLINES = {
    "Raa", "Kamela", "Sosala", "Huola", "Anka", "Iesa", "Uusanen", "Saikamon", "Halmah"
}

# Define regions for each warzone
# These are approximate and may need adjustment
AMARR_MINMATAR_REGIONS = {
    "Heimatar", "Metropolis", "Molden Heath", "The Bleak Lands", "Devoid", "Domain"
}

CALDARI_GALLENTE_REGIONS = {
    "Black Rise", "The Citadel", "Placid", "Essence", "Verge Vendor"
}

# Define real system names for the mock data
# This mapping will replace the generic "Amarr System n" and "Minmatar System n" names
SYSTEM_NAME_MAPPING = {
    # Amarr systems (30003100-30003129)
    "30003100": "Kurniainen",
    "30003101": "Saidusairos",
    "30003102": "Vaajaita",
    "30003103": "Tannakan",
    "30003104": "Komaa",
    "30003105": "Ayeroilen",
    "30003106": "Imata",
    "30003107": "Furskeshin",
    "30003108": "Kurmaru",
    "30003109": "Satalama",
    "30003110": "Ashokon",
    "30003111": "Mara",
    "30003112": "Lasleinur",
    "30003113": "Ofstold",
    "30003114": "Todifrauan",
    "30003115": "Helgatild",
    "30003116": "Arnstur",
    "30003117": "Lasleinur",
    "30003118": "Stoure",
    "30003119": "Gehi",
    "30003120": "Eszur",
    "30003121": "Hadozeko",
    "30003122": "Youl",
    "30003123": "Anka",
    "30003124": "Iesa",
    "30003125": "Netsalakka",
    "30003126": "Sasiekko",
    "30003127": "Myyhera",
    "30003128": "Gammel",
    "30003129": "Uusanen",
    
    # Minmatar systems (30002600-30002629)
    "30002600": "Abudban",
    "30002601": "Trytedald",
    "30002602": "Odatrik",
    "30002603": "Rens",
    "30002604": "Ameinaka",
    "30002605": "Alakgur",
    "30002606": "Dammalin",
    "30002607": "Bosena",
    "30002608": "Gulmorogod",
    "30002609": "Lulm",
    "30002610": "Kronsur",
    "30002611": "Dumkirinur",
    "30002612": "Sist",
    "30002613": "Obrolber",
    "30002614": "Austraka",
    "30002615": "Ivar",
    "30002616": "Meirakulf",
    "30002617": "Frarn",
    "30002618": "Illinfrik",
    "30002619": "Bosboger",
    "30002620": "Larkugei",
    "30002621": "Ebasgerdur",
    "30002622": "Hek",
    "30002623": "Hror",
    "30002624": "Ingunn",
    "30002625": "Tvink",
    "30002626": "Lanngisi",
    "30002627": "Eystur",
    "30002628": "Nakugard",
    "30002629": "Hrokkur"
}

def load_solar_systems() -> Dict[str, Any]:
    """
    Load solar systems data from pickle file.
    
    Returns:
        Dict[str, Any]: The solar systems data.
    """
    try:
        if os.path.exists(SOLAR_SYSTEMS_FILE):
            with open(SOLAR_SYSTEMS_FILE, 'rb') as f:
                solar_systems = pickle.load(f)
            logger.info(f"Loaded {len(solar_systems)} solar systems from {SOLAR_SYSTEMS_FILE}")
            return solar_systems
        else:
            logger.error(f"Solar systems file not found: {SOLAR_SYSTEMS_FILE}")
            return {}
    except Exception as e:
        logger.error(f"Error loading solar systems data: {e}", exc_info=True)
        return {}

def filter_systems_by_region(solar_systems: Dict[str, Any], regions: Set[str]) -> Dict[str, Any]:
    """
    Filter solar systems by region.
    
    Args:
        solar_systems (Dict[str, Any]): The solar systems data.
        regions (Set[str]): The set of region names to filter by.
    
    Returns:
        Dict[str, Any]: The filtered solar systems data.
    """
    filtered_systems = {}
    
    for system_id, system_data in solar_systems.items():
        region_name = system_data.get("region", "")
        if region_name in regions:
            filtered_systems[system_id] = system_data
    
    return filtered_systems

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
        system_name = system_data.get("name", "")
        if system_name in system_names:
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

def apply_real_system_names(systems: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply real system names to the systems data.
    
    Args:
        systems (Dict[str, Any]): The systems data.
    
    Returns:
        Dict[str, Any]: The systems data with real system names.
    """
    result = systems.copy()
    
    for system_id, system_data in result.items():
        # Check if this system has a generic name (Amarr System n or Minmatar System n)
        current_name = system_data.get("name", "")
        if current_name.startswith("Amarr System ") or current_name.startswith("Minmatar System "):
            # If we have a real name for this system, use it
            if system_id in SYSTEM_NAME_MAPPING:
                system_data["name"] = SYSTEM_NAME_MAPPING[system_id]
                logger.info(f"Renamed system {system_id} from '{current_name}' to '{SYSTEM_NAME_MAPPING[system_id]}'")
    
    return result

def filter_fw_systems():
    """
    Filter the original pickle file to extract only the Faction Warfare systems
    for each warzone and save them to separate pickle files.
    """
    try:
        # Load solar systems data
        solar_systems = load_solar_systems()
        if not solar_systems:
            logger.error("Failed to load solar systems data")
            return
        
        # Filter systems for Amarr-Minmatar warzone
        ama_min_systems = filter_systems_by_region(solar_systems, AMARR_MINMATAR_REGIONS)
        
        # Add permanent frontline systems if they're not already included
        frontline_systems = filter_systems_by_name(solar_systems, 
                                                 AMARR_PERMANENT_FRONTLINES.union(MINMATAR_PERMANENT_FRONTLINES))
        for system_id, system_data in frontline_systems.items():
            if system_id not in ama_min_systems:
                ama_min_systems[system_id] = system_data
        
        # Ensure all connected systems are included
        ama_min_systems = ensure_connected_systems(solar_systems, ama_min_systems)
        
        # Apply real system names to replace generic names
        ama_min_systems = apply_real_system_names(ama_min_systems)
        
        # Filter systems for Caldari-Gallente warzone
        cal_gal_systems = filter_systems_by_region(solar_systems, CALDARI_GALLENTE_REGIONS)
        
        # Ensure all connected systems are included
        cal_gal_systems = ensure_connected_systems(solar_systems, cal_gal_systems)
        
        # Apply real system names to replace generic names
        cal_gal_systems = apply_real_system_names(cal_gal_systems)
        
        # Save filtered systems to pickle files
        with open(AMA_MIN_OUTPUT_FILE, 'wb') as f:
            pickle.dump(ama_min_systems, f)
        logger.info(f"Saved {len(ama_min_systems)} Amarr-Minmatar systems to {AMA_MIN_OUTPUT_FILE}")
        
        with open(CAL_GAL_OUTPUT_FILE, 'wb') as f:
            pickle.dump(cal_gal_systems, f)
        logger.info(f"Saved {len(cal_gal_systems)} Caldari-Gallente systems to {CAL_GAL_OUTPUT_FILE}")
        
        # Print some statistics
        logger.info(f"Original solar systems: {len(solar_systems)}")
        logger.info(f"Amarr-Minmatar systems: {len(ama_min_systems)} ({len(ama_min_systems)/len(solar_systems)*100:.2f}%)")
        logger.info(f"Caldari-Gallente systems: {len(cal_gal_systems)} ({len(cal_gal_systems)/len(solar_systems)*100:.2f}%)")
        
    except Exception as e:
        logger.error(f"Error filtering FW systems: {e}", exc_info=True)

if __name__ == "__main__":
    filter_fw_systems()
