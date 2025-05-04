#!/usr/bin/env python3
"""
Script to update the web visualizer to use the filtered pickle files instead of the original one.
"""

import os
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path to web app file
APP_FILE = "eve_wiggin/eve_wiggin/web/app.py"
APP_BACKUP = "eve_wiggin/eve_wiggin/web/app.py.bak"

# Path to web visualizer file
VISUALIZER_FILE = "eve_wiggin/eve_wiggin/web/web_visualizer.py"
VISUALIZER_BACKUP = "eve_wiggin/eve_wiggin/web/web_visualizer.py.bak"

def update_app_file():
    """
    Update the app.py file to use the filtered pickle files.
    """
    try:
        # Create a backup of the original file
        shutil.copy2(APP_FILE, APP_BACKUP)
        logger.info(f"Created backup of {APP_FILE} at {APP_BACKUP}")
        
        # Read the original file
        with open(APP_FILE, 'r') as f:
            content = f.read()
        
        # Update the imports
        new_imports = """import os
import pickle
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from eve_wiggin.api.fw_api import get_fw_api
from eve_wiggin.models.faction_warfare import SystemAdjacency, SystemStatus, Warzone
from eve_wiggin.web.web_visualizer import WebVisualizer

# Path to solar systems data files
from eve_wiggin.services.adjacency_detector import SOLAR_SYSTEMS_FILE
AMA_MIN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ama_min.pickle")
CAL_GAL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cal_gal.pickle")
"""
        
        # Replace the imports
        content = content.replace("""import os
import pickle
import logging
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from eve_wiggin.api.fw_api import get_fw_api
from eve_wiggin.models.faction_warfare import SystemAdjacency, SystemStatus, Warzone
from eve_wiggin.web.web_visualizer import WebVisualizer

# Path to solar systems data file
from eve_wiggin.services.adjacency_detector import SOLAR_SYSTEMS_FILE""", new_imports)
        
        # Update the get_graph_data function
        old_graph_data = """@app.route('/api/graph_data', methods=['GET'])
@cross_origin()
def get_graph_data():
    \"\"\"
    Get graph data for faction warfare systems.
    \"\"\"
    try:
        # Get query parameters
        warzone = request.args.get('warzone', 'amarr_minmatar')
        filter_type = request.args.get('filter', 'all')
        
        # Get warzone systems
        warzone_systems = []
        if warzone == 'amarr_minmatar':
            warzone_systems = fw_api.get_warzone_systems(Warzone.AMARR_MINMATAR)
        elif warzone == 'caldari_gallente':
            warzone_systems = fw_api.get_warzone_systems(Warzone.CALDARI_GALLENTE)
        
        # Load solar systems data from pickle file
        solar_systems = {}
        try:
            if os.path.exists(SOLAR_SYSTEMS_FILE):
                with open(SOLAR_SYSTEMS_FILE, 'rb') as f:
                    solar_systems = pickle.load(f)
                logger.info(f"Loaded {len(solar_systems)} solar systems from {SOLAR_SYSTEMS_FILE}")
            else:
                logger.warning(f"Solar systems file not found: {SOLAR_SYSTEMS_FILE}")
        except Exception as e:
            logger.error(f"Error loading solar systems data: {e}", exc_info=True)
            return jsonify({"error": f"Error loading solar systems data: {str(e)}"})
        
        # Generate graph data
        graph_data = visualizer.generate_graph_data(warzone_systems, solar_systems, filter_type)
        
        return jsonify(graph_data)
    
    except Exception as e:
        logger.error(f"Error in get_graph_data: {e}", exc_info=True)
        return jsonify({"error": str(e)})"""
        
        new_graph_data = """@app.route('/api/graph_data', methods=['GET'])
@cross_origin()
def get_graph_data():
    \"\"\"
    Get graph data for faction warfare systems.
    \"\"\"
    try:
        # Get query parameters
        warzone = request.args.get('warzone', 'amarr_minmatar')
        filter_type = request.args.get('filter', 'all')
        
        # Get warzone systems
        warzone_systems = []
        if warzone == 'amarr_minmatar':
            warzone_systems = fw_api.get_warzone_systems(Warzone.AMARR_MINMATAR)
            pickle_file = AMA_MIN_FILE
        elif warzone == 'caldari_gallente':
            warzone_systems = fw_api.get_warzone_systems(Warzone.CALDARI_GALLENTE)
            pickle_file = CAL_GAL_FILE
        else:
            return jsonify({"error": f"Invalid warzone: {warzone}"})
        
        # Load solar systems data from the appropriate pickle file
        solar_systems = {}
        try:
            if os.path.exists(pickle_file):
                with open(pickle_file, 'rb') as f:
                    solar_systems = pickle.load(f)
                logger.info(f"Loaded {len(solar_systems)} solar systems from {pickle_file}")
            else:
                logger.warning(f"Solar systems file not found: {pickle_file}")
                # Fall back to the original pickle file
                if os.path.exists(SOLAR_SYSTEMS_FILE):
                    with open(SOLAR_SYSTEMS_FILE, 'rb') as f:
                        solar_systems = pickle.load(f)
                    logger.info(f"Loaded {len(solar_systems)} solar systems from {SOLAR_SYSTEMS_FILE} (fallback)")
                else:
                    logger.warning(f"Fallback solar systems file not found: {SOLAR_SYSTEMS_FILE}")
        except Exception as e:
            logger.error(f"Error loading solar systems data: {e}", exc_info=True)
            return jsonify({"error": f"Error loading solar systems data: {str(e)}"})
        
        # Generate graph data
        graph_data = visualizer.generate_graph_data(warzone_systems, solar_systems, filter_type)
        
        return jsonify(graph_data)
    
    except Exception as e:
        logger.error(f"Error in get_graph_data: {e}", exc_info=True)
        return jsonify({"error": str(e)})"""
        
        # Replace the get_graph_data function
        content = content.replace(old_graph_data, new_graph_data)
        
        # Write the updated content back to the file
        with open(APP_FILE, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated {APP_FILE} to use filtered pickle files")
        
    except Exception as e:
        logger.error(f"Error updating app file: {e}", exc_info=True)

def main():
    """
    Main function to update the web visualizer.
    """
    try:
        # Update the app.py file
        update_app_file()
        
    except Exception as e:
        logger.error(f"Error in main function: {e}", exc_info=True)

if __name__ == "__main__":
    main()

