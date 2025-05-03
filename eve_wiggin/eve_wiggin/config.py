"""
Configuration module for EVE Wiggin.
"""

import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for EVE Wiggin.
    """
    # Application settings
    app_name: str = "EVE Wiggin"
    app_description: str = "Strategic Analysis Tool for EVE Online Faction Warfare"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # EVE Online ESI API settings
    esi_base_url: str = "https://esi.evetech.net/latest"
    eve_user_agent: str = "EVE-Wiggin/0.1.0 (https://github.com/alepmalagon/rataura)"
    
    # Database settings
    db_url: Optional[str] = None
    
    # Logging settings
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_prefix = "EVE_WIGGIN_"


# Create a global settings instance
settings = Settings()

