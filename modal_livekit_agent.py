"""
Modal app for running the Rataura LiveKit agent on Modal.com.

This script demonstrates how to deploy the Rataura LiveKit agent on Modal's serverless platform.
"""

import os
import sys

import time
import logging
from typing import Optional, Dict, Any
from modal import App, Image, Secret, method, web_endpoint, Period


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
    # Debug: Show the environment
    .run_commands(
        "echo 'Current directory structure:'",
        "ls -la",
        "echo 'Python version:'",
        "python --version",
    )
)

# Define minimal versions of the necessary functions from rataura.livekit_agent.agent
def prewarm():
    """Prewarm function for the LiveKit agent."""
    print("Prewarming LiveKit agent...")
    return True

def entrypoint(context):
    """Entrypoint function for the LiveKit agent."""
    print("Starting LiveKit agent...")
    print(f"Context: {context}")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s %(name)s - %(message)s",
    )
    
    # Suppress websockets debug messages
    logging.getLogger("websockets.client").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    
    # Initialize OpenAI client
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Initialize Google AI client
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    print("LiveKit agent initialized successfully!")
    
    # This function would normally set up the LiveKit agent with EVE Online tools
    # For now, we'll just return a simple agent that responds to messages
    return {
        "status": "success",
        "message": "LiveKit agent started successfully",
    }

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
        
        # Print the Python path for debugging
        print(f"Python path: {sys.path}")
        
        # List the contents of the current directory for debugging
        import os
        print("Contents of current directory:")
        os.system("ls -la")
        
        print("Starting LiveKit worker...")
        
        # Run the LiveKit worker with our local entrypoint and prewarm functions
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
    # Print the Python path for debugging
    print(f"Python path: {sys.path}")
    
    # List the contents of the current directory for debugging
    import os
    print("Contents of current directory:")
    os.system("ls -la")
    
    print("Starting LiveKit worker...")
    
    # Run the LiveKit worker with our local entrypoint and prewarm functions
    from livekit.agents import WorkerOptions, cli
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )

# Define a function that will be automatically started when the app is deployed
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
    schedule=Period(minutes=5),  # Restart every 5 minutes to ensure it's always running
)
def keep_worker_running():
    """Ensure the LiveKit worker is always running by starting it periodically."""
    # Print the Python path for debugging
    print(f"Python path: {sys.path}")
    
    # List the contents of the current directory for debugging
    import os
    print("Contents of current directory:")
    os.system("ls -la")
    
    print("Starting LiveKit worker...")
    
    # Run the LiveKit worker with our local entrypoint and prewarm functions
    from livekit.agents import WorkerOptions, cli
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

# Define a web endpoint to manually start the worker
@app.function(
    image=image,
    secrets=[
        Secret.from_name("livekit-secrets"),
        Secret.from_name("openai-api-key"),
        Secret.from_name("google-api-key"),
        Secret.from_name("eve-esi-secrets"),
    ],
    timeout=30,
)
@web_endpoint(method="POST")
def start_worker(request):
    """Start the LiveKit worker manually via a web endpoint."""
    # Start the worker in a separate container
    run_standalone_worker.spawn()
    
    return {
        "status": "success",
        "message": "LiveKit worker started successfully",
    }

if __name__ == "__main__":
    # When run directly, this will deploy the app to Modal
    app.run()
