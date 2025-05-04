import pickle
import os
import json

# Path to solar systems data file
SOLAR_SYSTEMS_FILE = "eve_wiggin/eve_wiggin/data/solar_systems.pickle"

def examine_pickle():
    """
    Examine the structure of the pickle file.
    """
    try:
        if os.path.exists(SOLAR_SYSTEMS_FILE):
            with open(SOLAR_SYSTEMS_FILE, 'rb') as f:
                solar_systems = pickle.load(f)
            
            print(f"Loaded {len(solar_systems)} solar systems")
            
            # Get a sample system
            sample_id = next(iter(solar_systems))
            sample_system = solar_systems[sample_id]
            
            print("\nSample system structure:")
            print(json.dumps(sample_system, indent=2))
            
            # Check how many adjacent systems each system has
            adjacent_counts = {system_id: len(system["adjacent"]) for system_id, system in solar_systems.items()}
            max_adjacent = max(adjacent_counts.values())
            min_adjacent = min(adjacent_counts.values())
            avg_adjacent = sum(adjacent_counts.values()) / len(adjacent_counts)
            
            print(f"\nAdjacent systems statistics:")
            print(f"Min: {min_adjacent}, Max: {max_adjacent}, Avg: {avg_adjacent:.2f}")
            
            # Find a system with many adjacent systems
            many_adjacent_id = max(adjacent_counts, key=adjacent_counts.get)
            many_adjacent_system = solar_systems[many_adjacent_id]
            
            print(f"\nSystem with most adjacent systems ({adjacent_counts[many_adjacent_id]}):")
            print(f"Name: {many_adjacent_system['name']}")
            print(f"Adjacent systems: {', '.join([solar_systems[adj_id]['name'] for adj_id in many_adjacent_system['adjacent']])}")
            
        else:
            print(f"Solar systems file not found: {SOLAR_SYSTEMS_FILE}")
    except Exception as e:
        print(f"Error examining pickle file: {e}")

if __name__ == "__main__":
    examine_pickle()

