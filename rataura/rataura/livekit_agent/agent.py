"""
Livekit agent module for the Rataura application.
This module implements a Livekit 1.0 worker that includes the LLM tool functions for the ESI API.
"""

import logging
import asyncio
import json
import os
import time
import sys
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
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

# Global variable to store the ESI client
esi_client = None

# Validate required settings for Livekit agent
def validate_livekit_settings():
    """
    Validate that the required settings for the Livekit agent are present.
    Raises an error if any required settings are missing.
    """
    logger.info("Validating Livekit settings...")
    missing_settings = []
    
    if not settings.livekit_api_key:
        missing_settings.append("LIVEKIT_API_KEY")
    if not settings.livekit_api_secret:
        missing_settings.append("LIVEKIT_API_SECRET")
    if not settings.livekit_url:
        missing_settings.append("LIVEKIT_URL")
    
    # Check LLM settings based on provider
    if settings.llm_provider_name.lower() == "gemini":
        if not (settings.gemini_api_key or settings.llm_api_key):
            missing_settings.append("GEMINI_API_KEY or LLM_API_KEY")
    else:  # Default to OpenAI
        if not settings.llm_api_key:
            missing_settings.append("LLM_API_KEY")
    
    if missing_settings:
        error_msg = f"Missing required environment variables: {', '.join(missing_settings)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Livekit settings validation successful")

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
        )
        logger.info("RatauraAgent initialized successfully")
    
    async def on_enter(self):
        """
        Called when the agent is added to the session.
        """
        logger.info("Agent entered session, generating welcome message")
        # Generate a welcome message when the agent is added to the session
        self.session.generate_reply()
    
    # Function tools for the LLM
    
    @function_tool
    async def get_alliance_info_tool(
        self,
        context: RunContext,
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
        context: RunContext,
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
        context: RunContext,
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
        context: RunContext,
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
        context: RunContext,
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
        context: RunContext,
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
        context: RunContext,
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
        context: RunContext,
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
    start_time = time.time()
    
    # Validate settings early
    try:
        validate_livekit_settings()
        logger.info("Settings validation successful")
    except Exception as e:
        logger.error(f"Settings validation failed during prewarm: {e}")
        raise
    
    # Initialize the ESI client during prewarm to avoid delays during job execution
    try:
        # Store the ESI client in the process userdata for later use
        proc.userdata["esi_client"] = get_esi_client()
        logger.info("ESI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ESI client: {e}")
        raise
    
    logger.info(f"Prewarm completed in {time.time() - start_time:.2f} seconds")


async def entrypoint(ctx: JobContext):
    """
    Entrypoint function for the worker.
    """
    start_time = time.time()
    logger.info(f"Starting agent entrypoint for room: {ctx.room.name}")
    
    # Set up logging context
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "user_id": "rataura-agent",
    }
    
    # Connect to the room with a retry mechanism
    max_retries = 3
    retry_delay = 2
    connection_timeout = 10.0  # Increased timeout
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connecting to room (attempt {attempt}/{max_retries})...")
            # Use a longer timeout for the connection
            await asyncio.wait_for(ctx.connect(), timeout=connection_timeout)
            logger.info("Connected to room successfully")
            break
        except asyncio.TimeoutError:
            if attempt < max_retries:
                logger.warning(f"Timeout while connecting to room (attempt {attempt}/{max_retries}), retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to room after {max_retries} attempts")
                # Print detailed debug information
                logger.error(f"Room name: {ctx.room.name}")
                logger.error(f"Livekit URL: {settings.livekit_url}")
                logger.error("Connection timeout - check network connectivity and Livekit server status")
                raise
        except Exception as e:
            logger.error(f"Error connecting to room: {e}")
            if attempt < max_retries:
                logger.warning(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to room after {max_retries} attempts")
                raise
    
    # Create an agent session
    logger.info("Creating agent session...")
    try:
        session = AgentSession(
            # Configure the LLM
            llm=settings.llm_provider(model=settings.llm_model if settings.llm_provider_name.lower() != "gemini" else settings.gemini_model),
        )
        logger.info("Agent session created successfully")
    except Exception as e:
        logger.error(f"Failed to create agent session: {e}")
        raise
    
    # Set up metrics collection
    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: metrics.MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)
    
    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")
    
    # Add shutdown callback to log usage
    ctx.add_shutdown_callback(log_usage)
    
    # Wait for a participant to join the room with a timeout and retry mechanism
    max_participant_wait_retries = 2
    participant_wait_timeout = 10.0  # Increased timeout
    
    for attempt in range(1, max_participant_wait_retries + 1):
        try:
            logger.info(f"Waiting for participant (attempt {attempt}/{max_participant_wait_retries})...")
            await asyncio.wait_for(ctx.wait_for_participant(), timeout=participant_wait_timeout)
            logger.info("Participant joined")
            break
        except asyncio.TimeoutError:
            if attempt < max_participant_wait_retries:
                logger.warning(f"No participant joined within timeout (attempt {attempt}/{max_participant_wait_retries}), retrying...")
            else:
                logger.info("No participant joined within timeout, continuing anyway")
        except Exception as e:
            logger.error(f"Error waiting for participant: {e}")
            if attempt < max_participant_wait_retries:
                logger.warning("Retrying...")
            else:
                logger.error("Failed to wait for participant, continuing anyway")
    
    # Start the session with the agent
    logger.info("Starting agent session...")
    try:
        await session.start(
            agent=RatauraAgent(),
            room=ctx.room,
            room_input_options=RoomInputOptions(),
            room_output_options=RoomOutputOptions(transcription_enabled=True),
        )
        logger.info("Agent session started successfully")
    except Exception as e:
        logger.error(f"Failed to start agent session: {e}")
        raise
    
    logger.info(f"Entrypoint completed initialization in {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint, 
        prewarm_fnc=prewarm,
    ))
