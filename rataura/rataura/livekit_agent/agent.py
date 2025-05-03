"""
Livekit agent module for the Rataura application.
This module implements a Livekit 1.0 worker that includes the LLM tool functions for the ESI API.
"""

import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import asyncio
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    WorkerOptions,
    cli,
)
from livekit.agents.llm import function_tool, ChatContext
from livekit.plugins import google, silero

from rataura.config import settings
from rataura.esi.client import get_esi_client
from rataura.llm.function_tools import (
    get_alliance_info,
    get_character_info,
    get_corporation_info,
    get_item_info,
    get_market_prices,
    search_entities,
    get_system_info,
    get_region_info,
    get_killmail_info,
)
from rataura.llm.fw_tools import (
    get_fw_warzone_status,
    get_fw_system_info,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s %(name)s - %(message)s",
)
# Suppress websockets debug messages
logging.getLogger("websockets.client").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)

logger = logging.getLogger("rataura-agent")
load_dotenv()

class RatauraAgent(Agent):
    """
    Livekit agent for the Rataura application with configurable voice/text support.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Rataura agent with configurable voice/text capabilities.
        """
        mode = "voice and text" if settings.voice_enabled else "text-only"
        logger.info(f"Initializing RatauraAgent in {mode} mode...")
        
        agent_args = {
            "instructions": (
                "You are Rataura, a helpful assistant for EVE Online players. "
                "You have access to the EVE Online ESI API through function calls. "
                "Use these functions to get accurate information about the game. "
                "Keep your responses concise and to the point. "
                "You are knowledgeable about EVE Online game mechanics, items, ships, corporations, alliances, and more. "
                "When users ask about game information, use the appropriate function to get the most accurate data."
            ),
            # Use Gemini multimodal model for LLM
            "llm": google.beta.realtime.RealtimeModel(),
        }
        
        # Only add VAD if voice is enabled
        if settings.voice_enabled:
            agent_args["vad"] = silero.VAD.load()
            
        super().__init__(**agent_args)
        
        logger.info(f"RatauraAgent initialized successfully in {mode} mode")
    
    async def on_enter(self):
        """
        Called when the agent enters the room.
        """
        logger.info("Agent entered the room, sending introduction")
        
        # Customize introduction based on mode
        if settings.voice_enabled:
            intro_instructions = "Introduce yourself as Rataura, a voice and text assistant for EVE Online. Keep it brief and friendly."
        else:
            intro_instructions = "Introduce yourself as Rataura, a text assistant for EVE Online. Keep it brief and friendly."
            
        self.session.generate_reply(
            instructions=intro_instructions
        )
    
    async def on_text(self, text: str, ctx: ChatContext) -> None:
        """
        Called when a text message is received.
        This is the main entry point for chat messages.
        """
        logger.info(f"Received text message: {text}")
        
        # Generate a reply to the text message
        response = await self.session.generate_reply(ctx)
        
        # The response will be automatically sent to the transcription stream
        # by the AgentSession
        logger.info(f"Generated response: {response}")
    
    # Function tools for the LLM
    
    @function_tool
    async def get_alliance_info_tool(
        self,
        alliance_id: Optional[int] = None,
        alliance_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get information about an EVE Online alliance.
        
        Args:
            alliance_id: The ID of the alliance
            alliance_name: The name of the alliance (will be resolved to an ID)
        """
        logger.info(f"Looking up alliance info for ID: {alliance_id}, Name: {alliance_name}")
        result = await get_alliance_info(alliance_id, alliance_name)
        
        # If we have a formatted_info field, return it directly for better readability
        if "formatted_info" in result:
            return {"info": result["formatted_info"]}
        
        return result
    
    @function_tool
    async def get_character_info_tool(
        self,
        character_id: Optional[int] = None,
        character_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get information about an EVE Online character.
        
        Args:
            character_id: The ID of the character
            character_name: The name of the character (will be resolved to an ID)
        """
        logger.info(f"Looking up character info for ID: {character_id}, Name: {character_name}")
        result = await get_character_info(character_id, character_name)
        
        # Format a human-readable response
        if "error" in result:
            return result
        
        response = ""
        if "name" in result:
            response += f"{result['name']} is a "
            
            if "gender" in result:
                response += f"{result['gender'].lower()} "
            
            response += "character"
            
            if "birthday" in result:
                response += f" born on {result['birthday']}"
            
            if "bloodline_id" in result:
                bloodlines = {
                    1: "Deteis",
                    2: "Civire",
                    3: "Sebiestor",
                    4: "Brutor",
                    5: "Amarr",
                    6: "Ni-Kunni",
                    7: "Gallente",
                    8: "Intaki",
                    9: "Jin-Mei",
                    10: "Khanid",
                    11: "Vherokior",
                    12: "Achura",
                    13: "Drifter"
                }
                bloodline = bloodlines.get(result["bloodline_id"], "Unknown")
                response += f", belonging to\nthe {bloodline} bloodline"
            
            if "race_id" in result:
                races = {
                    1: "Caldari",
                    2: "Minmatar",
                    3: "Amarr",
                    4: "Gallente",
                    5: "Jove",
                    6: "Pirate"
                }
                race = races.get(result["race_id"], "Unknown")
                response += f" and {race} race"
            
            response += "."
            
            # Add alliance and corporation info
            if "alliance_name" in result and "corporation_name" in result:
                response += f" They are a member of the {result['alliance_name']} and the corporation {result['corporation_name']}."
            elif "corporation_name" in result:
                response += f" They are a member of the corporation {result['corporation_name']}."
            
            if "security_status" in result:
                response += f" Their security status is {result['security_status']}."
        
        result["formatted_info"] = response
        return result
    
    @function_tool
    async def get_corporation_info_tool(
        self,
        corporation_id: Optional[int] = None,
        corporation_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get information about an EVE Online corporation.
        
        Args:
            corporation_id: The ID of the corporation
            corporation_name: The name of the corporation (will be resolved to an ID)
        """
        logger.info(f"Looking up corporation info for ID: {corporation_id}, Name: {corporation_name}")
        result = await get_corporation_info(corporation_id, corporation_name)
        return result
    
    @function_tool
    async def get_item_info_tool(
        self,
        type_id: Optional[int] = None,
        type_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get information about an EVE Online item type.
        
        Args:
            type_id: The ID of the item type
            type_name: The name of the item type (will be resolved to an ID)
        """
        logger.info(f"Looking up item info for ID: {type_id}, Name: {type_name}")
        result = await get_item_info(type_id, type_name)
        return result
    
    @function_tool
    async def get_market_prices_tool(
        self,
        type_id: Optional[int] = None,
        type_name: Optional[str] = None,
        region_id: Optional[int] = None,
        region_name: Optional[str] = None,
        system_id: Optional[int] = None,
        system_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get market prices for EVE Online items. Can be used to find where an item is sold or bought and it's market value.
        
        Args:
            type_id: The ID of the item type
            type_name: The name of the item type (will be resolved to an ID)
            region_id: The ID of the region
            region_name: The name of the region (will be resolved to an ID)
            system_id: The ID of the solar system to filter by
            system_name: The name of the solar system to filter by
        """
        logger.info(f"Looking up market prices for Type ID: {type_id}, Type Name: {type_name}, Region ID: {region_id}, Region Name: {region_name}, System ID: {system_id}, System Name: {system_name}")
        result = await get_market_prices(type_id, type_name, region_id, region_name, system_id, system_name)
        
        # If we have a formatted_info field, return it directly for better readability
        if "formatted_info" in result:
            return {"info": result["formatted_info"]}
            
        # If there's an error, return it
        if "error" in result:
            return {"error": result["error"]}
        
        return result
    
    @function_tool
    async def search_entities_tool(
        self,
        search: str,
        categories: Optional[List[str]] = None,
        strict: bool = False,
    ) -> Dict[str, Any]:
        """
        Search for EVE Online entities by name.
        
        Args:
            search: The search query
            categories: The categories to search in (alliance, character, constellation, corporation, faction, inventory_type, region, solar_system, station)
            strict: Whether to perform a strict search
        """
        logger.info(f"Searching for entities with query: {search}, Categories: {categories}, Strict: {strict}")
        result = await search_entities(search, categories, strict)
        return result
    
    @function_tool
    async def get_system_info_tool(
        self,
        system_id: Optional[int] = None,
        system_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get information about an EVE Online solar system.
        
        Args:
            system_id: The ID of the solar system
            system_name: The name of the solar system (will be resolved to an ID)
        """
        logger.info(f"Looking up system info for ID: {system_id}, Name: {system_name}")
        result = await get_system_info(system_id, system_name)
        
        # Format a human-readable response
        if "error" in result:
            return result
        
        system_name = result.get("name", f"System ID {system_id}")
        constellation_name = result.get("constellation_name", "Unknown")
        region_name = result.get("region_name", "Unknown")
        
        # Create a formatted response
        formatted_response = f"{system_name} is located in the {constellation_name} constellation in the {region_name} region."
        
        # Add security status if available
        if "security_status" in result:
            security = result["security_status"]
            security_level = "high-security" if security >= 0.5 else "low-security" if security > 0.0 else "null-security"
            formatted_response += f" It is a {security_level} system with a security rating of {security:.1f}."
        
        # Add planets if available
        if "planets" in result and result["planets"]:
            planet_count = len(result["planets"])
            formatted_response += f" The system contains {planet_count} planet{'s' if planet_count != 1 else ''}."
        
        # Add stargates if available
        if "stargates" in result and result["stargates"]:
            stargate_count = len(result["stargates"])
            formatted_response += f" There {'are' if stargate_count != 1 else 'is'} {stargate_count} stargate{'s' if stargate_count != 1 else ''}."
        
        # Add stations if available
        if "stations" in result and result["stations"]:
            station_count = len(result["stations"])
            formatted_response += f" The system has {station_count} station{'s' if station_count != 1 else ''}."
        
        result["formatted_info"] = formatted_response
        return result
    
    @function_tool
    async def get_region_info_tool(
        self,
        region_id: Optional[int] = None,
        region_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get information about an EVE Online region.
        
        Args:
            region_id: The ID of the region
            region_name: The name of the region (will be resolved to an ID)
        """
        logger.info(f"Looking up region info for ID: {region_id}, Name: {region_name}")
        result = await get_region_info(region_id, region_name)
        
        # Format a human-readable response
        if "error" in result:
            return result
        
        region_name = result.get("name", f"Region ID {region_id}")
        
        # Create a formatted response
        formatted_response = f"{region_name} is a region in EVE Online."
        
        # Add constellations if available
        if "constellations" in result and result["constellations"]:
            constellation_count = len(result["constellations"])
            formatted_response += f" It contains {constellation_count} constellation{'s' if constellation_count != 1 else ''}."
        
        # Add description if available
        if "description" in result and result["description"]:
            # Clean up HTML tags from description
            description = result["description"].replace("<br>", " ").replace("<br/>", " ")
            # Truncate if too long
            if len(description) > 200:
                description = description[:200] + "..."
            formatted_response += f" {description}"
        
        result["formatted_info"] = formatted_response
        return result
    
    @function_tool
    async def get_killmail_info_tool(
        self,
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
        kills_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Get information about recent killmails for a character, corporation, alliance, or ship type from zKillboard.
        
        Args:
            character_id: The ID of the character to get killmails for
            character_name: The name of the character to get killmails for (will be resolved to an ID)
            corporation_id: The ID of the corporation to get killmails for
            corporation_name: The name of the corporation to get killmails for (will be resolved to an ID)
            alliance_id: The ID of the alliance to get killmails for
            alliance_name: The name of the alliance to get killmails for (will be resolved to an ID)
            ship_type_id: The ID of the ship type to get killmails for
            ship_type_name: The name of the ship type to get killmails for (will be resolved to an ID)
            limit: The maximum number of killmails to return (default: 5)
            losses_only: Whether to only return losses (default: false)
            kills_only: Whether to only return kills (default: false)
        """
        logger.info(f"Looking up killmail info for Character ID: {character_id}, Character Name: {character_name}, Corporation ID: {corporation_id}, Corporation Name: {corporation_name}, Alliance ID: {alliance_id}, Alliance Name: {alliance_name}, Ship Type ID: {ship_type_id}, Ship Type Name: {ship_type_name}, Limit: {limit}, Losses Only: {losses_only}, Kills Only: {kills_only}")
        result = await get_killmail_info(character_id, character_name, corporation_id, corporation_name, alliance_id, alliance_name, ship_type_id, ship_type_name, limit, losses_only, kills_only)
        
        # If we have a formatted_info field, return it directly for better readability
        if "formatted_info" in result:
            return {"info": result["formatted_info"]}
            
        # If there's an error, return it
        if "error" in result:
            return {"error": result["error"]}
        
        return result
    
    @function_tool
    async def get_fw_warzone_status_tool(
        self,
    ) -> Dict[str, Any]:
        """
        Get information about which side is winning in each faction warfare warzone based on system control.
        """
        logger.info("Looking up faction warfare warzone status")
        result = await get_fw_warzone_status()
        
        # If we have a formatted_info field, return it directly for better readability
        if "formatted_info" in result:
            return {"info": result["formatted_info"]}
            
        # If there's an error, return it
        if "error" in result:
            return {"error": result["error"]}
        
        return result
    
    @function_tool
    async def get_fw_system_info_tool(
        self,
        system_id: Optional[int] = None,
        system_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get detailed faction warfare information about a specific solar system. 
        Args:
            system_id: The ID of the solar system
            system_name: The name of the solar system (will be resolved to an ID)
        """
        logger.info(f"Looking up faction warfare system info for ID: {system_id}, Name: {system_name}")
        result = await get_fw_system_info(system_id, system_name)
        
        # If we have a formatted_info field, return it directly for better readability
        if "formatted_info" in result:
            return {"info": result["formatted_info"]}
            
        # If there's an error, return it
        if "error" in result:
            return {"error": result["error"]}
        
        return result


def prewarm(proc: JobProcess):
    """
    Prewarm function for the worker.
    This is called before any jobs are processed to initialize resources.
    """
    logger.info("Prewarming worker process...")
    
    # Initialize the ESI client during prewarm to avoid delays during job execution
    try:
        # Store the ESI client in the process userdata for later use
        proc.userdata["esi_client"] = get_esi_client()
        logger.info("ESI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ESI client: {e}")
        raise
    
    logger.info("Prewarm completed successfully")


async def entrypoint(ctx: JobContext):
    """
    Entrypoint function for the worker.
    """
      
    logger.info(f"Starting agent entrypoint for room: {ctx.room.name}")
    
    # Connect to the room
    logger.info("Connecting to room...")
    try:
        await ctx.connect()
        logger.info("Connected to room successfully")
    except Exception as e:
        logger.error(f"Failed to connect to room: {e}")
        raise
    
    # Wait for a participant to join
    await ctx.wait_for_participant()
    
    # Create and start the agent session
    logger.info("Creating and starting agent session...")
    session = AgentSession()
    
    @session.on("conversation_item_added")
    def conversation_item_added(msg):
        """Logs the end of speech and adds a transcription segment.""" 
        logger.info(f"Entity stopped speaking\n{str(msg)}")
    
    # Configure room options based on voice_enabled setting
    mode = "voice and text" if settings.voice_enabled else "text-only"
    logger.info(f"Starting agent session in {mode} mode")
    
    # Configure input options
    input_options = RoomInputOptions(
        audio_enabled=False,  # Only enable audio if voice is enabled
        video_enabled=False,  # Always disable video
        text_enabled=True,    # Always enable text
    )
    
    # Configure output options
    output_options = RoomOutputOptions(
        audio_enabled=False,  # Only enable audio output if voice is enabled
        transcription_enabled=True,  # Always enable transcription
    )
    
    # Start the agent session with the configured options
    await session.start(
        agent=RatauraAgent(),
        room=ctx.room,
        room_input_options=input_options,
        room_output_options=output_options,
    )
    
    logger.info(f"Agent session started successfully in {mode} mode")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
    ))
