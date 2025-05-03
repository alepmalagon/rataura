"""
Tests for the visualization module.
"""

import pytest
from unittest.mock import patch, MagicMock

from eve_wiggin.visualization.console import ConsoleVisualizer
from eve_wiggin.models.faction_warfare import FactionID, SystemAdjacency, SystemStatus


class TestConsoleVisualizer:
    """
    Tests for the ConsoleVisualizer class.
    """
    
    def setup_method(self):
        """
        Set up the test environment.
        """
        self.visualizer = ConsoleVisualizer()
    
    @patch('builtins.print')
    def test_display_warzone_summary(self, mock_print):
        """
        Test the display_warzone_summary method.
        """
        # Create mock warzone data
        warzone_data = {
            'name': 'Amarr-Minmatar Warzone',
            'total_systems': 70,
            'factions': [FactionID.AMARR_EMPIRE, FactionID.MINMATAR_REPUBLIC],
            'systems': {FactionID.AMARR_EMPIRE: 35, FactionID.MINMATAR_REPUBLIC: 35},
            'control_percentages': {FactionID.AMARR_EMPIRE: 50.0, FactionID.MINMATAR_REPUBLIC: 50.0},
            'contested': {FactionID.AMARR_EMPIRE: 10, FactionID.MINMATAR_REPUBLIC: 15}
        }
        
        # Call the method
        self.visualizer.display_warzone_summary(warzone_data)
        
        # Check that print was called
        assert mock_print.call_count > 0
    
    @patch('builtins.print')
    def test_display_faction_stats(self, mock_print):
        """
        Test the display_faction_stats method.
        """
        # Create mock faction stats
        faction_stats = {
            str(FactionID.AMARR_EMPIRE): {
                'pilots': 1000,
                'systems_controlled': 35,
                'victory_points_yesterday': 10000,
                'kills_yesterday': 500
            },
            str(FactionID.MINMATAR_REPUBLIC): {
                'pilots': 1200,
                'systems_controlled': 35,
                'victory_points_yesterday': 12000,
                'kills_yesterday': 600
            }
        }
        
        # Call the method
        self.visualizer.display_faction_stats(faction_stats)
        
        # Check that print was called
        assert mock_print.call_count > 0
    
    @patch('builtins.print')
    @patch('eve_wiggin.visualization.console.tabulate')
    def test_display_systems_table(self, mock_tabulate, mock_print):
        """
        Test the display_systems_table method.
        """
        # Mock tabulate to return a string
        mock_tabulate.return_value = "Mocked Table"
        
        # Create mock systems data
        systems = [
            {
                'system': {
                    'solar_system_id': 30003067,
                    'solar_system_name': 'Huola',
                    'owner_faction_id': FactionID.AMARR_EMPIRE,
                    'occupier_faction_id': FactionID.AMARR_EMPIRE,
                    'contested': SystemStatus.UNCONTESTED,
                    'victory_points': 0,
                    'victory_points_threshold': 75000,
                    'advantage': 0.0,
                    'adjacency': SystemAdjacency.FRONTLINE,
                    'contest_percent': 0.0,
                    'warzone': 'amarr_minmatar'
                },
                'system_info': {
                    'name': 'Huola',
                    'security_status': 0.37,
                    'security_class': 'B2',
                    'constellation_id': 20000448,
                    'constellation_name': 'Sasen',
                    'region_name': 'The Bleak Lands'
                },
                'owner_faction_name': 'Amarr Empire',
                'occupier_faction_name': 'Amarr Empire'
            }
        ]
        
        # Call the method with different sort options
        for sort_by in ['name', 'security', 'contest', 'region']:
            self.visualizer.display_systems_table(systems, sort_by=sort_by)
        
        # Check that tabulate was called for each sort option
        assert mock_tabulate.call_count == 4
        
        # Check that print was called
        assert mock_print.call_count > 0
    
    @patch('builtins.print')
    def test_display_system_details(self, mock_print):
        """
        Test the display_system_details method.
        """
        # Create mock system data
        system = {
            'system': {
                'solar_system_id': 30003067,
                'solar_system_name': 'Huola',
                'owner_faction_id': FactionID.AMARR_EMPIRE,
                'occupier_faction_id': FactionID.AMARR_EMPIRE,
                'contested': SystemStatus.UNCONTESTED,
                'victory_points': 0,
                'victory_points_threshold': 75000,
                'advantage': 0.0,
                'adjacency': SystemAdjacency.FRONTLINE,
                'contest_percent': 0.0,
                'warzone': 'amarr_minmatar'
            },
            'system_info': {
                'name': 'Huola',
                'security_status': 0.37,
                'security_class': 'B2',
                'constellation_id': 20000448,
                'constellation_name': 'Sasen',
                'region_name': 'The Bleak Lands'
            },
            'owner_faction_name': 'Amarr Empire',
            'occupier_faction_name': 'Amarr Empire'
        }
        
        # Call the method
        self.visualizer.display_system_details(system)
        
        # Check that print was called
        assert mock_print.call_count > 0

