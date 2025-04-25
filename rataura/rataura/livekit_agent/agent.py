"""
Livekit agent module for the Rataura application.
This module implements a Livekit 1.0 worker that includes the LLM tool functions for the ESI API.
"""

import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

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
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("rataura-agent")
load_dotenv()

class RatauraAgent(Agent):
    """
    Livekit agent for the Rataura application.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Rataura agent.
        """
        logger.info("Initializing RatauraAgent...")
        super().__init__(
            instructions=(
                "You are Rataura, a helpful assistant for EVE Online players. "
                "You have access to the EVE Online ESI API through function calls. "
                "Use these functions to get accurate information about the game. "
                "Keep your responses concise and to the point. "
                "You are knowledgeable about EVE Online game mechanics, items, ships, corporations, alliances, and more. "
                "When users ask about game information, use the appropriate function to get the most accurate data."
            ),
            llm=settings.llm_provider(),
        )
        logger.info("RatauraAgent initialized successfully")
    
    async def on_text(self, text: str, ctx: ChatContext) -> None:
        """
        Called when a text message is received.
        This is the main entry point for chat messages.
        """
        logger.info(f"Received text message: {text}")
        # Generate a reply to the text message
        await self.session.generate_reply(ctx)
    
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
    ) -> Dict[str, Any]:
        """
        Get market prices for EVE Online items.
        
        Args:
            type_id: The ID of the item type
            type_name: The name of the item type (will be resolved to an ID)
            region_id: The ID of the region
            region_name: The name of the region (will be resolved to an ID)
        """
        logger.info(f"Looking up market prices for Type ID: {type_id}, Type Name: {type_name}, Region ID: {region_id}, Region Name: {region_name}")
        result = await get_market_prices(type_id, type_name, region_id, region_name)
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
    
    # Create and start the agent session
    logger.info("Creating and starting agent session...")
    session = AgentSession()
    
    # Start the agent session with text input enabled
    await session.start(
        agent=RatauraAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(text_enabled=True, audio_enabled=False),
        room_output_options=RoomOutputOptions(text_enabled=True, audio_enabled=False),
    )
    logger.info("Agent session started successfully")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        prewarm_fnc=prewarm,
    ))
