"""
LLM function tools module for the Rataura application.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
import aiohttp
from rataura.config import settings
from rataura.esi.client import get_esi_client

# Configure logging
logger = logging.getLogger(__name__)

# Function definitions for the LLM
FUNCTION_DEFINITIONS = [
    {
        "name": "get_alliance_info",
        "description": "Get information about an EVE Online alliance",
        "parameters": {
            "type": "object",
            "properties": {
                "alliance_id": {
                    "type": "integer",
                    "description": "The ID of the alliance"
                },
                "alliance_name": {
                    "type": "string",
                    "description": "The name of the alliance"
                }
            }
        }
    },
    {
        "name": "get_character_info",
        "description": "Get information about an EVE Online character",
        "parameters": {
            "type": "object",
            "properties": {
                "character_id": {
                    "type": "integer",
                    "description": "The ID of the character"
                },
                "character_name": {
                    "type": "string",
                    "description": "The name of the character (will be resolved to an ID)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_corporation_info",
        "description": "Get information about an EVE Online corporation",
        "parameters": {
            "type": "object",
            "properties": {
                "corporation_id": {
                    "type": "integer",
                    "description": "The ID of the corporation"
                },
                "corporation_name": {
                    "type": "string",
                    "description": "The name of the corporation (will be resolved to an ID)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_item_info",
        "description": "Get information about an EVE Online item type",
        "parameters": {
            "type": "object",
            "properties": {
                "type_id": {
                    "type": "integer",
                    "description": "The ID of the item type"
                },
                "type_name": {
                    "type": "string",
                    "description": "The name of the item type (will be resolved to an ID)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_market_prices",
        "description": "Get market prices for EVE Online items",
        "parameters": {
            "type": "object",
            "properties": {
                "type_id": {
                    "type": "integer",
                    "description": "The ID of the item type"
                },
                "type_name": {
                    "type": "string",
                    "description": "The name of the item type (will be resolved to an ID)"
                },
                "region_id": {
                    "type": "integer",
                    "description": "The ID of the region"
                },
                "region_name": {
                    "type": "string",
                    "description": "The name of the region (will be resolved to an ID)"
                },
                "system_id": {
                    "type": "integer",
                    "description": "The ID of the solar system to filter by"
                },
                "system_name": {
                    "type": "string",
                    "description": "The name of the solar system to filter by"
                }
            },
            "required": []
        }
    },
    {
        "name": "search_entities",
        "description": "Search for EVE Online entities by name",
        "parameters": {
            "type": "object",
            "properties": {
                "search": {
                    "type": "string",
                    "description": "The search query"
                },
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["alliance", "character", "constellation", "corporation", "faction", "inventory_type", "region", "solar_system", "station"]
                    },
                    "description": "The categories to search in"
                },
                "strict": {
                    "type": "boolean",
                    "description": "Whether to perform a strict search"
                }
            },
            "required": ["search"]
        }
    },
    {
        "name": "get_system_info",
        "description": "Get information about an EVE Online solar system",
        "parameters": {
            "type": "object",
            "properties": {
                "system_id": {
                    "type": "integer",
                    "description": "The ID of the solar system"
                },
                "system_name": {
                    "type": "string",
                    "description": "The name of the solar system (will be resolved to an ID)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_region_info",
        "description": "Get information about an EVE Online region",
        "parameters": {
            "type": "object",
            "properties": {
                "region_id": {
                    "type": "integer",
                    "description": "The ID of the region"
                },
                "region_name": {
                    "type": "string",
                    "description": "The name of the region (will be resolved to an ID)"
                }
            },
            "required": []
        }
    },
    {
        "name": "get_killmail_info",
        "description": "Get information about recent killmails for a character, corporation, alliance, or ship type from zKillboard",
        "parameters": {
            "type": "object",
            "properties": {
                "character_id": {
                    "type": "integer",
                    "description": "The ID of the character to get killmails for"
                },
                "character_name": {
                    "type": "string",
                    "description": "The name of the character to get killmails for (will be resolved to an ID)"
                },
                "corporation_id": {
                    "type": "integer",
                    "description": "The ID of the corporation to get killmails for"
                },
                "corporation_name": {
                    "type": "string",
                    "description": "The name of the corporation to get killmails for (will be resolved to an ID)"
                },
                "alliance_id": {
                    "type": "integer",
                    "description": "The ID of the alliance to get killmails for"
                },
                "alliance_name": {
                    "type": "string",
                    "description": "The name of the alliance to get killmails for (will be resolved to an ID)"
                },
                "ship_type_id": {
                    "type": "integer",
                    "description": "The ID of the ship type to get killmails for"
                },
                "ship_type_name": {
                    "type": "string",
                    "description": "The name of the ship type to get killmails for (will be resolved to an ID)"
                },
                "limit": {
                    "type": "integer",
                    "description": "The maximum number of killmails to return (default: 5)"
                },
                "losses_only": {
                    "type": "boolean",
                    "description": "Whether to only return losses (default: false)"
                },
                "kills_only": {
                    "type": "boolean",
                    "description": "Whether to only return kills (default: false)"
                }
            },
            "required": []
        }
    }
]

# Function implementations

async def get_alliance_info(alliance_id: Optional[int] = None, alliance_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about an EVE Online alliance.
    
    Args:
        alliance_id (Optional[int], optional): The ID of the alliance.
        alliance_name (Optional[str], optional): The name of the alliance.
    
    Returns:
        Dict[str, Any]: Information about the alliance with IDs resolved to names.
    """
    esi_client = get_esi_client()
    
    # Resolve alliance name to ID if provided
    if alliance_name and not alliance_id:
        search_result = await esi_client.search(alliance_name, ["alliance"], strict=True)
        if "alliance" in search_result and search_result["alliance"]:
            alliance_id = search_result["alliance"][0]
        else:
            return {"error": f"Alliance '{alliance_name}' not found"}
    
    if not alliance_id:
        return {"error": "No alliance ID or name provided"}
    
    try:
        # Get basic alliance info
        alliance_info = await esi_client.get_alliance(alliance_id)
        
        # Resolve creator character ID to name
        if "creator_id" in alliance_info:
            try:
                creator_info = await esi_client.get_character(alliance_info["creator_id"])
                alliance_info["creator_name"] = creator_info.get("name", "Unknown")
            except Exception as e:
                logger.error(f"Error resolving creator name: {e}")
                alliance_info["creator_name"] = "Unknown"
        
        # Resolve creator corporation ID to name
        if "creator_corporation_id" in alliance_info:
            try:
                creator_corp_info = await esi_client.get_corporation(alliance_info["creator_corporation_id"])
                alliance_info["creator_corporation_name"] = creator_corp_info.get("name", "Unknown")
            except Exception as e:
                logger.error(f"Error resolving creator corporation name: {e}")
                alliance_info["creator_corporation_name"] = "Unknown"
        
        # Resolve executor corporation ID to name
        if "executor_corporation_id" in alliance_info:
            try:
                executor_corp_info = await esi_client.get_corporation(alliance_info["executor_corporation_id"])
                alliance_info["executor_corporation_name"] = executor_corp_info.get("name", "Unknown")
            except Exception as e:
                logger.error(f"Error resolving executor corporation name: {e}")
                alliance_info["executor_corporation_name"] = "Unknown"
        
        # Resolve faction ID to name if present
        if "faction_id" in alliance_info:
            # Since there's no direct faction endpoint, we'll use a mapping
            faction_names = {
                500001: "Caldari State",
                500002: "Minmatar Republic",
                500003: "Amarr Empire",
                500004: "Gallente Federation",
                500005: "Jove Empire",
                500006: "CONCORD Assembly",
                500007: "Ammatar Mandate",
                500008: "Khanid Kingdom",
                500009: "The Syndicate",
                500010: "Guristas Pirates",
                500011: "Angel Cartel",
                500012: "Blood Raider Covenant",
                500013: "The InterBus",
                500014: "ORE",
                500015: "Thukker Tribe",
                500016: "Servant Sisters of EVE",
                500017: "Society of Conscious Thought",
                500018: "Mordu's Legion Command",
                500019: "Sansha's Nation",
                500020: "Serpentis",
                500021: "Unknown",
                500022: "Unknown",
                500023: "Unknown",
                500024: "Unknown",
                500025: "Unknown",
                500026: "Unknown",
                500027: "Unknown",
                500028: "Unknown",
                500029: "Unknown",
                500030: "Unknown"
            }
            alliance_info["faction_name"] = faction_names.get(alliance_info["faction_id"], "Unknown Faction")
        
        # Format a human-readable response
        if "name" in alliance_info and "ticker" in alliance_info:
            response = f"{alliance_info['name']} ({alliance_info['ticker']})"
            
            if "date_founded" in alliance_info:
                response += f" was founded on {alliance_info['date_founded']}."
            
            if "creator_name" in alliance_info and "creator_corporation_name" in alliance_info:
                response += f" The creator was {alliance_info['creator_name']}, of corporation {alliance_info['creator_corporation_name']}."
            
            if "executor_corporation_name" in alliance_info:
                response += f" The executor corporation is {alliance_info['executor_corporation_name']}."
            
            if "faction_name" in alliance_info:
                response += f" They are aligned with the {alliance_info['faction_name']}."
            
            alliance_info["formatted_info"] = response
        
        return alliance_info
    except Exception as e:
        logger.error(f"Error getting alliance info: {e}")
        return {"error": f"Error getting alliance info: {str(e)}"}


async def get_character_info(character_id: Optional[int] = None, character_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about an EVE Online character.
    
    Args:
        character_id (Optional[int], optional): The ID of the character.
        character_name (Optional[str], optional): The name of the character.
    
    Returns:
        Dict[str, Any]: Information about the character.
    """
    esi_client = get_esi_client()
    
    # Resolve character name to ID if provided
    if character_name and not character_id:
        logger.info(f"Resolving character name '{character_name}' to ID")
        search_result = await esi_client.search(character_name, ["character"], strict=True)
        if "character" in search_result and search_result["character"]:
            character_id = search_result["character"][0]
            logger.info(f"Resolved character name '{character_name}' to ID {character_id}")
        else:
            logger.error(f"Character '{character_name}' not found")
            return {"error": f"Character '{character_name}' not found"}
    
    if not character_id:
        logger.error("No character ID or name provided")
        return {"error": "No character ID or name provided"}
    
    try:
        # Get basic character information
        logger.info(f"Getting character info for ID {character_id}")
        character_info = await esi_client.get_character(character_id)
        
        # Enhance with corporation information
        if "corporation_id" in character_info:
            corp_id = character_info["corporation_id"]
            logger.info(f"Getting corporation info for ID {corp_id}")
            try:
                corp_info = await esi_client.get_corporation(corp_id)
                character_info["corporation_name"] = corp_info.get("name", "Unknown Corporation")
                logger.info(f"Character belongs to corporation: {character_info['corporation_name']}")
            except Exception as e:
                logger.error(f"Error getting corporation info: {e}")
                character_info["corporation_name"] = f"Unknown Corporation (ID: {corp_id})"
        
        # Enhance with alliance information if available
        if "alliance_id" in character_info:
            alliance_id = character_info["alliance_id"]
            logger.info(f"Getting alliance info for ID {alliance_id}")
            try:
                alliance_info = await esi_client.get_alliance(alliance_id)
                character_info["alliance_name"] = alliance_info.get("name", "Unknown Alliance")
                logger.info(f"Character belongs to alliance: {character_info['alliance_name']}")
            except Exception as e:
                logger.error(f"Error getting alliance info: {e}")
                character_info["alliance_name"] = f"Unknown Alliance (ID: {alliance_id})"
        
        return character_info
    except Exception as e:
        logger.error(f"Error getting character info: {e}")
        return {"error": f"Error getting character info: {str(e)}"}


async def get_corporation_info(corporation_id: Optional[int] = None, corporation_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about an EVE Online corporation.
    
    Args:
        corporation_id (Optional[int], optional): The ID of the corporation.
        corporation_name (Optional[str], optional): The name of the corporation.
    
    Returns:
        Dict[str, Any]: Information about the corporation.
    """
    esi_client = get_esi_client()
    
    # Resolve corporation name to ID if provided
    if corporation_name and not corporation_id:
        search_result = await esi_client.search(corporation_name, ["corporation"], strict=True)
        if "corporation" in search_result and search_result["corporation"]:
            corporation_id = search_result["corporation"][0]
        else:
            return {"error": f"Corporation '{corporation_name}' not found"}
    
    if not corporation_id:
        return {"error": "No corporation ID or name provided"}
    
    try:
        corporation_info = await esi_client.get_corporation(corporation_id)
        return corporation_info
    except Exception as e:
        logger.error(f"Error getting corporation info: {e}")
        return {"error": f"Error getting corporation info: {str(e)}"}


async def get_item_info(type_id: Optional[int] = None, type_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about an EVE Online item type.
    
    Args:
        type_id (Optional[int], optional): The ID of the item type.
        type_name (Optional[str], optional): The name of the item type.
    
    Returns:
        Dict[str, Any]: Information about the item type.
    """
    esi_client = get_esi_client()
    
    # Resolve type name to ID if provided
    if type_name and not type_id:
        search_result = await esi_client.search(type_name, ["inventory_type"], strict=True)
        if "inventory_type" in search_result and search_result["inventory_type"]:
            type_id = search_result["inventory_type"][0]
        else:
            return {"error": f"Item type '{type_name}' not found"}
    
    if not type_id:
        return {"error": "No item type ID or name provided"}
    
    try:
        type_info = await esi_client.get_type(type_id)
        return type_info
    except Exception as e:
        logger.error(f"Error getting item info: {e}")
        return {"error": f"Error getting item info: {str(e)}"}


async def get_market_prices(type_id: Optional[int] = None, type_name: Optional[str] = None, region_id: Optional[int] = None, region_name: Optional[str] = None, system_id: Optional[int] = None, system_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get market prices for EVE Online items. Can search by region or specific solar system.
    
    Args:
        type_id (Optional[int], optional): The ID of the item type.
        type_name (Optional[str], optional): The name of the item type.
        region_id (Optional[int], optional): The ID of the region.
        region_name (Optional[str], optional): The name of the region.
        system_id (Optional[int], optional): The ID of the solar system to filter by.
        system_name (Optional[str], optional): The name of the solar system to filter by.
    
    Returns:
        Dict[str, Any]: Market prices for the item.
    """
    esi_client = get_esi_client()
    
    # Resolve type name to ID if provided
    if type_name and not type_id:
        logger.info(f"Resolving type name '{type_name}' to ID")
        search_result = await esi_client.search(type_name, ["inventory_type"], strict=True)
        logger.info(f"Search result for type '{type_name}': {search_result}")
        
        if "inventory_type" in search_result and search_result["inventory_type"]:
            type_id = search_result["inventory_type"][0]
            logger.info(f"Resolved type name '{type_name}' to ID {type_id}")
        else:
            logger.warning(f"Item type '{type_name}' not found")
            return {"error": f"Item type '{type_name}' not found"}
    
    if not type_id:
        logger.warning("No item type ID or name provided")
        return {"error": "No item type ID or name provided"}
    
    # Resolve system name to ID if provided
    system_filter_active = False
    system_region_id = None
    if system_name and not system_id:
        logger.info(f"Resolving system name '{system_name}' to ID")
        search_result = await esi_client.search(system_name, ["solar_system"], strict=True)
        logger.info(f"Search result for system '{system_name}': {search_result}")
        
        if "solar_system" in search_result and search_result["solar_system"]:
            system_id = search_result["solar_system"][0]
            system_filter_active = True
            logger.info(f"Resolved system name '{system_name}' to ID {system_id}")
        else:
            logger.warning(f"System '{system_name}' not found")
            return {"error": f"System '{system_name}' not found"}
    elif system_id:
        system_filter_active = True
    
    # If we're filtering by system, determine which region it belongs to
    if system_filter_active and system_id:
        try:
            system_info = await esi_client.get_system(system_id)
            system_name = system_info.get("name", f"System ID {system_id}")
            # Get the constellation to find the region
            constellation_id = system_info.get("constellation_id")
            if constellation_id:
                constellation_info = await esi_client.get(f"/universe/constellations/{constellation_id}/")
                system_region_id = constellation_info.get("region_id")
                if system_region_id:
                    logger.info(f"System {system_name} (ID: {system_id}) is in region ID {system_region_id}")
                    # If region was specified but doesn't match the system's region, warn about it
                    if region_id and region_id != system_region_id:
                        logger.warning(f"Specified region ID {region_id} doesn't match system's region ID {system_region_id}. Using system's region.")
                    # Use the system's region
                    region_id = system_region_id
        except Exception as e:
            logger.error(f"Error determining region for system {system_id}: {e}")
    
    # Resolve region name to ID if provided
    if region_name and not region_id:
        logger.info(f"Resolving region name '{region_name}' to ID")
        search_result = await esi_client.search(region_name, ["region"], strict=True)
        logger.info(f"Search result for region '{region_name}': {search_result}")
        
        if "region" in search_result and search_result["region"]:
            region_id = search_result["region"][0]
            logger.info(f"Resolved region name '{region_name}' to ID {region_id}")
        else:
            logger.warning(f"Region '{region_name}' not found")
            return {"error": f"Region '{region_name}' not found"}
    
    # If no region is specified, use The Forge (Jita)
    if not region_id:
        region_id = 10000002  # The Forge
        logger.info(f"No region specified, using The Forge (ID: {region_id})")
    
    try:
        # Get market orders for the item in the region
        logger.info(f"Getting market orders for type ID {type_id} in region ID {region_id}")
        market_orders = await esi_client.get_market_orders(region_id, type_id)
        logger.info(f"Found {len(market_orders)} market orders")
        
        # Log the first order to see its structure
        if market_orders and len(market_orders) > 0:
            logger.info(f"Sample market order: {market_orders[0]}")
        
        if not market_orders:
            logger.warning(f"No market orders found for type ID {type_id} in region ID {region_id}")
            
            # Get item info for better error message
            try:
                type_info = await esi_client.get_type(type_id)
                type_name = type_info.get("name", f"Type ID {type_id}")
            except Exception:
                type_name = f"Type ID {type_id}"
                
            # Get region info for better error message
            try:
                region_info = await esi_client.get_region(region_id)
                region_name = region_info.get("name", f"Region ID {region_id}")
            except Exception:
                region_name = f"Region ID {region_id}"
                
            return {"error": f"No market orders found for {type_name} in {region_name}"}
        
        # Filter by system if specified
        if system_filter_active and system_id:
            logger.info(f"Filtering market orders by system ID {system_id}")
            
            # Filter orders by system_id directly
            filtered_orders = [order for order in market_orders if order.get("system_id") == system_id]
            
            logger.info(f"Filtered from {len(market_orders)} to {len(filtered_orders)} orders in system {system_name}")
            
            # If no orders in the system, return an error
            if not filtered_orders:
                return {"error": f"No market orders found for {type_name} in system {system_name}"}
            
            # Use the filtered orders for further processing
            market_orders = filtered_orders
        
        # Process the orders
        buy_orders = [order for order in market_orders if order.get("is_buy_order", False)]
        sell_orders = [order for order in market_orders if not order.get("is_buy_order", False)]
        
        logger.info(f"Found {len(buy_orders)} buy orders and {len(sell_orders)} sell orders")
        
        # Calculate statistics
        highest_buy = max(buy_orders, key=lambda x: x["price"])["price"] if buy_orders else None
        lowest_sell = min(sell_orders, key=lambda x: x["price"])["price"] if sell_orders else None
        
        # Get best buy and sell orders with location information
        best_buy_order = max(buy_orders, key=lambda x: x["price"]) if buy_orders else None
        best_sell_order = min(sell_orders, key=lambda x: x["price"]) if sell_orders else None
        
        # Get item info
        type_info = await esi_client.get_type(type_id)
        
        # Get region info
        region_info = await esi_client.get_region(region_id)
        
        # Get location information for best orders
        best_buy_location = None
        best_sell_location = None
        if best_buy_order and "location_id" in best_buy_order:
            location_id = best_buy_order["location_id"]
            # Check if it's a station (range 60000000-64000000)
            if 60000000 <= location_id < 64000000:
                try:
                    station_info = await esi_client.get(f"/universe/stations/{location_id}/")
                    best_buy_location = f"{station_info.get('name', 'Unknown Station')}"
                    # Get the system name
                    if "system_id" in station_info:
                        system_info = await esi_client.get_system(station_info["system_id"])
                        best_buy_location = f"{station_info.get('name', 'Unknown Station')} in {system_info.get('name', 'Unknown System')}"
                except Exception as e:
                    logger.error(f"Error getting station info: {e}")
                    best_buy_location = f"Station ID {location_id}"
            # Check if it's a structure (not in the standard ID ranges)
            else:
                best_buy_location = f"Structure ID {location_id}"
        
        if best_sell_order and "location_id" in best_sell_order:
            location_id = best_sell_order["location_id"]
            # Check if it's a station (range 60000000-64000000)
            if 60000000 <= location_id < 64000000:
                try:
                    station_info = await esi_client.get(f"/universe/stations/{location_id}/")
                    best_sell_location = f"{station_info.get('name', 'Unknown Station')}"
                    # Get the system name
                    if "system_id" in station_info:
                        system_info = await esi_client.get_system(station_info["system_id"])
                        best_sell_location = f"{station_info.get('name', 'Unknown Station')} in {system_info.get('name', 'Unknown System')}"
                except Exception as e:
                    logger.error(f"Error getting station info: {e}")
                    best_sell_location = f"Station ID {location_id}"
            # Check if it's a structure (not in the standard ID ranges)
            else:
                best_sell_location = f"Structure ID {location_id}"
        
        # Create location context for the formatted message
        location_context = system_name if system_filter_active else region_info.get("name")
        
        result = {
            "type_id": type_id,
            "type_name": type_info.get("name"),
            "region_id": region_id,
            "region_name": region_info.get("name"),
            "system_id": system_id if system_filter_active else None,
            "system_name": system_name if system_filter_active else None,
            "highest_buy": highest_buy,
            "lowest_sell": lowest_sell,
            "buy_orders_count": len(buy_orders),
            "sell_orders_count": len(sell_orders),
            "best_buy_location": best_buy_location,
            "best_sell_location": best_sell_location,
            "formatted_info": f"Market prices for {type_info.get('name')} in {location_context}:\n" +
                             (f"Highest buy: {highest_buy:,.2f} ISK ({len(buy_orders)} orders)" + 
                              (f" at {best_buy_location}" if best_buy_location else "") + "\n" 
                              if highest_buy else "No buy orders found\n") +
                             (f"Lowest sell: {lowest_sell:,.2f} ISK ({len(sell_orders)} orders)" + 
                              (f" at {best_sell_location}" if best_sell_location else "")
                              if lowest_sell else "No sell orders found")
        }
        
        logger.info(f"Market price result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error getting market prices: {e}", exc_info=True)
        return {"error": f"Error getting market prices: {str(e)}"}


async def search_entities(search: str, categories: Optional[List[str]] = None, strict: bool = False) -> Dict[str, Any]:
    """
    Search for EVE Online entities by name.
    
    Args:
        search (str): The search query.
        categories (Optional[List[str]], optional): The categories to search in.
        strict (bool, optional): Whether to perform a strict search.
    
    Returns:
        Dict[str, Any]: The search results.
    """
    esi_client = get_esi_client()
    
    if not categories:
        categories = ["alliance", "character", "corporation", "inventory_type", "solar_system", "station"]
    
    try:
        search_result = await esi_client.search(search, categories, strict)
        
        # Resolve IDs to names
        resolved_results = {}
        
        for category, ids in search_result.items():
            if ids:
                try:
                    resolved = await esi_client.resolve_ids(ids)
                    resolved_results[category] = resolved
                except Exception as e:
                    logger.error(f"Error resolving IDs for category {category}: {e}")
                    resolved_results[category] = [{"id": id, "name": f"ID: {id}"} for id in ids]
        
        return {
            "search": search,
            "categories": categories,
            "strict": strict,
            "results": resolved_results,
        }
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        return {"error": f"Error searching entities: {str(e)}"}


async def get_system_info(system_id: Optional[int] = None, system_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about an EVE Online solar system.
    
    Args:
        system_id (Optional[int], optional): The ID of the solar system.
        system_name (Optional[str], optional): The name of the solar system.
    
    Returns:
        Dict[str, Any]: Information about the solar system.
    """
    esi_client = get_esi_client()
    
    # Resolve system name to ID if provided
    if system_name and not system_id:
        logger.info(f"Resolving system name '{system_name}' to ID")
        search_result = await esi_client.search(system_name, ["solar_system"], strict=True)
        if "solar_system" in search_result and search_result["solar_system"]:
            system_id = search_result["solar_system"][0]
            logger.info(f"Resolved system name '{system_name}' to ID {system_id}")
        else:
            logger.error(f"Solar system '{system_name}' not found")
            return {"error": f"Solar system '{system_name}' not found"}
    
    if not system_id:
        logger.error("No solar system ID or name provided")
        return {"error": "No solar system ID or name provided"}
    
    try:
        # Get system information
        system_info = await esi_client.get_system(system_id)
        
        # Get constellation information
        constellation_id = system_info.get("constellation_id")
        constellation_name = "Unknown"
        region_name = "Unknown"
        
        if constellation_id:
            try:
                constellation_info = await esi_client.get_constellation(constellation_id)
                constellation_name = constellation_info.get("name", "Unknown")
                
                # Get region information
                region_id = constellation_info.get("region_id")
                if region_id:
                    try:
                        region_info = await esi_client.get_region(region_id)
                        region_name = region_info.get("name", "Unknown")
                    except Exception as e:
                        logger.error(f"Error getting region info: {e}")
            except Exception as e:
                logger.error(f"Error getting constellation info: {e}")
        
        # Add human-readable names to the response
        system_info["constellation_name"] = constellation_name
        system_info["region_name"] = region_name
        
        return system_info
    except Exception as e:
        logger.error(f"Error getting solar system info: {e}")
        return {"error": f"Error getting solar system info: {str(e)}"}


async def get_region_info(region_id: Optional[int] = None, region_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get information about an EVE Online region.
    
    Args:
        region_id (Optional[int], optional): The ID of the region.
        region_name (Optional[str], optional): The name of the region.
    
    Returns:
        Dict[str, Any]: Information about the region.
    """
    esi_client = get_esi_client()
    
    # Resolve region name to ID if provided
    if region_name and not region_id:
        logger.info(f"Resolving region name '{region_name}' to ID")
        search_result = await esi_client.search(region_name, ["region"], strict=True)
        logger.info(f"Search result for region '{region_name}': {search_result}")
        
        if "region" in search_result and search_result["region"]:
            region_id = search_result["region"][0]
            logger.info(f"Resolved region name '{region_name}' to ID {region_id}")
        else:
            logger.error(f"Region '{region_name}' not found")
            return {"error": f"Region '{region_name}' not found"}
    
    if not region_id:
        logger.error("No region ID or name provided")
        return {"error": "No region ID or name provided"}
    
    try:
        region_info = await esi_client.get_region(region_id)
        
        # Get constellation names if available
        if "constellations" in region_info and region_info["constellations"]:
            constellation_names = []
            for constellation_id in region_info["constellations"][:5]:  # Limit to first 5 to avoid too many requests
                try:
                    constellation_info = await esi_client.get_constellation(constellation_id)
                    constellation_names.append(constellation_info.get("name", f"Constellation ID {constellation_id}"))
                except Exception as e:
                    logger.error(f"Error getting constellation info: {e}")
                    constellation_names.append(f"Constellation ID {constellation_id}")
            
            # Add constellation names to the response
            region_info["constellation_names"] = constellation_names
        
        return region_info
    except Exception as e:
        logger.error(f"Error getting region info: {e}")
        return {"error": f"Error getting region info: {str(e)}"}


async def get_killmail_info(
    character_id: Optional[int] = None, 
    character_name: Optional[str] = None,
    corporation_id: Optional[int] = None, 
    corporation_name: Optional[str] = None,
    alliance_id: Optional[int] = None, 
    alliance_name: Optional[str] = None,
    ship_type_id: Optional[int] = None, 
    ship_type_name: Optional[str] = None,
    limit: int = 5,
    losses_only: bool = False,
    kills_only: bool = False
) -> Dict[str, Any]:
    """
    Get information about recent killmails for a character, corporation, alliance, or ship type from zKillboard.
    
    Args:
        character_id (Optional[int], optional): The ID of the character to get killmails for.
        character_name (Optional[str], optional): The name of the character to get killmails for.
        corporation_id (Optional[int], optional): The ID of the corporation to get killmails for.
        corporation_name (Optional[str], optional): The name of the corporation to get killmails for.
        alliance_id (Optional[int], optional): The ID of the alliance to get killmails for.
        alliance_name (Optional[str], optional): The name of the alliance to get killmails for.
        ship_type_id (Optional[int], optional): The ID of the ship type to get killmails for.
        ship_type_name (Optional[str], optional): The name of the ship type to get killmails for.
        limit (int, optional): The maximum number of killmails to return. Defaults to 5.
        losses_only (bool, optional): Whether to only return losses. Defaults to False.
        kills_only (bool, optional): Whether to only return kills. Defaults to False.
    
    Returns:
        Dict[str, Any]: Information about recent killmails.
    """
    esi_client = get_esi_client()
    
    # Resolve names to IDs if provided
    if character_name and not character_id:
        logger.info(f"Resolving character name '{character_name}' to ID")
        search_result = await esi_client.search(character_name, ["character"], strict=True)
        if "character" in search_result and search_result["character"]:
            character_id = search_result["character"][0]
            logger.info(f"Resolved character name '{character_name}' to ID {character_id}")
        else:
            logger.error(f"Character '{character_name}' not found")
            return {"error": f"Character '{character_name}' not found"}
    
    if corporation_name and not corporation_id:
        logger.info(f"Resolving corporation name '{corporation_name}' to ID")
        search_result = await esi_client.search(corporation_name, ["corporation"], strict=True)
        if "corporation" in search_result and search_result["corporation"]:
            corporation_id = search_result["corporation"][0]
            logger.info(f"Resolved corporation name '{corporation_name}' to ID {corporation_id}")
        else:
            logger.error(f"Corporation '{corporation_name}' not found")
            return {"error": f"Corporation '{corporation_name}' not found"}
    
    if alliance_name and not alliance_id:
        logger.info(f"Resolving alliance name '{alliance_name}' to ID")
        search_result = await esi_client.search(alliance_name, ["alliance"], strict=True)
        if "alliance" in search_result and search_result["alliance"]:
            alliance_id = search_result["alliance"][0]
            logger.info(f"Resolved alliance name '{alliance_name}' to ID {alliance_id}")
        else:
            logger.error(f"Alliance '{alliance_name}' not found")
            return {"error": f"Alliance '{alliance_name}' not found"}
    
    if ship_type_name and not ship_type_id:
        logger.info(f"Resolving ship type name '{ship_type_name}' to ID")
        search_result = await esi_client.search(ship_type_name, ["inventory_type"], strict=True)
        if "inventory_type" in search_result and search_result["inventory_type"]:
            ship_type_id = search_result["inventory_type"][0]
            logger.info(f"Resolved ship type name '{ship_type_name}' to ID {ship_type_id}")
        else:
            logger.error(f"Ship type '{ship_type_name}' not found")
            return {"error": f"Ship type '{ship_type_name}' not found"}
    
    # Construct the zKillboard API URL according to their documentation
    # https://github.com/zKillboard/zKillboard/wiki/API-(Killmails)
    zkillboard_base_url = "https://zkillboard.com/api"
    
    # Build the URL path with modifiers
    url_parts = [zkillboard_base_url]
    
    # Add kill/loss filter
    if losses_only:
        url_parts.append("losses")
    elif kills_only:
        url_parts.append("kills")
    
    # Add entity filters
    if character_id:
        url_parts.append(f"characterID/{character_id}")
    elif corporation_id:
        url_parts.append(f"corporationID/{corporation_id}")
    elif alliance_id:
        url_parts.append(f"allianceID/{alliance_id}")
    
    # Add ship type filter
    if ship_type_id:
        url_parts.append(f"shipTypeID/{ship_type_id}")
    
    # Add page limit
    if limit and limit > 0:
        # Ensure limit doesn't exceed 200 (zkillboard max)
        actual_limit = min(limit, 200)
        url_parts.append(f"page/1")  # Always start with page 1
    
    # Ensure URL ends with a forward slash
    api_url = "/".join(url_parts) + "/"
    
    logger.info(f"Fetching killmail data from zKillboard: {api_url}")
    
    try:
        # Make the request to zKillboard with proper headers as required by their documentation
        headers = {
            "User-Agent": "Rataura/1.0.0 (EVE Online Livekit Agent; https://github.com/alepmalagon/rataura; maintainer: alepmalagon@github.com)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip"
        }
        
        async with aiohttp.ClientSession() as session:
            # Add a delay to avoid rate limiting
            await asyncio.sleep(2)
            
            async with session.get(api_url, headers=headers) as response:
                if response.status == 200:
                    try:
                        # Try to parse the response as JSON
                        content_type = response.headers.get('Content-Type', '')
                        logger.info(f"Response content type: {content_type}")
                        
                        # Get the raw content for debugging
                        content = await response.read()
                        logger.info(f"Response size: {len(content)} bytes")
                        
                        # If it's HTML, we need to handle it differently
                        if 'text/html' in content_type:
                            logger.error(f"Received HTML instead of JSON. This might be a rate limit or blocking issue.")
                            return {
                                "error": "zKillboard returned HTML instead of JSON. This is likely due to rate limiting or IP restrictions.",
                                "technical_details": "Try again later or check if your IP is being blocked."
                            }
                        
                        # Try to decode the JSON
                        try:
                            killmails = await response.json()
                            logger.info(f"Retrieved {len(killmails)} killmails from zKillboard")
                        except Exception as e:
                            logger.error(f"Error parsing zKillboard response: {e}")
                            # Try to get the content as text for debugging
                            text_content = content.decode('utf-8', errors='replace')
                            logger.error(f"Response content: {text_content[:200]}...")  # Log first 200 chars
                            return {"error": f"Error parsing zKillboard response: {str(e)}"}
                        
                        # Process the killmails
                        processed_killmails = []
                        for killmail in killmails:
                            try:
                                # Get basic killmail info from the zkillboard response
                                killmail_id = killmail.get("killmail_id")
                                if not killmail_id:
                                    # zkillboard API returns different format than expected
                                    # Try to extract from zkb data
                                    zkb = killmail.get("zkb", {})
                                    killmail_id = zkb.get("killID")
                                
                                # Get timestamp
                                killmail_time = killmail.get("killmail_time")
                                if not killmail_time:
                                    # Try alternative field
                                    killmail_time = killmail.get("killTime")
                                
                                # Get victim info - structure depends on API response format
                                victim = killmail.get("victim", {})
                                victim_id = victim.get("character_id") or victim.get("characterID")
                                victim_name = "Unknown"
                                victim_ship_type_id = victim.get("ship_type_id") or victim.get("shipTypeID")
                                victim_ship_name = "Unknown Ship"
                                
                                # Get attacker info
                                attackers = killmail.get("attackers", [])
                                final_blow_attacker = next((a for a in attackers if a.get("final_blow") == 1), None)
                                final_blow_id = None
                                final_blow_name = "Unknown"
                                final_blow_ship_type_id = None
                                final_blow_ship_name = "Unknown Ship"
                                
                                if final_blow_attacker:
                                    final_blow_id = final_blow_attacker.get("character_id") or final_blow_attacker.get("characterID")
                                    final_blow_ship_type_id = final_blow_attacker.get("ship_type_id") or final_blow_attacker.get("shipTypeID")
                                
                                # Get solar system info
                                solar_system_id = killmail.get("solar_system_id") or killmail.get("solarSystemID")
                                solar_system_name = "Unknown System"
                                
                                # Get zkillboard URL and value
                                zkb = killmail.get("zkb", {})
                                total_value = zkb.get("totalValue", 0)
                                
                                # Resolve IDs to names using ESI API
                                tasks = []
                                
                                # Resolve victim character name
                                if victim_id:
                                    tasks.append(esi_client.get_character(victim_id))
                                
                                # Resolve victim ship name
                                if victim_ship_type_id:
                                    tasks.append(esi_client.get_type(victim_ship_type_id))
                                
                                # Resolve final blow character name
                                if final_blow_id:
                                    tasks.append(esi_client.get_character(final_blow_id))
                                
                                # Resolve final blow ship name
                                if final_blow_ship_type_id:
                                    tasks.append(esi_client.get_type(final_blow_ship_type_id))
                                
                                # Resolve solar system name
                                if solar_system_id:
                                    tasks.append(esi_client.get_system(solar_system_id))
                                
                                # Wait for all tasks to complete
                                results = await asyncio.gather(*tasks, return_exceptions=True)
                                
                                # Process results
                                result_index = 0
                                
                                # Process victim character name
                                if victim_id:
                                    if isinstance(results[result_index], dict):
                                        victim_name = results[result_index].get("name", "Unknown")
                                    result_index += 1
                                
                                # Process victim ship name
                                if victim_ship_type_id:
                                    if isinstance(results[result_index], dict):
                                        victim_ship_name = results[result_index].get("name", "Unknown Ship")
                                    result_index += 1
                                
                                # Process final blow character name
                                if final_blow_id:
                                    if isinstance(results[result_index], dict):
                                        final_blow_name = results[result_index].get("name", "Unknown")
                                    result_index += 1
                                
                                # Process final blow ship name
                                if final_blow_ship_type_id:
                                    if isinstance(results[result_index], dict):
                                        final_blow_ship_name = results[result_index].get("name", "Unknown Ship")
                                    result_index += 1
                                
                                # Process solar system name
                                if solar_system_id:
                                    if isinstance(results[result_index], dict):
                                        solar_system_name = results[result_index].get("name", "Unknown System")
                                    result_index += 1
                                
                                # Create a processed killmail entry
                                processed_killmail = {
                                    "killmail_id": killmail_id,
                                    "killmail_time": killmail_time,
                                    "victim_id": victim_id,
                                    "victim_name": victim_name,
                                    "victim_ship_type_id": victim_ship_type_id,
                                    "victim_ship_name": victim_ship_name,
                                    "final_blow_id": final_blow_id,
                                    "final_blow_name": final_blow_name,
                                    "final_blow_ship_type_id": final_blow_ship_type_id,
                                    "final_blow_ship_name": final_blow_ship_name,
                                    "solar_system_id": solar_system_id,
                                    "solar_system_name": solar_system_name,
                                    "total_value": total_value,
                                    "zkillboard_url": f"https://zkillboard.com/kill/{killmail_id}/",
                                }
                                
                                processed_killmails.append(processed_killmail)
                            except Exception as e:
                                logger.error(f"Error processing killmail: {e}", exc_info=True)
                        
                        # Create a formatted summary
                        entity_name = None
                        entity_type = None
                        
                        if character_id:
                            entity_type = "character"
                            if character_name:
                                entity_name = character_name
                            else:
                                try:
                                    character_info = await esi_client.get_character(character_id)
                                    entity_name = character_info.get("name", f"Character ID {character_id}")
                                except Exception:
                                    entity_name = f"Character ID {character_id}"
                        elif corporation_id:
                            entity_type = "corporation"
                            if corporation_name:
                                entity_name = corporation_name
                            else:
                                try:
                                    corporation_info = await esi_client.get_corporation(corporation_id)
                                    entity_name = corporation_info.get("name", f"Corporation ID {corporation_id}")
                                except Exception:
                                    entity_name = f"Corporation ID {corporation_id}"
                        elif alliance_id:
                            entity_type = "alliance"
                            if alliance_name:
                                entity_name = alliance_name
                            else:
                                try:
                                    alliance_info = await esi_client.get_alliance(alliance_id)
                                    entity_name = alliance_info.get("name", f"Alliance ID {alliance_id}")
                                except Exception:
                                    entity_name = f"Alliance ID {alliance_id}"
                        
                        ship_name = None
                        if ship_type_id:
                            if ship_type_name:
                                ship_name = ship_type_name
                            else:
                                try:
                                    ship_info = await esi_client.get_type(ship_type_id)
                                    ship_name = ship_info.get("name", f"Ship Type ID {ship_type_id}")
                                except Exception:
                                    ship_name = f"Ship Type ID {ship_type_id}"
                        
                        # Create a formatted summary
                        summary = ""
                        
                        if entity_name and ship_name:
                            if losses_only:
                                summary = f"Recent {ship_name} losses for {entity_name}:\n\n"
                            elif kills_only:
                                summary = f"Recent {ship_name} kills for {entity_name}:\n\n"
                            else:
                                summary = f"Recent {ship_name} killmails for {entity_name}:\n\n"
                        elif entity_name:
                            if losses_only:
                                summary = f"Recent losses for {entity_name}:\n\n"
                            elif kills_only:
                                summary = f"Recent kills for {entity_name}:\n\n"
                            else:
                                summary = f"Recent killmails for {entity_name}:\n\n"
                        elif ship_name:
                            if losses_only:
                                summary = f"Recent {ship_name} losses:\n\n"
                            elif kills_only:
                                summary = f"Recent {ship_name} kills:\n\n"
                            else:
                                summary = f"Recent {ship_name} killmails:\n\n"
                        else:
                            summary = "Recent killmails:\n\n"
                        
                        # Add each killmail to the summary
                        for i, killmail in enumerate(processed_killmails):
                            summary += f"{i+1}. "
                            
                            # Format the killmail time
                            killmail_time = killmail.get("killmail_time", "Unknown time")
                            if killmail_time and killmail_time != "Unknown time":
                                try:
                                    # Convert to a more readable format
                                    killmail_time = killmail_time.replace("T", " ").replace("Z", "")
                                except Exception:
                                    pass
                            
                            # Format the ISK value
                            total_value = killmail.get("total_value", 0)
                            if total_value:
                                if total_value >= 1000000000:  # Billions
                                    formatted_value = f"{total_value / 1000000000:.2f}B ISK"
                                elif total_value >= 1000000:  # Millions
                                    formatted_value = f"{total_value / 1000000:.2f}M ISK"
                                elif total_value >= 1000:  # Thousands
                                    formatted_value = f"{total_value / 1000:.2f}K ISK"
                                else:
                                    formatted_value = f"{total_value:.2f} ISK"
                            else:
                                formatted_value = "Unknown value"
                            
                            # Add the killmail details
                            victim_name = killmail.get("victim_name", "Unknown")
                            victim_ship_name = killmail.get("victim_ship_name", "Unknown Ship")
                            final_blow_name = killmail.get("final_blow_name", "Unknown")
                            final_blow_ship_name = killmail.get("final_blow_ship_name", "Unknown Ship")
                            solar_system_name = killmail.get("solar_system_name", "Unknown System")
                            
                            summary += f"{victim_name} lost a {victim_ship_name} ({formatted_value}) in {solar_system_name} on {killmail_time}. "
                            summary += f"Final blow by {final_blow_name} in a {final_blow_ship_name}.\n"
                            summary += f"   zKillboard: {killmail.get('zkillboard_url', 'Unknown')}\n\n"
                        
                        if not processed_killmails:
                            if entity_name and ship_name:
                                if losses_only:
                                    summary = f"No recent {ship_name} losses found for {entity_name}."
                                elif kills_only:
                                    summary = f"No recent {ship_name} kills found for {entity_name}."
                                else:
                                    summary = f"No recent {ship_name} killmails found for {entity_name}."
                            elif entity_name:
                                if losses_only:
                                    summary = f"No recent losses found for {entity_name}."
                                elif kills_only:
                                    summary = f"No recent kills found for {entity_name}."
                                else:
                                    summary = f"No recent killmails found for {entity_name}."
                            elif ship_name:
                                if losses_only:
                                    summary = f"No recent {ship_name} losses found."
                                elif kills_only:
                                    summary = f"No recent {ship_name} kills found."
                                else:
                                    summary = f"No recent {ship_name} killmails found."
                            else:
                                summary = "No recent killmails found."
                        
                        return {
                            "killmails": processed_killmails,
                            "formatted_info": summary,
                        }
                    except Exception as e:
                        logger.error(f"Error processing zKillboard response: {e}", exc_info=True)
                        return {"error": f"Error processing zKillboard response: {str(e)}"}
                else:
                    error_text = await response.text()
                    logger.error(f"zKillboard API error: {response.status} - {error_text}")
                    
                    # Provide a more user-friendly error message for common errors
                    if response.status == 403:
                        return {
                            "error": "Access to zKillboard API is currently restricted. This could be due to rate limiting or IP restrictions.",
                            "technical_details": f"zKillboard API error: {response.status} - {error_text}",
                            "troubleshooting": "Try again later or check if your IP is being blocked. Make sure you're following zKillboard's API usage guidelines."
                        }
                    elif response.status == 404:
                        return {
                            "error": "The requested resource was not found on zKillboard.",
                            "technical_details": f"zKillboard API error: {response.status} - {error_text}"
                        }
                    elif response.status == 429:
                        return {
                            "error": "You've been rate limited by zKillboard. Please wait before making more requests.",
                            "technical_details": f"zKillboard API error: {response.status} - {error_text}"
                        }
                    
                    return {"error": f"zKillboard API error: {response.status} - {error_text}"}
    except Exception as e:
        logger.error(f"Error getting killmail info: {e}", exc_info=True)
        return {"error": f"Error getting killmail info: {str(e)}"}
