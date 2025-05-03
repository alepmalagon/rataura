"""
Logging utilities for EVE Wiggin.
"""

import logging
import sys
from typing import Optional

from eve_wiggin.config import settings


def setup_logging(log_level: Optional[str] = None):
    """
    Set up logging for the application.
    
    Args:
        log_level (Optional[str], optional): The log level to use. Defaults to None.
    """
    level = log_level or settings.log_level
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Set log levels for specific loggers
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

