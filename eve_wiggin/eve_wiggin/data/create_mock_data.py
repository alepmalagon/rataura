"""
Create mock solar systems data for testing.
"""

import pickle
import os

# Define mock solar systems
mock_solar_systems = {
    "30003067": {
        "name": "Huola",
        "solar_system_id": "30003067",
        "region": "The Bleak Lands",
        "region_id": "10000038",
        "constellation": "Sasen",
        "constellation_id": "20000448",
        "adjacent": ["30003068", "30003069"]  # Connected to Kourmonen and Kamela
    },
    "30003068": {
        "name": "Kourmonen",
        "solar_system_id": "30003068",
        "region": "The Bleak Lands",
        "region_id": "10000038",
        "constellation": "Sasen",
        "constellation_id": "20000448",
        "adjacent": ["30003067", "30002537"]  # Connected to Huola and Amamake
    },
    "30003069": {
        "name": "Kamela",
        "solar_system_id": "30003069",
        "region": "The Bleak Lands",
        "region_id": "10000038",
        "constellation": "Sasen",
        "constellation_id": "20000448",
        "adjacent": ["30003067", "30003070"]  # Connected to Huola and Sosala
    },
    "30003070": {
        "name": "Sosala",
        "solar_system_id": "30003070",
        "region": "The Bleak Lands",
        "region_id": "10000038",
        "constellation": "Sasen",
        "constellation_id": "20000448",
        "adjacent": ["30003069"]  # Connected to Kamela
    },
    "30002537": {
        "name": "Amamake",
        "solar_system_id": "30002537",
        "region": "Heimatar",
        "region_id": "10000030",
        "constellation": "Matar",
        "constellation_id": "20000352",
        "adjacent": ["30003068", "30002538"]  # Connected to Kourmonen and Vard
    },
    "30002538": {
        "name": "Vard",
        "solar_system_id": "30002538",
        "region": "Heimatar",
        "region_id": "10000030",
        "constellation": "Matar",
        "constellation_id": "20000352",
        "adjacent": ["30002537", "30002539"]  # Connected to Amamake and Siseide
    },
    "30002539": {
        "name": "Siseide",
        "solar_system_id": "30002539",
        "region": "Heimatar",
        "region_id": "10000030",
        "constellation": "Matar",
        "constellation_id": "20000352",
        "adjacent": ["30002538"]  # Connected to Vard
    }
}

# Add more systems for the Amarr/Minmatar warzone
for i in range(30):
    system_id = f"3000{3100 + i}"
    mock_solar_systems[system_id] = {
        "name": f"Amarr System {i}",
        "solar_system_id": system_id,
        "region": "The Bleak Lands",
        "region_id": "10000038",
        "constellation": "Sasen",
        "constellation_id": "20000448",
        "adjacent": [f"3000{3100 + j}" for j in range(max(0, i-2), min(30, i+3)) if j != i]
    }

for i in range(30):
    system_id = f"3000{2600 + i}"
    mock_solar_systems[system_id] = {
        "name": f"Minmatar System {i}",
        "solar_system_id": system_id,
        "region": "Heimatar",
        "region_id": "10000030",
        "constellation": "Matar",
        "constellation_id": "20000352",
        "adjacent": [f"3000{2600 + j}" for j in range(max(0, i-2), min(30, i+3)) if j != i]
    }

# Connect some Amarr and Minmatar systems to create frontlines
for i in range(5):
    amarr_id = f"3000{3100 + i}"
    minmatar_id = f"3000{2600 + i}"
    
    # Add connections
    mock_solar_systems[amarr_id]["adjacent"].append(minmatar_id)
    mock_solar_systems[minmatar_id]["adjacent"].append(amarr_id)

# Save the mock data
with open("solar_systems.pickle", "wb") as f:
    pickle.dump(mock_solar_systems, f)

print(f"Created mock data with {len(mock_solar_systems)} solar systems")

