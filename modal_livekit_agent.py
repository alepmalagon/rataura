"""
Modal app for running the Rataura LiveKit agent on Modal.com.

This script demonstrates how to deploy the Rataura LiveKit agent on Modal's serverless platform.
"""

import os

import time
from modal import App, Image, Secret, method, web_endpoint


# Create a Modal app
app = App("rataura-livekit-agent")

# Define the container image with all required dependencies
image = (
    Image.debian_slim()
    .pip_install(
        # Livekit dependencies
        "livekit-agents[google,elevenlabs,openai,silero,deepgram,cartesia,turn-detector,rag,noise-cancellation]~=1.0rc",
        "livekit-api",
        # EVE Online ESI API client
        "requests>=2.25.0",
        "aiohttp>=3.7.4",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        # LLM integration
        "openai>=1.0.0",
        "google-generativeai>=0.8.0",
        # Utilities
        "python-dotenv>=0.19.0",
        "loguru>=0.5.3",
        # Discord integration
        "discord.py>=2.0.0",
    )
    # Copy the rataura package to the image instead of installing it
    .copy("./rataura", "/root/rataura")
)

# Add the rataura package to the Python path
import sys
sys.path.append("/root")

# Define the LiveKit agent class that will run on Modal
@app.cls(
    image=image,
    gpu="T4",  # Updated to use string format instead of gpu.T4()

    secrets=[
        Secret.from_name("livekit-secrets"),  # Contains LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
        Secret.from_name("openai-api-key"),   # Contains OPENAI_API_KEY
        Secret.from_name("google-api-key"),   # Contains GOOGLE_API_KEY
        Secret.from_name("eve-esi-secrets"),  # Contains any EVE Online ESI API credentials
    ],
    timeout=3600,  # 1 hour timeout for long-running sessions
)
class RatauraLiveKitWorker:
    def __enter__(self):
        """Initialize resources when the container starts."""
        # Import here to ensure imports happen in the Modal container
        import logging
        from dotenv import load_dotenv
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s %(name)s - %(message)s",
        )
        # Suppress websockets debug messages
        logging.getLogger("websockets.client").setLevel(logging.WARNING)
        logging.getLogger("websockets").setLevel(logging.WARNING)
        
        # Load environment variables from secrets
        # Modal automatically loads secrets as environment variables
        load_dotenv()
        
        # Initialize any other resources needed
        
    @method()
    def run_worker(self):
        """Run the LiveKit worker."""
        # Import here to ensure imports happen in the Modal container
        from livekit.agents import WorkerOptions, cli
        from rataura.livekit_agent.agent import entrypoint, prewarm
        
        # Run the LiveKit worker
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                prewarm_fnc=prewarm,
            )
        )

# Define a function to run the worker as a standalone process
@app.function(
    image=image,
    secrets=[
        Secret.from_name("livekit-secrets"),
        Secret.from_name("openai-api-key"),
        Secret.from_name("google-api-key"),
        Secret.from_name("eve-esi-secrets"),
    ],
    timeout=3600,  # 1 hour timeout
    min_containers=1,  # Keep one instance warm to reduce cold start times

)
def run_standalone_worker():
    """Run the LiveKit worker as a standalone process."""
    from livekit.agents import WorkerOptions, cli
    from rataura.livekit_agent.agent import entrypoint, prewarm
    
    # Run the LiveKit worker
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )

# Define a web endpoint that can be used to create new LiveKit rooms
@app.function(
    image=image,
    secrets=[Secret.from_name("livekit-secrets")],
    timeout=30,
)

@web_endpoint(method="POST")  # Updated from web_endpoint to fastapi_endpoint

def create_room(request):
    """Create a new LiveKit room and return the room details."""
    import json
    from livekit import api
    
    # Get LiveKit credentials from environment variables
    livekit_url = os.environ["LIVEKIT_URL"]
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]
    
    # Parse request body
    request_data = request.json()
    room_name = request_data.get("room_name", f"rataura-room-{int(time.time())}")
    
    # Create LiveKit room client
    room_client = api.RoomServiceClient(
        livekit_url,
        api_key,
        api_secret,
    )
    
    # Create a new room
    room = room_client.create_room(room_name)
    
    # Create a token for the user
    token_client = api.TokenClient(api_key, api_secret)
    token = token_client.create_join_token(
        room_name=room_name,
        identity="user",
        ttl=3600,  # 1 hour
        name="User",
    )
    
    # Return room details and token
    return {
        "room_name": room_name,
        "room_id": room.sid,
        "user_token": token,
    }

if __name__ == "__main__":
    # When run directly, this will deploy the app to Modal
    app.run()
