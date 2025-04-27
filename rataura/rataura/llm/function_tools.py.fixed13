# This is a simplified version of the function_tools.py file
# with the problematic get_killmail_info function removed

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp
from livekit.agents import AgentContext

from rataura.config import settings
from rataura.esi.client import ESIClient

# Set up logging
logger = logging.getLogger("rataura-agent")

# Initialize ESI client
esi_client = ESIClient(
    client_id=settings.eve_client_id,
    client_secret=settings.eve_client_secret,
    callback_url=settings.eve_callback_url,
)

# Function implementations from the original file
# ... (copy all the functions except get_killmail_info)

async def get_alliance_info(
    alliance_id: Optional[int] = None,
    alliance_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about an EVE Online alliance.
    """
    logger.info(f"Looking up alliance info for ID: {alliance_id}, Name: {alliance_name}")
    
    try:
        # If only name is provided, look up the ID
        if alliance_name and not alliance_id:
            search_result = await esi_client.search(alliance_name, ["alliance"], strict=True)
            logger.info(f"Search result for alliance '{alliance_name}': {search_result}")
            
            if "alliance" in search_result and search_result["alliance"]:
                alliance_id = search_result["alliance"][0]
                logger.info(f"Resolved alliance name '{alliance_name}' to ID {alliance_id}")
            else:
                return {"error": f"Alliance '{alliance_name}' not found"}
        
        # If no ID is available, return an error
        if not alliance_id:
            return {"error": "No alliance ID or name provided"}
        
        # Get alliance information
        alliance_info = await esi_client.get_alliance(alliance_id)
        
        # Get creator information
        creator_id = alliance_info.get("creator_id")
        creator_info = await esi_client.get_character(creator_id) if creator_id else None
        creator_name = creator_info.get("name", f"character ID {creator_id}") if creator_info else f"character ID {creator_id}"
        
        # Get creator corporation information
        creator_corporation_id = alliance_info.get("creator_corporation_id")
        creator_corporation_info = await esi_client.get_corporation(creator_corporation_id) if creator_corporation_id else None
        creator_corporation_name = creator_corporation_info.get("name", f"corporation ID {creator_corporation_id}") if creator_corporation_info else f"corporation ID {creator_corporation_id}"
        
        # Get executor corporation information
        executor_corporation_id = alliance_info.get("executor_corporation_id")
        executor_corporation_info = await esi_client.get_corporation(executor_corporation_id) if executor_corporation_id else None
        executor_corporation_name = executor_corporation_info.get("name", f"corporation ID {executor_corporation_id}") if executor_corporation_info else f"corporation ID {executor_corporation_id}"
        
        # Get faction information
        faction_id = alliance_info.get("faction_id")
        faction_info = await esi_client.get_faction(faction_id) if faction_id else None
        faction_name = faction_info.get("name", f"faction ID {faction_id}") if faction_info else "no faction"
        
        # Format the response
        alliance_name = alliance_info.get("name", f"Alliance ID {alliance_id}")
        alliance_ticker = alliance_info.get("ticker", "")
        date_founded = alliance_info.get("date_founded", "unknown date")
        
        response = (
            f"{alliance_name} ({alliance_ticker}) was founded on {date_founded}. "
            f"The creator was {creator_name}, of corporation {creator_corporation_name}. "
            f"The executor corporation is {executor_corporation_name}. "
        )
        
        if faction_id:
            response += f"They are aligned with the {faction_name}."
        else:
            response += "They are not aligned with any faction."
        
        return {"alliance_info": response}
    
    except Exception as e:
        logger.error(f"Error getting alliance info: {e}", exc_info=True)
        return {"error": f"Error getting alliance info: {str(e)}"}

async def get_character_info(
    character_id: Optional[int] = None,
    character_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about an EVE Online character.
    """
    logger.info(f"Looking up character info for ID: {character_id}, Name: {character_name}")
    
    try:
        # If only name is provided, look up the ID
        if character_name and not character_id:
            search_result = await esi_client.search(character_name, ["character"], strict=True)
            logger.info(f"Search result for character '{character_name}': {search_result}")
            
            if "character" in search_result and search_result["character"]:
                character_id = search_result["character"][0]
                logger.info(f"Resolved character name '{character_name}' to ID {character_id}")
            else:
                return {"error": f"Character '{character_name}' not found"}
        
        # If no ID is available, return an error
        if not character_id:
            return {"error": "No character ID or name provided"}
        
        # Get character information
        character_info = await esi_client.get_character(character_id)
        
        # Get corporation information
        corporation_id = character_info.get("corporation_id")
        corporation_info = await esi_client.get_corporation(corporation_id) if corporation_id else None
        corporation_name = corporation_info.get("name", f"corporation ID {corporation_id}") if corporation_info else "no corporation"
        
        # Get alliance information if available
        alliance_id = character_info.get("alliance_id")
        alliance_info = await esi_client.get_alliance(alliance_id) if alliance_id else None
        alliance_name = alliance_info.get("name", f"alliance ID {alliance_id}") if alliance_info else "no alliance"
        
        # Format the response
        character_name = character_info.get("name", f"Character ID {character_id}")
        gender = character_info.get("gender", "unknown gender")
        birthday = character_info.get("birthday", "unknown date")
        bloodline_id = character_info.get("bloodline_id")
        race_id = character_info.get("race_id")
        security_status = character_info.get("security_status", 0)
        
        # Get bloodline and race names
        bloodline_info = await esi_client.get_bloodline(bloodline_id) if bloodline_id else None
        race_info = await esi_client.get_race(race_id) if race_id else None
        
        bloodline_name = bloodline_info.get("name", f"bloodline ID {bloodline_id}") if bloodline_info else "unknown bloodline"
        race_name = race_info.get("name", f"race ID {race_id}") if race_info else "unknown race"
        
        response = (
            f"{character_name} is a {gender} character born on {birthday}, belonging to "
            f"the {bloodline_name} bloodline and {race_name} race. "
        )
        
        if alliance_id:
            response += f"They are a member of the {alliance_name} and the corporation {corporation_name}. "
        else:
            response += f"They are a member of the corporation {corporation_name}. "
        
        response += f"Their security status is {security_status:.9f}."
        
        return {"character_info": response}
    
    except Exception as e:
        logger.error(f"Error getting character info: {e}", exc_info=True)
        return {"error": f"Error getting character info: {str(e)}"}

async def get_corporation_info(
    corporation_id: Optional[int] = None,
    corporation_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about an EVE Online corporation.
    """
    logger.info(f"Looking up corporation info for ID: {corporation_id}, Name: {corporation_name}")
    
    try:
        # If only name is provided, look up the ID
        if corporation_name and not corporation_id:
            search_result = await esi_client.search(corporation_name, ["corporation"], strict=True)
            logger.info(f"Search result for corporation '{corporation_name}': {search_result}")
            
            if "corporation" in search_result and search_result["corporation"]:
                corporation_id = search_result["corporation"][0]
                logger.info(f"Resolved corporation name '{corporation_name}' to ID {corporation_id}")
            else:
                return {"error": f"Corporation '{corporation_name}' not found"}
        
        # If no ID is available, return an error
        if not corporation_id:
            return {"error": "No corporation ID or name provided"}
        
        # Get corporation information
        corporation_info = await esi_client.get_corporation(corporation_id)
        
        # Get alliance information if available
        alliance_id = corporation_info.get("alliance_id")
        alliance_info = await esi_client.get_alliance(alliance_id) if alliance_id else None
        alliance_name = alliance_info.get("name", f"alliance ID {alliance_id}") if alliance_info else "no alliance"
        
        # Get CEO information
        ceo_id = corporation_info.get("ceo_id")
        ceo_info = await esi_client.get_character(ceo_id) if ceo_id else None
        ceo_name = ceo_info.get("name", f"character ID {ceo_id}") if ceo_info else f"character ID {ceo_id}"
        
        # Get creator information
        creator_id = corporation_info.get("creator_id")
        creator_info = await esi_client.get_character(creator_id) if creator_id else None
        creator_name = creator_info.get("name", f"character ID {creator_id}") if creator_info else f"character ID {creator_id}"
        
        # Get faction information
        faction_id = corporation_info.get("faction_id")
        faction_info = await esi_client.get_faction(faction_id) if faction_id else None
        faction_name = faction_info.get("name", f"faction ID {faction_id}") if faction_info else "no faction"
        
        # Format the response
        corporation_name = corporation_info.get("name", f"Corporation ID {corporation_id}")
        corporation_ticker = corporation_info.get("ticker", "")
        member_count = corporation_info.get("member_count", 0)
        date_founded = corporation_info.get("date_founded", "unknown date")
        tax_rate = corporation_info.get("tax_rate", 0)
        
        response = (
            f"{corporation_name} [{corporation_ticker}] was founded on {date_founded} by {creator_name}. "
            f"The current CEO is {ceo_name}. "
            f"They have {member_count} members and a tax rate of {tax_rate * 100:.1f}%. "
        )
        
        if alliance_id:
            response += f"They are a member of the {alliance_name} alliance. "
        
        if faction_id:
            response += f"They are aligned with the {faction_name}."
        else:
            response += "They are not aligned with any faction."
        
        return {"corporation_info": response}
    
    except Exception as e:
        logger.error(f"Error getting corporation info: {e}", exc_info=True)
        return {"error": f"Error getting corporation info: {str(e)}"}

async def get_market_prices(
    type_id: Optional[int] = None,
    type_name: Optional[str] = None,
    region_id: Optional[int] = None,
    region_name: Optional[str] = None,
    system_id: Optional[int] = None,
    system_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get market prices for an item in a specific region or system.
    
    This function retrieves current buy and sell orders for a specified item type
    in a given region or solar system. It provides the highest buy price and lowest
    sell price, along with the number of orders and their locations.
    
    Parameters:
    - type_id: The ID of the item type to look up
    - type_name: The name of the item type to look up (will be resolved to an ID)
    - region_id: The ID of the region to search in
    - region_name: The name of the region to search in (will be resolved to an ID)
    - system_id: The ID of the solar system to filter by
    - system_name: The name of the solar system to filter by (will be resolved to an ID)
    
    Returns a dictionary with market information or an error message.
    """
    logger.info(f"Looking up market prices for Type ID: {type_id}, Type Name: {type_name}, "
                f"Region ID: {region_id}, Region Name: {region_name}, "
                f"System ID: {system_id}, System Name: {system_name}")
    
    try:
        # If only type name is provided, look up the ID
        if type_name and not type_id:
            logger.info(f"Resolving type name '{type_name}' to ID")
            search_result = await esi_client.search(type_name, ["inventory_type"], strict=True)
            logger.info(f"Search result for type '{type_name}': {search_result}")
            
            if "inventory_type" in search_result and search_result["inventory_type"]:
                type_id = search_result["inventory_type"][0]
                logger.info(f"Resolved type name '{type_name}' to ID {type_id}")
            else:
                return {"error": f"Item type '{type_name}' not found"}
        
        # If no type ID is available, return an error
        if not type_id:
            return {"error": "No item type ID or name provided"}
        
        # If system name is provided, look up the ID
        if system_name and not system_id:
            logger.info(f"Resolving system name '{system_name}' to ID")
            search_result = await esi_client.search(system_name, ["solar_system"], strict=True)
            logger.info(f"Search result for system '{system_name}': {search_result}")
            
            if "solar_system" in search_result and search_result["solar_system"]:
                system_id = search_result["solar_system"][0]
                logger.info(f"Resolved system name '{system_name}' to ID {system_id}")
            else:
                return {"error": f"Solar system '{system_name}' not found"}
        
        # If system ID is provided but no region, get the region ID from the system
        if system_id and not region_id:
            logger.info(f"Getting region ID for system ID {system_id}")
            system_info = await esi_client.get_system(system_id)
            constellation_id = system_info.get("constellation_id")
            
            if constellation_id:
                constellation_info = await esi_client.get_constellation(constellation_id)
                region_id = constellation_info.get("region_id")
                logger.info(f"System {system_id} is in region {region_id}")
            
            if not region_id:
                # Default to The Forge (Jita) if we can't determine the region
                region_id = 10000002
                logger.info(f"No region specified, using The Forge (ID: {region_id})")
        
        # If only region name is provided, look up the ID
        if region_name and not region_id:
            logger.info(f"Resolving region name '{region_name}' to ID")
            search_result = await esi_client.search(region_name, ["region"], strict=True)
            logger.info(f"Search result for region '{region_name}': {search_result}")
            
            if "region" in search_result and search_result["region"]:
                region_id = search_result["region"][0]
                logger.info(f"Resolved region name '{region_name}' to ID {region_id}")
            else:
                return {"error": f"Region '{region_name}' not found"}
        
        # If no region ID is available, default to The Forge (Jita)
        if not region_id:
            region_id = 10000002
            logger.info(f"No region specified, using The Forge (ID: {region_id})")
        
        # Get market orders for the specified type in the specified region
        logger.info(f"Getting market orders for type ID {type_id} in region ID {region_id}")
        market_orders = await esi_client.get_market_orders(region_id, type_id)
        logger.info(f"Found {len(market_orders)} market orders")
        
        if market_orders:
            logger.info(f"Sample market order: {market_orders[0]}")
        
        # Filter by system if specified
        if system_id:
            logger.info(f"Filtering market orders by system ID {system_id}")
            filtered_orders = [order for order in market_orders if order.get("system_id") == system_id]
            logger.info(f"Filtered from {len(market_orders)} to {len(filtered_orders)} orders in system {system_name or system_id}")
            market_orders = filtered_orders
        
        if not market_orders:
            if system_id:
                return {"error": f"No market orders found for {type_name or f'type ID {type_id}'} in the {system_name or f'system ID {system_id}'}."}
            else:
                return {"error": f"No market orders found for {type_name or f'type ID {type_id}'} in the {region_name or f'region ID {region_id}'}."}
        
        # Get item type information
        type_info = await esi_client.get_type(type_id)
        type_name = type_info.get("name", f"Type ID {type_id}")
        
        # Get region information
        region_info = await esi_client.get_region(region_id)
        region_name = region_info.get("name", f"Region ID {region_id}")
        
        # Get system information if specified
        system_name = None
        if system_id:
            system_info = await esi_client.get_system(system_id)
            system_name = system_info.get("name", f"System ID {system_id}")
        
        # Separate buy and sell orders
        buy_orders = [order for order in market_orders if order.get("is_buy_order", False)]
        sell_orders = [order for order in market_orders if not order.get("is_buy_order", False)]
        
        # Sort buy orders by price (descending)
        buy_orders.sort(key=lambda x: x.get("price", 0), reverse=True)
        
        # Sort sell orders by price (ascending)
        sell_orders.sort(key=lambda x: x.get("price", 0))
        
        # Get highest buy order and lowest sell order
        highest_buy = buy_orders[0] if buy_orders else None
        lowest_sell = sell_orders[0] if sell_orders else None
        
        # Format the response
        response = {}
        
        if system_id:
            response["location_type"] = "system"
            response["location_name"] = system_name or f"System ID {system_id}"
        else:
            response["location_type"] = "region"
            response["location_name"] = region_name
        
        response["item_name"] = type_name
        
        # Get station information for the orders
        if highest_buy:
            highest_buy_location_id = highest_buy.get("location_id")
            highest_buy_location_info = await esi_client.get_station(highest_buy_location_id)
            highest_buy_location_name = highest_buy_location_info.get("name", f"Location ID {highest_buy_location_id}")
            highest_buy_system_id = highest_buy.get("system_id")
            highest_buy_system_info = await esi_client.get_system(highest_buy_system_id)
            highest_buy_system_name = highest_buy_system_info.get("name", f"System ID {highest_buy_system_id}")
            
            response["highest_buy"] = {
                "price": highest_buy.get("price", 0),
                "volume": highest_buy.get("volume_remain", 0),
                "location_id": highest_buy_location_id,
                "location_name": highest_buy_location_name,
                "system_id": highest_buy_system_id,
                "system_name": highest_buy_system_name,
                "order_count": len(buy_orders)
            }
        
        if lowest_sell:
            lowest_sell_location_id = lowest_sell.get("location_id")
            lowest_sell_location_info = await esi_client.get_station(lowest_sell_location_id)
            lowest_sell_location_name = lowest_sell_location_info.get("name", f"Location ID {lowest_sell_location_id}")
            lowest_sell_system_id = lowest_sell.get("system_id")
            lowest_sell_system_info = await esi_client.get_system(lowest_sell_system_id)
            lowest_sell_system_name = lowest_sell_system_info.get("name", f"System ID {lowest_sell_system_id}")
            
            response["lowest_sell"] = {
                "price": lowest_sell.get("price", 0),
                "volume": lowest_sell.get("volume_remain", 0),
                "location_id": lowest_sell_location_id,
                "location_name": lowest_sell_location_name,
                "system_id": lowest_sell_system_id,
                "system_name": lowest_sell_system_name,
                "order_count": len(sell_orders)
            }
        
        # Format a human-readable response
        formatted_response = f"Market prices for {type_name} in {response['location_name']}:\n\n"
        
        if "highest_buy" in response:
            formatted_response += f"Highest buy: {response['highest_buy']['price']:,.2f} ISK ({response['highest_buy']['order_count']} orders) "
            formatted_response += f"at {response['highest_buy']['location_name']} in {response['highest_buy']['system_name']}\n"
        else:
            formatted_response += "No buy orders found.\n"
        
        if "lowest_sell" in response:
            formatted_response += f"Lowest sell: {response['lowest_sell']['price']:,.2f} ISK ({response['lowest_sell']['order_count']} orders) "
            formatted_response += f"at {response['lowest_sell']['location_name']} in {response['lowest_sell']['system_name']}"
        else:
            formatted_response += "No sell orders found."
        
        response["formatted"] = formatted_response
        return response
    
    except Exception as e:
        logger.error(f"Error getting market prices: {e}", exc_info=True)
        return {"error": f"Error getting market prices: {str(e)}"}

async def get_system_info(
    system_id: Optional[int] = None,
    system_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about an EVE Online solar system.
    """
    logger.info(f"Looking up system info for ID: {system_id}, Name: {system_name}")
    
    try:
        # If only name is provided, look up the ID
        if system_name and not system_id:
            search_result = await esi_client.search(system_name, ["solar_system"], strict=True)
            logger.info(f"Search result for system '{system_name}': {search_result}")
            
            if "solar_system" in search_result and search_result["solar_system"]:
                system_id = search_result["solar_system"][0]
                logger.info(f"Resolved system name '{system_name}' to ID {system_id}")
            else:
                return {"error": f"System '{system_name}' not found"}
        
        # If no ID is available, return an error
        if not system_id:
            return {"error": "No system ID or name provided"}
        
        # Get system information
        system_info = await esi_client.get_system(system_id)
        
        # Get constellation information
        constellation_id = system_info.get("constellation_id")
        constellation_info = await esi_client.get_constellation(constellation_id) if constellation_id else None
        constellation_name = constellation_info.get("name", f"constellation ID {constellation_id}") if constellation_info else "unknown constellation"
        
        # Get region information
        region_id = constellation_info.get("region_id") if constellation_info else None
        region_info = await esi_client.get_region(region_id) if region_id else None
        region_name = region_info.get("name", f"region ID {region_id}") if region_info else "unknown region"
        
        # Get system details
        system_name = system_info.get("name", f"System ID {system_id}")
        security_status = system_info.get("security_status", 0)
        security_class = system_info.get("security_class", "null")
        
        # Get planets
        planets = system_info.get("planets", [])
        planet_count = len(planets)
        
        # Get stargates
        stargates = system_info.get("stargates", [])
        stargate_count = len(stargates)
        
        # Get stations
        stations = system_info.get("stations", [])
        station_count = len(stations)
        
        # Determine security level description
        if security_status >= 0.5:
            security_description = "high-security"
        elif security_status > 0.0:
            security_description = "low-security"
        else:
            security_description = "null-security"
        
        # Format the response
        response = (
            f"{system_name} is located in the {constellation_name} constellation in the {region_name} region. "
            f"It is a {security_description} system with a security rating of {security_status:.1f}. "
            f"The system contains {planet_count} planets. "
        )
        
        if stargate_count > 0:
            response += f"There are {stargate_count} stargates. "
        else:
            response += "There are no stargates. "
        
        if station_count > 0:
            response += f"The system has {station_count} stations."
        else:
            response += "There are no stations in this system."
        
        return {"system_info": response}
    
    except Exception as e:
        logger.error(f"Error getting system info: {e}", exc_info=True)
        return {"error": f"Error getting system info: {str(e)}"}

async def get_region_info(
    region_id: Optional[int] = None,
    region_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about an EVE Online region.
    """
    logger.info(f"Looking up region info for ID: {region_id}, Name: {region_name}")
    
    try:
        # If only name is provided, look up the ID
        if region_name and not region_id:
            search_result = await esi_client.search(region_name, ["region"], strict=True)
            logger.info(f"Search result for region '{region_name}': {search_result}")
            
            if "region" in search_result and search_result["region"]:
                region_id = search_result["region"][0]
                logger.info(f"Resolved region name '{region_name}' to ID {region_id}")
            else:
                return {"error": f"Region '{region_name}' not found"}
        
        # If no ID is available, return an error
        if not region_id:
            return {"error": "No region ID or name provided"}
        
        # Get region information
        region_info = await esi_client.get_region(region_id)
        
        # Get constellations
        constellation_ids = region_info.get("constellations", [])
        constellation_count = len(constellation_ids)
        
        # Get a sample of constellation names
        constellation_names = []
        for i, constellation_id in enumerate(constellation_ids[:5]):  # Get first 5 constellations
            constellation_info = await esi_client.get_constellation(constellation_id)
            if constellation_info:
                constellation_names.append(constellation_info.get("name", f"Constellation ID {constellation_id}"))
        
        # Format the response
        region_name = region_info.get("name", f"Region ID {region_id}")
        description = region_info.get("description", "No description available.")
        
        response = (
            f"{region_name} is a region in EVE Online containing {constellation_count} constellations. "
        )
        
        if constellation_names:
            response += f"Some constellations in this region include: {', '.join(constellation_names)}"
            if constellation_count > 5:
                response += f", and {constellation_count - 5} more."
            else:
                response += "."
        
        return {"region_info": response}
    
    except Exception as e:
        logger.error(f"Error getting region info: {e}", exc_info=True)
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
    losses_only: bool = False,
    kills_only: bool = False,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Get killmail information for a character, corporation, alliance, or ship type.
    """
    logger.info(f"Getting killmail info for character ID: {character_id}, name: {character_name}, "
                f"corporation ID: {corporation_id}, name: {corporation_name}, "
                f"alliance ID: {alliance_id}, name: {alliance_name}, "
                f"ship type ID: {ship_type_id}, name: {ship_type_name}, "
                f"losses_only: {losses_only}, kills_only: {kills_only}, limit: {limit}")
    
    try:
        return {"error": "Killmail information is temporarily unavailable."}
    except Exception as e:
        logger.error(f"Error getting killmail info: {e}", exc_info=True)
        return {"error": f"Error getting killmail info: {str(e)}"}
