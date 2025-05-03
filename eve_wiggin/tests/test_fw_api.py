"""
Tests for the faction warfare API.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from eve_wiggin.api.fw_api import FWApi
from eve_wiggin.models.faction_warfare import FWWarzoneStatus, FWWarzone


@pytest.fixture
def mock_analyzer():
    """
    Fixture for a mock faction warfare analyzer.
    """
    mock = MagicMock()
    mock.get_warzone_status = AsyncMock()
    mock.get_system_details = AsyncMock()
    mock.esi_client = MagicMock()
    mock.esi_client.search = AsyncMock()
    return mock


@pytest.fixture
def fw_api(mock_analyzer):
    """
    Fixture for a faction warfare API with a mock analyzer.
    """
    api = FWApi()
    api.analyzer = mock_analyzer
    return api


@pytest.mark.asyncio
async def test_get_warzone_status(fw_api, mock_analyzer):
    """
    Test getting warzone status.
    """
    # Create a mock warzone status
    mock_warzone = FWWarzone(
        name="Caldari-Gallente Warzone",
        factions=[500001, 500004],
        systems={500001: 10, 500004: 15},
        contested={500001: 2, 500004: 3},
        total_systems=25,
        control_percentages={500001: 40.0, 500004: 60.0}
    )
    
    mock_status = FWWarzoneStatus(
        warzones={"caldari_gallente": mock_warzone},
        faction_stats={},
        timestamp="2023-01-01T00:00:00"
    )
    
    # Set up the mock
    mock_analyzer.get_warzone_status.return_value = mock_status
    
    # Call the method
    result = await fw_api.get_warzone_status()
    
    # Verify the result
    assert "warzones" in result
    assert "caldari_gallente" in result["warzones"]
    assert result["warzones"]["caldari_gallente"]["name"] == "Caldari-Gallente Warzone"
    assert result["warzones"]["caldari_gallente"]["total_systems"] == 25
    assert result["warzones"]["caldari_gallente"]["control_percentages"][500004] == 60.0


@pytest.mark.asyncio
async def test_get_system_details(fw_api, mock_analyzer):
    """
    Test getting system details.
    """
    # Mock system details
    mock_details = {
        "system": {
            "solar_system_id": 30002813,
            "solar_system_name": "Tama",
            "owner_faction_id": 500001,
            "occupier_faction_id": 500001,
            "contested": "uncontested",
            "victory_points": 0,
            "victory_points_threshold": 3000
        },
        "system_info": {
            "name": "Tama",
            "security_status": 0.3,
            "security_class": "D",
            "constellation_name": "Kaimon",
            "region_name": "Black Rise"
        },
        "owner_faction_name": "Caldari State",
        "occupier_faction_name": "Caldari State"
    }
    
    # Set up the mock
    mock_analyzer.get_system_details.return_value = mock_details
    
    # Call the method
    result = await fw_api.get_system_details(30002813)
    
    # Verify the result
    assert result["system"]["solar_system_id"] == 30002813
    assert result["system"]["solar_system_name"] == "Tama"
    assert result["system_info"]["security_status"] == 0.3
    assert result["owner_faction_name"] == "Caldari State"


@pytest.mark.asyncio
async def test_search_system(fw_api, mock_analyzer):
    """
    Test searching for a system.
    """
    # Mock search result
    mock_analyzer.esi_client.search.return_value = {
        "solar_system": [30002813]
    }
    
    # Mock system details
    mock_details = {
        "system": {
            "solar_system_id": 30002813,
            "solar_system_name": "Tama"
        }
    }
    
    # Set up the mock
    mock_analyzer.get_system_details.return_value = mock_details
    
    # Call the method
    result = await fw_api.search_system("Tama")
    
    # Verify the result
    assert result["system"]["solar_system_id"] == 30002813
    assert result["system"]["solar_system_name"] == "Tama"
    
    # Verify the search call
    mock_analyzer.esi_client.search.assert_called_once_with("Tama", ["solar_system"], strict=True)
    mock_analyzer.get_system_details.assert_called_once_with(30002813)


@pytest.mark.asyncio
async def test_search_system_not_found(fw_api, mock_analyzer):
    """
    Test searching for a system that doesn't exist.
    """
    # Mock search result (empty)
    mock_analyzer.esi_client.search.return_value = {
        "solar_system": []
    }
    
    # Call the method
    result = await fw_api.search_system("NonExistentSystem")
    
    # Verify the result
    assert "error" in result
    assert "not found" in result["error"]
    
    # Verify the search call
    mock_analyzer.esi_client.search.assert_called_once_with("NonExistentSystem", ["solar_system"], strict=True)
    mock_analyzer.get_system_details.assert_not_called()

