"""
Configuration module for EVE Wiggin.
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    """
    app_name: str = "EVE Wiggin"
    app_version: str = "0.1.0"
    log_level: str = "DEBUG"  # Changed from INFO to DEBUG for more detailed logging
    
    # ESI API settings
    esi_client_id: str = ""
    esi_client_secret: str = ""
    esi_callback_url: str = "http://localhost:8000/callback"
    
    class Config:
        env_prefix = "EVE_WIGGIN_"
        env_file = ".env"


settings = Settings()
