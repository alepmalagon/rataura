"""
Tests for the adjacency detector.
"""

import unittest
import os
import pickle
from unittest.mock import patch, MagicMock

from eve_wiggin.services.adjacency_detector import AdjacencyDetector, MINMATAR_PERMANENT_FRONTLINES, AMARR_PERMANENT_FRONTLINES
from eve_wiggin.models.faction_warfare import (
    FWSystem, FactionID, SystemAdjacency
)


class TestAdjacencyDetector(unittest.TestCase):
    """
    Test cases for the adjacency detector.
    """
    
    def setUp(self):
        """
        Set up the test case.
        """
        # Create a mock solar systems dictionary
        self.mock_solar_systems = {
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
        
        # Create mock FW systems
        self.fw_systems = [
            FWSystem(
                solar_system_id=30003067,
                solar_system_name="Huola",
                owner_faction_id=FactionID.MINMATAR_REPUBLIC,  # Changed to Minmatar to match permanent frontline list
                occupier_faction_id=FactionID.MINMATAR_REPUBLIC,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            ),
            FWSystem(
                solar_system_id=30003068,
                solar_system_name="Kourmonen",
                owner_faction_id=FactionID.AMARR_EMPIRE,
                occupier_faction_id=FactionID.AMARR_EMPIRE,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            ),
            FWSystem(
                solar_system_id=30003069,
                solar_system_name="Kamela",
                owner_faction_id=FactionID.MINMATAR_REPUBLIC,  # Changed to Minmatar to match permanent frontline list
                occupier_faction_id=FactionID.MINMATAR_REPUBLIC,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            ),
            FWSystem(
                solar_system_id=30003070,
                solar_system_name="Sosala",
                owner_faction_id=FactionID.MINMATAR_REPUBLIC,  # Changed to Minmatar to match permanent frontline list
                occupier_faction_id=FactionID.MINMATAR_REPUBLIC,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            ),
            FWSystem(
                solar_system_id=30002537,
                solar_system_name="Amamake",
                owner_faction_id=FactionID.AMARR_EMPIRE,  # Changed to Amarr to match permanent frontline list
                occupier_faction_id=FactionID.AMARR_EMPIRE,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            ),
            FWSystem(
                solar_system_id=30002538,
                solar_system_name="Vard",
                owner_faction_id=FactionID.MINMATAR_REPUBLIC,
                occupier_faction_id=FactionID.MINMATAR_REPUBLIC,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            ),
            FWSystem(
                solar_system_id=30002539,
                solar_system_name="Siseide",
                owner_faction_id=FactionID.MINMATAR_REPUBLIC,
                occupier_faction_id=FactionID.MINMATAR_REPUBLIC,
                contested="uncontested",
                victory_points=0,
                victory_points_threshold=20000,
                advantage=0.0,
                contest_percent=0.0,
                warzone="amarr_minmatar"
            )
        ]
        
        # Verify that our test data matches the permanent frontline lists
        assert "Huola" in MINMATAR_PERMANENT_FRONTLINES
        assert "Kamela" in MINMATAR_PERMANENT_FRONTLINES
        assert "Sosala" in MINMATAR_PERMANENT_FRONTLINES
        assert "Amamake" in AMARR_PERMANENT_FRONTLINES
    
    @patch('eve_wiggin.services.adjacency_detector.pickle.load')
    def test_determine_adjacency(self, mock_pickle_load):
        """
        Test the determine_adjacency method.
        """
        # Set up the mock
        mock_pickle_load.return_value = self.mock_solar_systems
        
        # Create the adjacency detector
        detector = AdjacencyDetector()
        
        # Determine adjacency
        updated_systems = detector.determine_adjacency(self.fw_systems)
        
        # Verify the results
        system_by_id = {system.solar_system_id: system for system in updated_systems}
        
        # Huola should be a frontline (permanent Minmatar frontline)
        self.assertEqual(system_by_id[30003067].adjacency, SystemAdjacency.FRONTLINE)
        
        # Kourmonen should be a frontline (adjacent to Amamake which is Amarr)
        self.assertEqual(system_by_id[30003068].adjacency, SystemAdjacency.FRONTLINE)
        
        # Kamela should be a frontline (permanent Minmatar frontline)
        self.assertEqual(system_by_id[30003069].adjacency, SystemAdjacency.FRONTLINE)
        
        # Sosala should be a frontline (permanent Minmatar frontline)
        self.assertEqual(system_by_id[30003070].adjacency, SystemAdjacency.FRONTLINE)
        
        # Amamake should be a frontline (permanent Amarr frontline and adjacent to Kourmonen)
        self.assertEqual(system_by_id[30002537].adjacency, SystemAdjacency.FRONTLINE)
        
        # Vard should be a frontline (adjacent to Amamake which is Amarr)
        self.assertEqual(system_by_id[30002538].adjacency, SystemAdjacency.FRONTLINE)
        
        # Siseide should be a command ops (adjacent to Vard which is a frontline)
        self.assertEqual(system_by_id[30002539].adjacency, SystemAdjacency.COMMAND_OPERATIONS)
    
    @patch('eve_wiggin.services.adjacency_detector.pickle.load')
    def test_empty_solar_systems(self, mock_pickle_load):
        """
        Test the determine_adjacency method with empty solar systems.
        """
        # Set up the mock
        mock_pickle_load.return_value = {}
        
        # Create the adjacency detector
        detector = AdjacencyDetector()
        
        # Determine adjacency
        updated_systems = detector.determine_adjacency(self.fw_systems)
        
        # Verify the results - all systems should be rearguards except permanent frontlines
        system_by_id = {system.solar_system_id: system for system in updated_systems}
        
        # Huola should be a frontline (permanent Minmatar frontline)
        self.assertEqual(system_by_id[30003067].adjacency, SystemAdjacency.FRONTLINE)
        
        # Kamela should be a frontline (permanent Minmatar frontline)
        self.assertEqual(system_by_id[30003069].adjacency, SystemAdjacency.FRONTLINE)
        
        # Sosala should be a frontline (permanent Minmatar frontline)
        self.assertEqual(system_by_id[30003070].adjacency, SystemAdjacency.FRONTLINE)
        
        # Amamake should be a frontline (permanent Amarr frontline)
        self.assertEqual(system_by_id[30002537].adjacency, SystemAdjacency.FRONTLINE)
        
        # All other systems should be rearguards
        self.assertEqual(system_by_id[30003068].adjacency, SystemAdjacency.REARGUARD)
        self.assertEqual(system_by_id[30002538].adjacency, SystemAdjacency.REARGUARD)
        self.assertEqual(system_by_id[30002539].adjacency, SystemAdjacency.REARGUARD)


if __name__ == '__main__':
    unittest.main()
