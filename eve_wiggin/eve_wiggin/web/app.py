"""
Flask application for EVE Wiggin.
"""

import logging
import asyncio
import json
import os
import pickle
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin

from eve_wiggin.api.fw_api import FWApi
from eve_wiggin.models.faction_warfare import Warzone, FactionID
from eve_wiggin.web.web_visualizer import WebVisualizer
from eve_wiggin.services.adjacency_detector import SOLAR_SYSTEMS_FILE
from eve_wiggin.graph_utils import load_pickle_to_dict, get_warzone_graph, analyze_graph

# Define paths to filtered pickle files
AMA_MIN_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ama_min.pickle")
CAL_GAL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cal_gal.pickle")

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Initialize API and visualizer
fw_api = None
visualizer = WebVisualizer()

CORS(app)

def init_api():
    """Initialize the FW API."""
    global fw_api
    if fw_api is None:
        fw_api = FWApi()


@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
async def analyze():
    """
    Run the EVE Wiggin analysis and return the results.
    """
    try:
        # Initialize API if needed
        init_api()
        
        # Get parameters from request
        data = request.json or {}
        warzone_key = data.get('warzone', 'amarr_minmatar')
        sort_by = data.get('sort', 'name')
        system_name = data.get('system')
        
        # Reset visualizer output
        visualizer.reset_output()
        
        # If a specific system was requested
        if system_name:
            logger.info(f"Getting system details for {system_name}...")
            system_details = await fw_api.search_system(system_name)
            
            if "error" in system_details:
                return jsonify({"error": system_details["error"]})
            else:
                visualizer.display_system_details(system_details)
                return jsonify({"html": visualizer.get_html()})
        
        # Get warzone status
        logger.info("Getting warzone status...")
        warzone_status = await fw_api.get_warzone_status()
        
        # Focus on the selected warzone
        warzone_enum = getattr(Warzone, warzone_key.upper())
        warzone_data = warzone_status["warzones"].get(warzone_enum)
        
        if warzone_data:
            # Display warzone summary
            visualizer.display_warzone_summary(warzone_data)
            
            # Display faction statistics
            faction_stats = {}
            for faction_id in warzone_data["factions"]:
                # Convert faction_id to string for dictionary lookup
                faction_id_str = str(faction_id)
                
                # Get faction stats from warzone_status
                if faction_id in warzone_status["faction_stats"]:
                    faction_stats[faction_id_str] = warzone_status["faction_stats"][faction_id]
                else:
                    # If faction stats not found, create empty stats
                    logger.warning(f"No faction stats found for faction ID {faction_id}")
                    faction_stats[faction_id_str] = {
                        "faction_id": faction_id,
                        "pilots": 0,
                        "systems_controlled": 0,
                        "kills_yesterday": 0,
                        "kills_last_week": 0,
                        "kills_total": 0,
                        "victory_points_yesterday": 0,
                        "victory_points_last_week": 0,
                        "victory_points_total": 0
                    }
            
            visualizer.display_faction_stats(faction_stats)
            
            # Get and display all systems in the warzone
            logger.info(f"Getting systems for {warzone_key} warzone...")
            warzone_systems = await fw_api.get_warzone_systems(warzone_enum)
            
            # Display systems table
            visualizer.display_systems_table(warzone_systems, sort_by=sort_by)
            
            return jsonify({"html": visualizer.get_html()})
        else:
            return jsonify({"error": f"Warzone data not available for {warzone_key}"})
    
    except Exception as e:
        logger.error(f"Error in analyze: {e}", exc_info=True)
        return jsonify({"error": str(e)})


@app.route('/api/graph', methods=['POST'])
async def get_graph_data():
    """
    Get graph data for faction warfare systems.
    """
    try:
        # Initialize API if needed
        init_api()
        
        # Get parameters from request
        data = request.json or {}
        warzone_key = data.get('warzone', 'amarr_minmatar')
        filter_type = data.get('filter', 'all')
        
        # Get warzone status
        logger.info("Getting warzone status for graph...")
        warzone_status = await fw_api.get_warzone_status()
        
        # Focus on the selected warzone
        warzone_enum = getattr(Warzone, warzone_key.upper())
        warzone_data = warzone_status["warzones"].get(warzone_enum)
        
        if not warzone_data:
            return jsonify({"error": f"Warzone data not available for {warzone_key}"})
        
        # Get systems in the warzone
        logger.info(f"Getting systems for {warzone_key} warzone graph...")
        warzone_systems = await fw_api.get_warzone_systems(warzone_enum)
        
        # Generate graph data using the new approach
        try:
            # Get the NetworkX graph for the warzone
            graph, system_name_to_index, systems_data = get_warzone_graph(warzone_key)
            
            # Enrich warzone_systems with capture effort data from the graph
            for system in warzone_systems:
                system_name = system["system_info"]["name"]
                
                # Find the corresponding node in the graph
                for node in graph.nodes:
                    if graph.nodes[node].get("solar_system_name") == system_name:
                        # Copy capture effort data to the warzone system
                        system["system"]["capture_effort"] = graph.nodes[node].get("capture_effort", 0.0)
                        system["system"]["capture_effort_category"] = graph.nodes[node].get("capture_effort_category", "Unknown")
                        break
            
            # Generate graph data for visualization
            graph_data = visualizer.generate_graph_data(warzone_systems, systems_data, filter_type)
            
            # Add graph metrics to the response
            metrics = analyze_graph(graph)
            graph_data["metrics"] = metrics
            
            return jsonify(graph_data)
            
        except Exception as e:
            logger.error(f"Error generating graph data: {e}", exc_info=True)
            
            # Fall back to the original approach if the new one fails
            logger.warning("Falling back to original graph generation approach")
            
            # Load solar systems data from the appropriate filtered pickle file
            solar_systems = {}
            try:
                # Select the appropriate pickle file based on the warzone
                if warzone_key == 'amarr_minmatar':
                    pickle_file = AMA_MIN_FILE
                else:
                    pickle_file = CAL_GAL_FILE
                    
                if os.path.exists(pickle_file):
                    with open(pickle_file, 'rb') as f:
                        solar_systems = pickle.load(f)
                    logger.info(f"Loaded {len(solar_systems)} solar systems from {pickle_file}")
                else:
                    logger.warning(f"Filtered pickle file not found: {pickle_file}, falling back to original")
                    # Fall back to the original pickle file
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
        return jsonify({"error": str(e)})


@app.route('/api/pickle_data', methods=['GET'])
def get_pickle_data():
    """
    Get the raw data from the pickle file as a list of dictionaries.
    """
    try:
        # Get parameters from request
        warzone_key = request.args.get('warzone', 'amarr_minmatar')
        
        # Select the appropriate pickle file
        if warzone_key == 'amarr_minmatar':
            pickle_file = AMA_MIN_FILE
        else:
            pickle_file = CAL_GAL_FILE
        
        # Load the pickle file into a list of dictionaries
        systems_data = load_pickle_to_dict(pickle_file)
        
        # Return the data as JSON
        return jsonify({
            "warzone": warzone_key,
            "systems_count": len(systems_data),
            "systems": systems_data
        })
    
    except Exception as e:
        logger.error(f"Error in get_pickle_data: {e}", exc_info=True)
        return jsonify({"error": str(e)})


@app.route('/api/graph_metrics', methods=['GET'])
def get_graph_metrics():
    """
    Get metrics about the warzone graph.
    """
    try:
        # Get parameters from request
        warzone_key = request.args.get('warzone', 'amarr_minmatar')
        
        # Get the NetworkX graph for the warzone
        graph, system_name_to_index, systems_data = get_warzone_graph(warzone_key)
        
        # Analyze the graph
        metrics = analyze_graph(graph)
        
        # Return the metrics as JSON
        return jsonify({
            "warzone": warzone_key,
            "metrics": metrics
        })
    
    except Exception as e:
        logger.error(f"Error in get_graph_metrics: {e}", exc_info=True)
        return jsonify({"error": str(e)})


@app.route('/api/node_positions', methods=['GET', 'POST'])
def handle_node_positions():
    """
    Store or retrieve node positions for the graph.
    
    GET: Retrieve saved node positions for a warzone
    POST: Save node positions for a warzone
    """
    try:
        # Get warzone from request
        warzone_key = request.args.get('warzone', 'amarr_minmatar')
        
        # Define the path to the positions file
        positions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "positions")
        os.makedirs(positions_dir, exist_ok=True)
        positions_file = os.path.join(positions_dir, f"{warzone_key}_positions.json")
        
        if request.method == 'GET':
            # Retrieve saved positions
            if os.path.exists(positions_file):
                with open(positions_file, 'r') as f:
                    positions = json.load(f)
                return jsonify({"positions": positions})
            else:
                # Check if default positions exist
                default_positions_file = os.path.join(positions_dir, f"{warzone_key}_default_positions.json")
                if os.path.exists(default_positions_file):
                    with open(default_positions_file, 'r') as f:
                        positions = json.load(f)
                    return jsonify({"positions": positions})
                return jsonify({"positions": {}})
        
        elif request.method == 'POST':
            # Save positions
            positions = request.json.get('positions', {})
            with open(positions_file, 'w') as f:
                json.dump(positions, f)
            return jsonify({"success": True, "message": "Positions saved successfully"})
    
    except Exception as e:
        logger.error(f"Error handling node positions: {e}", exc_info=True)
        return jsonify({"error": str(e)})


@app.route('/api/default_node_positions', methods=['GET', 'POST'])
def handle_default_node_positions():
    """
    Store or retrieve default node positions for the graph.
    
    GET: Retrieve saved default node positions for a warzone
    POST: Save current node positions as default for all users
    """
    try:
        # Get warzone from request
        warzone_key = request.args.get('warzone', 'amarr_minmatar')
        
        # Define the path to the default positions file
        positions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "positions")
        os.makedirs(positions_dir, exist_ok=True)
        default_positions_file = os.path.join(positions_dir, f"{warzone_key}_default_positions.json")
        
        if request.method == 'GET':
            # Retrieve saved default positions
            if os.path.exists(default_positions_file):
                with open(default_positions_file, 'r') as f:
                    positions = json.load(f)
                return jsonify({"positions": positions})
            else:
                return jsonify({"positions": {}})
        
        elif request.method == 'POST':
            # Save current positions as default
            positions = request.json.get('positions', {})
            with open(default_positions_file, 'w') as f:
                json.dump(positions, f)
            return jsonify({"success": True, "message": "Default positions saved successfully"})
    
    except Exception as e:
        logger.error(f"Error handling default node positions: {e}", exc_info=True)
        return jsonify({"error": str(e)})


@app.route('/api/systems/<system_id>')
@cross_origin()
async def get_system(system_id):
    """
    Get details for a specific system.
    """
    try:
        # Get the NetworkX graph for the warzone
        graph = await get_graph()
        
        # Find the system in the graph
        for node in graph.nodes:
            if str(graph.nodes[node].get('solar_system_id')) == system_id:
                system_data = dict(graph.nodes[node])
                
                # Add additional data
                system_data['node_id'] = node
                
                # Format numeric values
                if 'amarr_advantage' in system_data:
                    system_data['amarr_advantage'] = round(system_data['amarr_advantage'], 2)
                if 'minmatar_advantage' in system_data:
                    system_data['minmatar_advantage'] = round(system_data['minmatar_advantage'], 2)
                if 'net_advantage' in system_data:
                    system_data['net_advantage'] = round(system_data['net_advantage'], 2)
                if 'capture_effort' in system_data:
                    system_data['capture_effort'] = round(system_data['capture_effort'], 2)
                
                # Get adjacent systems
                adjacent_systems = []
                for neighbor in graph.neighbors(node):
                    adjacent_systems.append({
                        'id': str(graph.nodes[neighbor].get('solar_system_id')),
                        'name': graph.nodes[neighbor].get('solar_system_name'),
                        'occupier_faction_id': graph.nodes[neighbor].get('occupier_faction_id')
                    })
                
                system_data['adjacent_systems'] = adjacent_systems
                
                return jsonify(system_data)
        
        # If system not found
        return jsonify({'error': f'System with ID {system_id} not found'}), 404
    
    except Exception as e:
        logger.error(f"Error getting system details: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def run_app(host='0.0.0.0', port=5000, debug=False):
    """
    Run the Flask application.
    
    Args:
        host (str, optional): The host to run on. Defaults to '0.0.0.0'.
        port (int, optional): The port to run on. Defaults to 5000.
        debug (bool, optional): Whether to run in debug mode. Defaults to False.
    """
    app.run(host=host, port=port, debug=debug)
