# livekit_text_agent.py

"""
A LiveKit Agent Worker script for text-based interaction via the LiveKit Playground.
This agent uses Google Gemini (via livekit-plugins-google) as its LLM and communicates exclusively via text streams:
it listens on the 'lk.chat' topic for incoming user messages and sends responses to the 'lk.transcription' topic.
Audio input/output (STT/TTS) are disabled to operate in text-only mode.
"""

import os
import logging

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    WorkerOptions,
    cli,
)
from livekit import rtc
from livekit.agents.voice.room_io.room_io import TextInputEvent
from livekit.plugins import google

# Load environment variables from a .env file (LIVEKIT_URL, LIVEKIT_API_KEY/SECRET, GOOGLE_API_KEY, etc.)
load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("livekit-text-agent")

class TextAgent(Agent):
    """
    A simple agent that generates text responses using a Google Gemini LLM.
    """
    def __init__(self):
        # Initialize the agent with instructions for text-based conversation.
        # These instructions guide the Gemini LLM's behavior.
        super().__init__(
            instructions="You are a helpful text-based assistant. "
                         "Respond to user queries clearly and concisely."
        )
    
    async def on_enter(self):
        # When the agent is started, we do not send an initial greeting.
        # The agent will wait for user input on the 'lk.chat' topic.
        pass

def prewarm(proc: JobProcess):
    """
    Prewarm function called once per worker process before any session starts.
    It can be used to load expensive resources into memory.
    """
    # No heavy resources to pre-load for Gemini in this example.
    # For demonstration, we log the current process info.
    logger.info(f"Prewarming worker process PID: {os.getpid()}")

async def entrypoint(ctx: JobContext):
    async def _text_input_cb(sess: AgentSession, ev: TextInputEvent) -> None:
        logger.info(f"Received text input: {ev.text}")
        sess.interrupt()
        handle = await sess.generate_reply(user_input=ev.text)
        ctx.room.local_participant.publish_data()
        # This retrieves the plain text from the last LLM output
        logger.info(f"LLM Reply:\n {str(handle)}")
    """
    Entrypoint for each agent session. Connects to the LiveKit room and starts the AgentSession.
    """
    # Include context fields in log messages for easier debugging
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "user_id": "text_user",
    }
    
    # Connect to the LiveKit room (join as a hidden audio/video participant)
    await ctx.connect()
    
    # Create the Google Gemini LLM instance.
    # Ensure GOOGLE_API_KEY is set in the environment for authentication.
    # We use the Gemini-2.0 Flash model with a moderate temperature for creativity.
    llm = google.LLM(model="gemini-2.0-flash-001", temperature=0.7)
    
    # Initialize the AgentSession with only the LLM (no STT/TTS since this is text-only).
    session = AgentSession(
        llm=llm
    )
    
    # Wait for a participant (i.e., the user) to join the room before starting the session.
    await ctx.wait_for_participant()

    @session.on("conversation_item_added")
    def conversation_item_added(msg):
        """Logs the end of speech and adds a transcription segment.""" 
        logger.info(f"Entity stopped speaking\n{str(msg)}")
    
    # Start the session with the TextAgent.
    # Configure the room input/output for text-only operation:
    #   - Enable text input from 'lk.chat' (default topic).
    #   - Disable audio output and use text output on 'lk.transcription'.
    await session.start(
        agent=TextAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            text_enabled=True,        # Enable receiving text from the user
            text_input_cb = _text_input_cb
        ),
        room_output_options=RoomOutputOptions(
            audio_enabled=False,       # Disable TTS/audio output entirely
            transcription_enabled=True,
        ),
    )
    chat = rtc.ChatManager(ctx.room)

    @chat.on("message_received")
    def on_chat_received(msg):
        logger.info(f"Received chat message: {str(msg)}")
        
if __name__ == "__main__":
    # Run the LiveKit agent worker using the defined entrypoint and prewarm functions.
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
