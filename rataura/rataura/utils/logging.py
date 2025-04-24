"""
Logging utility module for the Rataura application.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None):
    """
    Set up logging for the application.
    
    Args:
        level (int, optional): The logging level. Defaults to logging.INFO.
        log_file (Optional[str], optional): The path to the log file. Defaults to None.
    """
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create a file handler if a log file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Suppress logs from other libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("discord").setLevel(logging.WARNING)
    
    logger.info("Logging setup complete")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name (str): The name of the logger.
    
    Returns:
        logging.Logger: The logger.
    """
    return logging.getLogger(name)
