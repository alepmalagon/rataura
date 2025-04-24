"""
LLM function tools module for the Rataura application.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Callable
import openai
from rataura.config import settings
from rataura.esi.client import get_esi_client

# Configure logging
logger = logging.getLogger(__name__)

# Configure LLM API keys
if settings.llm_provider_name.lower() == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key or settings.llm_api_key)
else:
    # Default to OpenAI
    openai.api_key = settings.llm_api_key


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
                    "description": "The name of the alliance (will be resolved to an ID)"
                }
            },
            "required": []
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
        Dict[str, Any]: Information about the alliance.
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
        alliance_info = await esi_client.get_alliance(alliance_id)
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
        search_result = await esi_client.search(character_name, ["character"], strict=True)
        if "character" in search_result and search_result["character"]:
            character_id = search_result["character"][0]
        else:
            return {"error": f"Character '{character_name}' not found"}
    
    if not character_id:
        return {"error": "No character ID or name provided"}
    
    try:
        character_info = await esi_client.get_character(character_id)
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
        logger.error(f"Error getting item type info: {e}")
        return {"error": f"Error getting item type info: {str(e)}"}


async def get_market_prices(type_id: Optional[int] = None, type_name: Optional[str] = None, region_id: Optional[int] = None, region_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get market prices for EVE Online items.
    
    Args:
        type_id (Optional[int], optional): The ID of the item type.
        type_name (Optional[str], optional): The name of the item type.
        region_id (Optional[int], optional): The ID of the region.
        region_name (Optional[str], optional): The name of the region.
    
    Returns:
        Dict[str, Any]: Market prices for the item.
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
    
    # Resolve region name to ID if provided
    if region_name and not region_id:
        search_result = await esi_client.search(region_name, ["region"], strict=True)
        if "region" in search_result and search_result["region"]:
            region_id = search_result["region"][0]
        else:
            return {"error": f"Region '{region_name}' not found"}
    
    # If no region is specified, use The Forge (Jita)
    if not region_id:
        region_id = 10000002  # The Forge
    
    try:
        # Get market orders for the item in the region
        market_orders = await esi_client.get_market_orders(region_id, type_id)
        
        # Process the orders
        buy_orders = [order for order in market_orders if order.get("is_buy_order", False)]
        sell_orders = [order for order in market_orders if not order.get("is_buy_order", False)]
        
        # Calculate statistics
        highest_buy = max(buy_orders, key=lambda x: x["price"])["price"] if buy_orders else None
        lowest_sell = min(sell_orders, key=lambda x: x["price"])["price"] if sell_orders else None
        
        # Get item info
        type_info = await esi_client.get_type(type_id)
        
        # Get region info
        region_info = await esi_client.get_region(region_id)
        
        return {
            "type_id": type_id,
            "type_name": type_info.get("name"),
            "region_id": region_id,
            "region_name": region_info.get("name"),
            "highest_buy": highest_buy,
            "lowest_sell": lowest_sell,
            "buy_orders_count": len(buy_orders),
            "sell_orders_count": len(sell_orders),
        }
    except Exception as e:
        logger.error(f"Error getting market prices: {e}")
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
        search_result = await esi_client.search(system_name, ["solar_system"], strict=True)
        if "solar_system" in search_result and search_result["solar_system"]:
            system_id = search_result["solar_system"][0]
        else:
            return {"error": f"Solar system '{system_name}' not found"}
    
    if not system_id:
        return {"error": "No solar system ID or name provided"}
    
    try:
        system_info = await esi_client.get_system(system_id)
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
        search_result = await esi_client.search(region_name, ["region"], strict=True)
        if "region" in search_result and search_result["region"]:
            region_id = search_result["region"][0]
        else:
            return {"error": f"Region '{region_name}' not found"}
    
    if not region_id:
        return {"error": "No region ID or name provided"}
    
    try:
        region_info = await esi_client.get_region(region_id)
        return region_info
    except Exception as e:
        logger.error(f"Error getting region info: {e}")
        return {"error": f"Error getting region info: {str(e)}"}


# Function mapping
FUNCTION_MAP = {
    "get_alliance_info": get_alliance_info,
    "get_character_info": get_character_info,
    "get_corporation_info": get_corporation_info,
    "get_item_info": get_item_info,
    "get_market_prices": get_market_prices,
    "search_entities": search_entities,
    "get_system_info": get_system_info,
    "get_region_info": get_region_info,
}


async def process_message(message: str) -> str:
    """
    Process a message with the LLM and execute any function calls.
    
    Args:
        message (str): The message to process.
    
    Returns:
        str: The response from the LLM.
    """
    try:
        # Create the messages for the LLM
        system_prompt = "You are a helpful assistant that provides information about EVE Online. You have access to the EVE Online ESI API through function calls. Use these functions to get accurate information about the game."
        
        if settings.llm_provider_name.lower() == "gemini":
            try:
                # Use Google's Gemini model
                model = genai.GenerativeModel(
                    model_name=settings.gemini_model,
                    generation_config={"temperature": 0.7},
                    tools=FUNCTION_DEFINITIONS
                )
                
                # Create the chat session
                chat = model.start_chat(history=[])
                
                # Send the message
                response = chat.send_message(
                    f"{system_prompt}\n\nUser message: {message}"
                )
                
                # Check if there are function calls
                if hasattr(response, 'candidates') and response.candidates and hasattr(response.candidates[0], 'content') and response.candidates[0].content:
                    for part in response.candidates[0].content:
                        if hasattr(part, 'function_call'):
                            # Get the function call details
                            function_name = part.function_call.name
                            function_args = {}
                            for param in part.function_call.args:
                                function_args[param] = part.function_call.args[param]
                            
                            # Call the function
                            function_response = await FUNCTION_MAP[function_name](**function_args)
                            
                            # Send the function response back to the model
                            response = chat.send_message(
                                f"Function {function_name} returned: {json.dumps(function_response)}"
                            )
                            
                            # Return the final response
                            return response.text
                
                # If no function calls, return the response text
                return response.text
                
            except Exception as e:
                logger.exception(f"Error using Gemini: {e}")
                # Fall back to OpenAI if Gemini fails
                logger.warning("Falling back to OpenAI due to Gemini error")
        
        # Default to OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]
        
        # Call the LLM
        response = await openai.ChatCompletion.acreate(
            model=settings.llm_model,
            messages=messages,
            functions=FUNCTION_DEFINITIONS,
            function_call="auto",
        )
        
        # Get the response message
        response_message = response["choices"][0]["message"]
        
        # Check if the LLM wants to call a function
        if response_message.get("function_call"):
            # Get the function call details
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(response_message["function_call"]["arguments"])
            
            # Call the function
            function_response = await FUNCTION_MAP[function_name](**function_args)
            
            # Add the function response to the messages
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_response),
                }
            )
            
            # Call the LLM again with the function response
            second_response = await openai.ChatCompletion.acreate(
                model=settings.llm_model,
                messages=messages,
            )
            
            # Return the final response
            return second_response["choices"][0]["message"]["content"]
        else:
            # Return the response from the LLM
            return response_message["content"]
    except Exception as e:
        logger.exception(f"Error processing message: {e}")
        return f"I'm sorry, but I encountered an error while processing your message: {str(e)}"
