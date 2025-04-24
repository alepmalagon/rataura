"""
Configuration module for the Rataura application.
"""

import os
from typing import Optional, Any, Callable
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Discord settings
    discord_token: Optional[str] = Field(None, env="DISCORD_TOKEN")
    
    # EVE Online ESI API settings
    eve_client_id: Optional[str] = Field(None, env="EVE_CLIENT_ID")
    eve_client_secret: Optional[str] = Field(None, env="EVE_CLIENT_SECRET")
    eve_callback_url: Optional[str] = Field(None, env="EVE_CALLBACK_URL")
    eve_user_agent: str = Field("Rataura/0.1.0 (Discord Bot)", env="EVE_USER_AGENT")
    
    # LLM settings
    llm_api_key: Optional[str] = Field(None, env="LLM_API_KEY")
    llm_model: str = Field("gpt-4", env="LLM_MODEL")
    
    # Livekit settings
    livekit_api_key: Optional[str] = Field(None, env="LIVEKIT_API_KEY")
    livekit_api_secret: Optional[str] = Field(None, env="LIVEKIT_API_SECRET")
    livekit_url: Optional[str] = Field(None, env="LIVEKIT_URL")
    
    class Config:
        """
        Pydantic configuration class.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def llm_provider(self, model: Optional[str] = None) -> Any:
        """
        Get the LLM provider for the Livekit agent.
        
        Args:
            model (Optional[str], optional): The model to use. Defaults to None.
        
        Returns:
            Any: The LLM provider.
        """
        try:
            from livekit.plugins import openai
            return openai.LLM(model=model or self.llm_model)
        except ImportError:
            raise ImportError("Livekit plugins are not installed. Please install livekit-agents package.")


# Create a global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get the application settings.
    
    Returns:
        Settings: The application settings.
    """
    return settings
