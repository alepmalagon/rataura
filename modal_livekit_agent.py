"""
Modal app for running the Rataura LiveKit agent on Modal.com.

This script demonstrates how to deploy the Rataura LiveKit agent on Modal's serverless platform.
"""

import os
import sys

import time
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
    # Set up the rataura package in the container
    .run_commands(
        # Create directories
        "mkdir -p /root/rataura",
        # Debug: List the current directory structure
        "echo 'Current directory structure:'",
        "ls -la",
        "echo 'Contents of ./rataura:'",
        "ls -la ./rataura || echo 'rataura directory not found'",
        # Copy the rataura package to the container with error handling
        "if [ -d './rataura/rataura' ]; then cp -r ./rataura/rataura /root/rataura/; else echo 'Directory ./rataura/rataura not found'; fi",
        "if [ -f './rataura/requirements.txt' ]; then cp ./rataura/requirements.txt /root/rataura/; else echo 'File ./rataura/requirements.txt not found'; fi",
        "if [ -f './rataura/README.md' ]; then cp ./rataura/README.md /root/rataura/; else echo 'File ./rataura/README.md not found'; fi",
        # Alternative approach: Copy the entire rataura directory
        "if [ -d './rataura' ]; then cp -r ./rataura /root/; else echo 'Directory ./rataura not found'; fi",
        # Debug: List the contents of the destination directory
        "echo 'Contents of /root/rataura:'",
        "ls -la /root/rataura || echo '/root/rataura directory not found'",
        "echo 'Contents of /root:'",
        "ls -la /root",
    )
)

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
        
        # Add the rataura package to the Python path
        import sys
        sys.path.insert(0, "/root")
        
        # Print the Python path for debugging
        print(f"Python path: {sys.path}")
        
        # List the contents of the rataura directory for debugging
        import os
        print("Contents of /root:")
        os.system("ls -la /root")
        print("Contents of /root/rataura:")
        os.system("ls -la /root/rataura || echo '/root/rataura not found'")
        
        # Try different import paths
        try:
            print("Trying import path: rataura.rataura.livekit_agent.agent")
            from rataura.rataura.livekit_agent.agent import entrypoint, prewarm
            print("Import successful!")
        except ImportError as e1:
            print(f"First import attempt failed: {e1}")
            try:
                print("Trying import path: rataura.livekit_agent.agent")
                from rataura.livekit_agent.agent import entrypoint, prewarm
                print("Import successful!")
            except ImportError as e2:
                print(f"Second import attempt failed: {e2}")
                raise ImportError(f"Could not import the rataura package. Errors: {e1}, {e2}")
        
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
    # Add the rataura package to the Python path
    import sys
    sys.path.insert(0, "/root")
    
    # Print the Python path for debugging
    print(f"Python path: {sys.path}")
    
    # List the contents of the rataura directory for debugging
    import os
    print("Contents of /root:")
    os.system("ls -la /root")
    print("Contents of /root/rataura:")
    os.system("ls -la /root/rataura || echo '/root/rataura not found'")
    
    # Try different import paths
    try:
        print("Trying import path: rataura.rataura.livekit_agent.agent")
        from rataura.rataura.livekit_agent.agent import entrypoint, prewarm
        print("Import successful!")
    except ImportError as e1:
        print(f"First import attempt failed: {e1}")
        try:
            print("Trying import path: rataura.livekit_agent.agent")
            from rataura.livekit_agent.agent import entrypoint, prewarm
            print("Import successful!")
        except ImportError as e2:
            print(f"Second import attempt failed: {e2}")
            raise ImportError(f"Could not import the rataura package. Errors: {e1}, {e2}")
    
    # Run the LiveKit worker
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
    # Add the rataura package to the Python path
    import sys
    sys.path.insert(0, "/root")
    
    # Print the Python path for debugging
    print(f"Python path: {sys.path}")
    
    # List the contents of the rataura directory for debugging
    import os
    print("Contents of /root:")
    os.system("ls -la /root")
    print("Contents of /root/rataura:")
    os.system("ls -la /root/rataura || echo '/root/rataura not found'")
    
    print("Starting LiveKit worker...")
    
    # Try different import paths
    try:
        print("Trying import path: rataura.rataura.livekit_agent.agent")
        from rataura.rataura.livekit_agent.agent import entrypoint, prewarm
        print("Import successful!")
    except ImportError as e1:
        print(f"First import attempt failed: {e1}")
        try:
            print("Trying import path: rataura.livekit_agent.agent")
            from rataura.livekit_agent.agent import entrypoint, prewarm
            print("Import successful!")
        except ImportError as e2:
            print(f"Second import attempt failed: {e2}")
            raise ImportError(f"Could not import the rataura package. Errors: {e1}, {e2}")
    
    # Run the LiveKit worker
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
