"""
Livekit integration module for the Rataura application.
"""

import logging
import asyncio
from typing import Optional, Callable, Any
from livekit import rtc
from rataura.config import settings

# Configure logging
logger = logging.getLogger(__name__)


class LivekitClient:
    """
    Livekit client for the Rataura application.
    """
    
    def __init__(self):
        """
        Initialize the Livekit client.
        """
        self.room: Optional[rtc.Room] = None
        self.is_connected = False
        self.message_callback: Optional[Callable[[str], Any]] = None
    
    async def connect(self, room_name: str, participant_name: str):
        """
        Connect to a Livekit room.
        
        Args:
            room_name (str): The name of the room to connect to.
            participant_name (str): The name of the participant.
        
        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        if not settings.livekit_url or not settings.livekit_api_key or not settings.livekit_api_secret:
            logger.error("Livekit settings are not configured")
            return False
        
        try:
            # Create a new room
            self.room = rtc.Room()
            
            # Set up event listeners
            self.room.on("participant_connected", self._on_participant_connected)
            self.room.on("participant_disconnected", self._on_participant_disconnected)
            self.room.on("data_received", self._on_data_received)
            
            # Connect to the room
            await self.room.connect(
                settings.livekit_url,
                settings.livekit_api_key,
                participant_name=participant_name,
                room_name=room_name
            )
            
            self.is_connected = True
            logger.info(f"Connected to Livekit room: {room_name}")
            return True
            
        except Exception as e:
            logger.exception(f"Error connecting to Livekit room: {e}")
            return False
    
    async def disconnect(self):
        """
        Disconnect from the Livekit room.
        """
        if self.room and self.is_connected:
            try:
                await self.room.disconnect()
                self.is_connected = False
                logger.info("Disconnected from Livekit room")
            except Exception as e:
                logger.exception(f"Error disconnecting from Livekit room: {e}")
    
    async def send_message(self, message: str):
        """
        Send a message to the Livekit room.
        
        Args:
            message (str): The message to send.
        
        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        if not self.room or not self.is_connected:
            logger.error("Not connected to a Livekit room")
            return False
        
        try:
            # Convert the message to bytes
            data = message.encode("utf-8")
            
            # Send the message to all participants
            await self.room.local_participant.publish_data(data, rtc.DataPacketKind.RELIABLE)
            return True
            
        except Exception as e:
            logger.exception(f"Error sending message to Livekit room: {e}")
            return False
    
    def set_message_callback(self, callback: Callable[[str], Any]):
        """
        Set the callback function for received messages.
        
        Args:
            callback (Callable[[str], Any]): The callback function.
        """
        self.message_callback = callback
    
    def _on_participant_connected(self, participant: rtc.RemoteParticipant):
        """
        Event handler for when a participant connects to the room.
        
        Args:
            participant (rtc.RemoteParticipant): The participant that connected.
        """
        logger.info(f"Participant connected: {participant.identity}")
    
    def _on_participant_disconnected(self, participant: rtc.RemoteParticipant):
        """
        Event handler for when a participant disconnects from the room.
        
        Args:
            participant (rtc.RemoteParticipant): The participant that disconnected.
        """
        logger.info(f"Participant disconnected: {participant.identity}")
    
    def _on_data_received(self, data: bytes, participant: rtc.RemoteParticipant):
        """
        Event handler for when data is received from a participant.
        
        Args:
            data (bytes): The data that was received.
            participant (rtc.RemoteParticipant): The participant that sent the data.
        """
        try:
            # Convert the data to a string
            message = data.decode("utf-8")
            
            # Call the message callback if it exists
            if self.message_callback:
                asyncio.create_task(self.message_callback(message))
                
        except Exception as e:
            logger.exception(f"Error processing received data: {e}")


# Create a global Livekit client instance
livekit_client = LivekitClient()


def get_livekit_client() -> LivekitClient:
    """
    Get the Livekit client instance.
    
    Returns:
        LivekitClient: The Livekit client instance.
    """
    return livekit_client
