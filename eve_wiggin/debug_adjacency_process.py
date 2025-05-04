#!/usr/bin/env python3
"""
Debug Adjacency Process for EVE Wiggin.

This script provides detailed logging of the entire adjacency determination process,
showing how each system's adjacency is calculated and why some systems might not be
getting their adjacency correctly assigned.
"""

import asyncio
import logging
import os
import sys

# Add the parent directory to the path so we can import the eve_wiggin package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eve_wiggin.services.fw_graph_builder import get_fw_graph_builder
from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency

async def debug_adjacency_process():
    """
    Run a detailed debug of the adjacency determination process.
    """
    try:
        # Configure logging to show DEBUG level messages
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        
        # Set the fw_graph_builder logger to DEBUG level
        logging.getLogger('eve_wiggin.services.fw_graph_builder').setLevel(logging.DEBUG)
        
        # Get the graph builder
        graph_builder = get_fw_graph_builder()
        
        # Build the warzone graph with detailed logging
        print("Building warzone graph with detailed logging...")
        graph = await graph_builder.build_warzone_graph()
        
        # Print summary statistics
        print("\n=== ADJACENCY DETERMINATION SUMMARY ===")
        
        # Count systems by faction and adjacency
        total_systems = graph.number_of_nodes()
        amarr_systems = sum(1 for _, data in graph.nodes(data=True) 
                           if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE)
        minmatar_systems = sum(1 for _, data in graph.nodes(data=True) 
                              if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC)
        neutral_systems = total_systems - amarr_systems - minmatar_systems
        
        frontlines = sum(1 for _, data in graph.nodes(data=True) 
                        if data.get("adjacency") == SystemAdjacency.FRONTLINE)
        command_ops = sum(1 for _, data in graph.nodes(data=True) 
                         if data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        rearguards = sum(1 for _, data in graph.nodes(data=True) 
                        if data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        amarr_frontlines = sum(1 for _, data in graph.nodes(data=True) 
                              if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE and
                              data.get("adjacency") == SystemAdjacency.FRONTLINE)
        amarr_command_ops = sum(1 for _, data in graph.nodes(data=True) 
                               if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE and
                               data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        amarr_rearguards = sum(1 for _, data in graph.nodes(data=True) 
                              if data.get("occupier_faction_id") == FactionID.AMARR_EMPIRE and
                              data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        minmatar_frontlines = sum(1 for _, data in graph.nodes(data=True) 
                                 if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC and
                                 data.get("adjacency") == SystemAdjacency.FRONTLINE)
        minmatar_command_ops = sum(1 for _, data in graph.nodes(data=True) 
                                  if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC and
                                  data.get("adjacency") == SystemAdjacency.COMMAND_OPERATIONS)
        minmatar_rearguards = sum(1 for _, data in graph.nodes(data=True) 
                                 if data.get("occupier_faction_id") == FactionID.MINMATAR_REPUBLIC and
                                 data.get("adjacency") == SystemAdjacency.REARGUARD)
        
        print(f"Total systems: {total_systems}")
        print(f"  - Amarr systems: {amarr_systems}")
        print(f"  - Minmatar systems: {minmatar_systems}")
        print(f"  - Neutral systems: {neutral_systems}")
        print(f"Total frontlines: {frontlines}")
        print(f"  - Amarr frontlines: {amarr_frontlines}")
        print(f"  - Minmatar frontlines: {minmatar_frontlines}")
        print(f"Total command ops: {command_ops}")
        print(f"  - Amarr command ops: {amarr_command_ops}")
        print(f"  - Minmatar command ops: {minmatar_command_ops}")
        print(f"Total rearguards: {rearguards}")
        print(f"  - Amarr rearguards: {amarr_rearguards}")
        print(f"  - Minmatar rearguards: {minmatar_rearguards}")
        
        # Check for systems that should be frontlines but aren't
        print("\n=== POTENTIAL MISSED FRONTLINES ===")
        potential_frontlines = []
        
        for system_id, data in graph.nodes(data=True):
            if data.get("adjacency") != SystemAdjacency.FRONTLINE:
                system_name = data.get("solar_system_name", "")
                occupier_faction_id = data.get("occupier_faction_id", 0)
                
                # Skip systems with no faction
                if occupier_faction_id == 0:
                    continue
                
                # Check if this system has neighbors of the enemy faction
                neighbors = list(graph.neighbors(system_id))
                enemy_neighbors = []
                
                for neighbor_id in neighbors:
                    neighbor_data = graph.nodes[neighbor_id]
                    neighbor_name = neighbor_data.get("solar_system_name", "")
                    neighbor_faction = neighbor_data.get("occupier_faction_id", 0)
                    
                    # Check if this is an enemy system
                    is_enemy = False
                    if occupier_faction_id == FactionID.AMARR_EMPIRE and neighbor_faction == FactionID.MINMATAR_REPUBLIC:
                        is_enemy = True
                        enemy_neighbors.append(neighbor_name)
                    elif occupier_faction_id == FactionID.MINMATAR_REPUBLIC and neighbor_faction == FactionID.AMARR_EMPIRE:
                        is_enemy = True
                        enemy_neighbors.append(neighbor_name)
                
                if enemy_neighbors:
                    faction_name = "Amarr" if occupier_faction_id == FactionID.AMARR_EMPIRE else "Minmatar"
                    print(f"System {system_name} ({faction_name}) should be a frontline!")
                    print(f"  - Adjacent to enemy systems: {', '.join(enemy_neighbors)}")
                    print(f"  - Current adjacency: {data.get('adjacency')}")
                    potential_frontlines.append(system_name)
        
        if not potential_frontlines:
            print("No potential missed frontlines found.")
        
        print("\n=== DEBUG COMPLETE ===")
        
    except Exception as e:
        logging.error(f"Error debugging adjacency process: {e}", exc_info=True)

if __name__ == "__main__":
    # Run the async function
    asyncio.run(debug_adjacency_process())

