"""
ESI API authentication module for the Rataura application.
"""

import logging
import aiohttp
import time
from typing import Dict, Any, Optional, Tuple
from rataura.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# EVE Online SSO URLs
EVE_SSO_AUTH_URL = "https://login.eveonline.com/v2/oauth/authorize"
EVE_SSO_TOKEN_URL = "https://login.eveonline.com/v2/oauth/token"
EVE_SSO_VERIFY_URL = "https://login.eveonline.com/oauth/verify"


class ESIAuth:
    """
    Authentication handler for the EVE Online ESI API.
    """
    
    def __init__(self):
        """
        Initialize the ESI authentication handler.
        """
        self.client_id = settings.eve_client_id
        self.client_secret = settings.eve_client_secret
        self.callback_url = settings.eve_callback_url
    
    def get_auth_url(self, state: str, scopes: Optional[str] = None) -> str:
        """
        Get the URL for the EVE Online SSO authorization page.
        
        Args:
            state (str): A unique state string to prevent CSRF attacks.
            scopes (Optional[str], optional): A space-separated list of scopes to request.
        
        Returns:
            str: The authorization URL.
        """
        params = {
            "response_type": "code",
            "redirect_uri": self.callback_url,
            "client_id": self.client_id,
            "state": state,
        }
        
        if scopes:
            params["scope"] = scopes
        
        # Build the query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        
        return f"{EVE_SSO_AUTH_URL}?{query_string}"
    
    async def get_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange an authorization code for access and refresh tokens.
        
        Args:
            code (str): The authorization code from the EVE Online SSO.
        
        Returns:
            Dict[str, Any]: The token response data.
        
        Raises:
            Exception: If the token request fails.
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.eveonline.com",
        }
        
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(EVE_SSO_TOKEN_URL, data=data, headers=headers, auth=auth) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"ESI token error: {response.status} - {error_text}")
                    raise Exception(f"ESI token error: {response.status} - {error_text}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token (str): The refresh token.
        
        Returns:
            Dict[str, Any]: The token response data.
        
        Raises:
            Exception: If the token refresh fails.
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.eveonline.com",
        }
        
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(EVE_SSO_TOKEN_URL, data=data, headers=headers, auth=auth) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"ESI token refresh error: {response.status} - {error_text}")
                    raise Exception(f"ESI token refresh error: {response.status} - {error_text}")
    
    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify an access token and get character information.
        
        Args:
            access_token (str): The access token to verify.
        
        Returns:
            Dict[str, Any]: The character information.
        
        Raises:
            Exception: If the token verification fails.
        """
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(EVE_SSO_VERIFY_URL, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"ESI token verification error: {response.status} - {error_text}")
                    raise Exception(f"ESI token verification error: {response.status} - {error_text}")


class TokenManager:
    """
    Manager for EVE Online ESI API tokens.
    """
    
    def __init__(self):
        """
        Initialize the token manager.
        """
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self.auth = ESIAuth()
    
    async def add_token(self, user_id: str, code: str) -> Dict[str, Any]:
        """
        Add a new token for a user.
        
        Args:
            user_id (str): The user ID.
            code (str): The authorization code from the EVE Online SSO.
        
        Returns:
            Dict[str, Any]: The token data.
        """
        token_data = await self.auth.get_tokens(code)
        
        # Add expiry time
        token_data["expires_at"] = time.time() + token_data["expires_in"]
        
        # Store the token
        self.tokens[user_id] = token_data
        
        return token_data
    
    async def get_access_token(self, user_id: str) -> Optional[str]:
        """
        Get a valid access token for a user.
        
        Args:
            user_id (str): The user ID.
        
        Returns:
            Optional[str]: The access token, or None if the user has no token.
        """
        if user_id not in self.tokens:
            return None
        
        token_data = self.tokens[user_id]
        
        # Check if the token is expired
        if time.time() >= token_data["expires_at"]:
            # Refresh the token
            try:
                new_token_data = await self.auth.refresh_token(token_data["refresh_token"])
                
                # Update the token data
                token_data.update(new_token_data)
                token_data["expires_at"] = time.time() + new_token_data["expires_in"]
                
                # Store the updated token
                self.tokens[user_id] = token_data
                
            except Exception as e:
                logger.error(f"Error refreshing token for user {user_id}: {e}")
                return None
        
        return token_data["access_token"]
    
    async def get_character_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get character information for a user.
        
        Args:
            user_id (str): The user ID.
        
        Returns:
            Optional[Dict[str, Any]]: The character information, or None if the user has no token.
        """
        access_token = await self.get_access_token(user_id)
        
        if not access_token:
            return None
        
        try:
            return await self.auth.verify_token(access_token)
        except Exception as e:
            logger.error(f"Error verifying token for user {user_id}: {e}")
            return None
    
    def remove_token(self, user_id: str) -> bool:
        """
        Remove a token for a user.
        
        Args:
            user_id (str): The user ID.
        
        Returns:
            bool: True if the token was removed, False if the user had no token.
        """
        if user_id in self.tokens:
            del self.tokens[user_id]
            return True
        return False


# Create a global token manager instance
token_manager = TokenManager()


def get_token_manager() -> TokenManager:
    """
    Get the token manager instance.
    
    Returns:
        TokenManager: The token manager instance.
    """
    return token_manager
