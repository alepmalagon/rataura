"""
Configuration module for EVE Wiggin.
"""

# Updated import for Pydantic v2 compatibility
try:
    # For Pydantic v2
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    # Fallback for Pydantic v1
    from pydantic import BaseSettings, Field


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
        env_file_encoding = "utf-8"
        # Make all fields optional to prevent validation errors
        validate_assignment = False
        extra = "ignore"


settings = Settings()
