"""
Tests for the faction warfare analyzer service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from eve_wiggin.services.fw_analyzer import FWAnalyzer
from eve_wiggin.models.faction_warfare import (
    FWSystem, FWFactionStats, FWWarzone, FWWarzoneStatus,
    FactionID, Warzone, SystemStatus
)


@pytest.fixture
def mock_esi_client():
    """
    Fixture for a mock ESI client.
    """
    mock_client = MagicMock()
    mock_client.get_fw_systems = AsyncMock()
    mock_client.get_fw_stats = AsyncMock()
    mock_client.get_system = AsyncMock()
    mock_client.get_constellation = AsyncMock()
    mock_client.get_region = AsyncMock()
    mock_client.search = AsyncMock()
    return mock_client


@pytest.fixture
def fw_analyzer(mock_esi_client):
    """
    Fixture for a faction warfare analyzer with a mock ESI client.
    """
    analyzer = FWAnalyzer()
    analyzer.esi_client = mock_esi_client
    return analyzer


@pytest.mark.asyncio
async def test_get_fw_systems(fw_analyzer, mock_esi_client):
    """
    Test getting faction warfare systems.
    """
    # Mock ESI response
    mock_esi_client.get_fw_systems.return_value = [
        {
            "solar_system_id": 30002813,
            "owner_faction_id": 500001,
            "occupier_faction_id": 500001,
            "contested": "uncontested",
            "victory_points": 0,
            "victory_points_threshold": 3000,
            "advantage": 0.0
        },
        {
            "solar_system_id": 30045334,
            "owner_faction_id": 500004,
            "occupier_faction_id": 500001,
            "contested": "contested",
            "victory_points": 1500,
            "victory_points_threshold": 3000,
            "advantage": 20.0
        }
    ]
    
    # Call the method
    systems = await fw_analyzer.get_fw_systems()
    
    # Verify the result
    assert len(systems) == 2
    assert isinstance(systems[0], FWSystem)
    assert systems[0].solar_system_id == 30002813
    assert systems[0].owner_faction_id == 500001
    assert systems[0].warzone == Warzone.CALDARI_GALLENTE
    assert systems[1].solar_system_id == 30045334
    assert systems[1].contest_percent == 50.0
    assert systems[1].warzone == Warzone.CALDARI_GALLENTE


@pytest.mark.asyncio
async def test_get_fw_faction_stats(fw_analyzer, mock_esi_client):
    """
    Test getting faction warfare statistics.
    """
    # Mock ESI response
    mock_esi_client.get_fw_stats.return_value = [
        {
            "faction_id": 500001,
            "pilots": 1234,
            "systems_controlled": 42,
            "kills": {
                "yesterday": 100,
                "last_week": 700,
                "total": 10000
            },
            "victory_points": {
                "yesterday": 1000,
                "last_week": 7000,
                "total": 100000
            }
        }
    ]
    
    # Call the method
    faction_stats = await fw_analyzer.get_fw_faction_stats()
    
    # Verify the result
    assert len(faction_stats) == 1
    assert 500001 in faction_stats
    assert isinstance(faction_stats[500001], FWFactionStats)
    assert faction_stats[500001].pilots == 1234
    assert faction_stats[500001].systems_controlled == 42
    assert faction_stats[500001].kills_yesterday == 100
    assert faction_stats[500001].kills_last_week == 700
    assert faction_stats[500001].kills_total == 10000


@pytest.mark.asyncio
async def test_get_warzone_status(fw_analyzer, mock_esi_client):
    """
    Test getting warzone status.
    """
    # Mock get_fw_systems
    mock_systems = [
        FWSystem(
            solar_system_id=30002813,
            owner_faction_id=500001,
            occupier_faction_id=500001,
            contested="uncontested",
            victory_points=0,
            victory_points_threshold=3000,
            warzone=Warzone.CALDARI_GALLENTE
        ),
        FWSystem(
            solar_system_id=30045334,
            owner_faction_id=500004,
            occupier_faction_id=500001,
            contested="contested",
            victory_points=1500,
            victory_points_threshold=3000,
            contest_percent=50.0,
            warzone=Warzone.CALDARI_GALLENTE
        )
    ]
    
    # Mock get_fw_faction_stats
    mock_faction_stats = {
        500001: FWFactionStats(
            faction_id=500001,
            pilots=1234,
            systems_controlled=42,
            kills_yesterday=100,
            kills_last_week=700,
            kills_total=10000
        )
    }
    
    # Set up the mocks
    with patch.object(fw_analyzer, 'get_fw_systems', return_value=mock_systems), \
         patch.object(fw_analyzer, 'get_fw_faction_stats', return_value=mock_faction_stats):
        
        # Call the method
        warzone_status = await fw_analyzer.get_warzone_status()
        
        # Verify the result
        assert isinstance(warzone_status, FWWarzoneStatus)
        assert Warzone.CALDARI_GALLENTE in warzone_status.warzones
        assert Warzone.AMARR_MINMATAR in warzone_status.warzones
        
        # Check Caldari-Gallente warzone
        cg_warzone = warzone_status.warzones[Warzone.CALDARI_GALLENTE]
        assert cg_warzone.systems[500001] == 1
        assert cg_warzone.systems[500004] == 1
        assert cg_warzone.contested[500001] == 1
        assert cg_warzone.total_systems == 2
        assert cg_warzone.control_percentages[500001] == 50.0
        assert cg_warzone.control_percentages[500004] == 50.0
        
        # Check faction stats
        assert 500001 in warzone_status.faction_stats
        assert warzone_status.faction_stats[500001].pilots == 1234


@pytest.mark.asyncio
async def test_get_system_details(fw_analyzer, mock_esi_client):
    """
    Test getting system details.
    """
    # Mock get_fw_systems
    mock_systems = [
        FWSystem(
            solar_system_id=30002813,
            owner_faction_id=500001,
            occupier_faction_id=500001,
            contested="uncontested",
            victory_points=0,
            victory_points_threshold=3000,
            warzone=Warzone.CALDARI_GALLENTE
        )
    ]
    
    # Mock ESI responses
    mock_esi_client.get_system.return_value = {
        "name": "Tama",
        "security_status": 0.3,
        "security_class": "D",
        "constellation_id": 20000346
    }
    
    mock_esi_client.get_constellation.return_value = {
        "name": "Kaimon",
        "region_id": 10000069
    }
    
    mock_esi_client.get_region.return_value = {
        "name": "Black Rise"
    }
    
    # Set up the mocks
    with patch.object(fw_analyzer, 'get_fw_systems', return_value=mock_systems):
        
        # Call the method
        system_details = await fw_analyzer.get_system_details(30002813)
        
        # Verify the result
        assert system_details["system"]["solar_system_id"] == 30002813
        assert system_details["system_info"]["name"] == "Tama"
        assert system_details["system_info"]["security_status"] == 0.3
        assert system_details["system_info"]["constellation_name"] == "Kaimon"
        assert system_details["system_info"]["region_name"] == "Black Rise"
        assert system_details["owner_faction_name"] == "Caldari State"

