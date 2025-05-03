#!/usr/bin/env python3
"""
Main entry point for the Rataura application.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Suppress websockets debug messages
logging.getLogger("websockets.client").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the application.
    """
    try:
        logger.info("Starting Rataura...")
        
        # Import here to avoid circular imports
        from rataura.discord.bot import start_bot
        
        # Start the Discord bot
        start_bot()
        
    except Exception as e:
        logger.exception(f"Error starting Rataura: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
