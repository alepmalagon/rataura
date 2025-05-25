# Deploying Rataura LiveKit Agent on Modal.com

This guide explains how to deploy the Rataura LiveKit agent on Modal.com's serverless platform.

## Prerequisites

1. A [Modal.com](https://modal.com) account
2. A [LiveKit](https://livekit.io) account with API credentials
3. API keys for any AI services used (OpenAI, Google AI, etc.)
4. Python 3.9+ installed locally

## Setup

### 1. Install Modal CLI

```bash
pip install modal
```

### 2. Authenticate with Modal

```bash
modal setup
```

Follow the prompts to authenticate with your Modal account.

### 3. Set up Secrets in Modal Dashboard

Navigate to the Secrets section in the Modal dashboard and add the following secrets:

#### LiveKit Secrets

Create a secret named `livekit-secrets` with the following values:
- `LIVEKIT_URL`: Your LiveKit WebRTC server URL
- `LIVEKIT_API_KEY`: API key for authenticating LiveKit requests
- `LIVEKIT_API_SECRET`: API secret for LiveKit authentication

You can find these values in the LiveKit dashboard under Settings > Project and Settings > Keys.

#### AI Service Secrets

Create secrets for each AI service you're using:

- `openai-api-key`: Contains `OPENAI_API_KEY` for OpenAI services
- `google-api-key`: Contains `GOOGLE_API_KEY` for Google AI services

#### EVE Online ESI API Secrets

Create a secret named `eve-esi-secrets` with any credentials needed for the EVE Online ESI API.

### 4. Deploy the Modal App

1. Clone the Rataura repository (if you haven't already):
   ```bash
   git clone https://github.com/alepmalagon/rataura.git
   cd rataura
   ```

2. Copy the `modal_livekit_agent.py` file to the root of the repository.

3. Make sure the `rataura` package directory is in the repository root.

4. Deploy the app to Modal:
   ```bash
   modal deploy modal_livekit_agent.py
   ```

## Usage

### Automatic Worker Execution

The LiveKit worker is automatically started when the app is deployed, thanks to the scheduled function `keep_worker_running`. This function:

1. Runs immediately when the app is deployed
2. Restarts every 5 minutes to ensure the worker is always running
3. Uses the same LiveKit agent entrypoint as the manual methods

You can monitor the worker's activity in the Modal dashboard under the "App" section.

### Manual Worker Execution

If you need to manually start the LiveKit worker, you can use one of these methods:

#### Method 1: Using the Modal CLI

```bash
modal run modal_livekit_agent.py::run_standalone_worker
```

This will start a LiveKit worker that connects to your LiveKit server and waits for room connections.

#### Method 2: Using the Web Endpoint

You can also start the worker by making a POST request to the `start_worker` endpoint:

```bash
curl -X POST https://alepmalagon--rataura-livekit-agent-start-worker.modal.run
```

This will spawn a new worker container and return a success message.

### Creating LiveKit Rooms via API

The Modal app includes a web endpoint that can be used to create new LiveKit rooms:

```bash
curl -X POST https://alepmalagon--rataura-livekit-agent-create-room.modal.run \
  -H "Content-Type: application/json" \
  -d '{"room_name": "my-room"}'
```

This will return a JSON response with the room details and a token that can be used to join the room.

## Configuration

### GPU Options

By default, the Modal app uses NVIDIA T4 GPUs. You can adjust the GPU type in the `modal_livekit_agent.py` file:

```python
# For T4 GPU (default)
gpu="T4"

# For A10G GPU (more powerful)
gpu="A10G"

# For H100 GPU (most powerful)
gpu="H100"

# For no GPU
gpu=None
```

### Scaling

Modal automatically scales your application based on demand. You can adjust the `min_containers` parameter to keep a certain number of instances warm to reduce cold start times:

```python
min_containers=1  # Keep one instance warm
```

### Worker Schedule

The worker is configured to restart every 5 minutes to ensure it's always running. You can adjust this interval by changing the `Period` parameter in the `keep_worker_running` function:

```python
@app.function(
    # ... other parameters ...
    schedule=Period(minutes=5),  # Restart every 5 minutes
)
def keep_worker_running():
    # ... function implementation ...
```

## Package Handling

The Modal app copies the `rataura` package to the container using shell commands. This is done using the `.run_commands()` method in the Image definition:

```python
image = (
    Image.debian_slim()
    .pip_install(
        # Dependencies...
    )
    # Copy the rataura package to the container
    .run_commands(
        "mkdir -p /root/rataura",
        "cp -r ./rataura/rataura /root/rataura/",
        "cp -r ./rataura/requirements.txt /root/rataura/",
        "cp -r ./rataura/README.md /root/rataura/",
        "ls -la /root/rataura",
    )
)
```

Additionally, each function that needs to import from the `rataura` package adds the `/root` directory to the Python path:

```python
# Add the rataura package to the Python path
import sys
sys.path.insert(0, "/root")

# Now import from rataura
from rataura.rataura.livekit_agent.agent import entrypoint, prewarm
```

Note that the import path is `rataura.rataura.livekit_agent.agent` because the `rataura` package has a nested structure with a `rataura` directory inside the `rataura` directory.

## Web Endpoints

The Modal app uses the `web_endpoint` decorator to create HTTP endpoints. Note that in Modal's 1.0 migration, this decorator is imported directly from the `modal` module:

```python
from modal import web_endpoint

@app.function(...)
@web_endpoint(method="POST")
def create_room(request):
    # Function implementation
```

## Monitoring

You can monitor your Modal app in the Modal dashboard. The dashboard provides logs, metrics, and other information about your app.

To check if the LiveKit worker is running:

1. Go to the Modal dashboard
2. Navigate to the "Apps" section
3. Select your app (rataura-livekit-agent)
4. Look for the `keep_worker_running` function in the list of functions
5. Check the logs to see if the worker is running properly

## Troubleshooting

### Common Issues

1. **Cold Start Latency**: If you experience high latency when starting new LiveKit rooms, consider increasing the `min_containers` parameter.

2. **Missing Secrets**: If you see errors about missing environment variables, make sure you've set up all the required secrets in the Modal dashboard.

3. **LiveKit Connection Issues**: If the worker can't connect to LiveKit, check your LiveKit URL and API credentials.

4. **GPU Availability**: If you're using GPUs, make sure the GPU type you've selected is available in your Modal account tier.

5. **Package Import Issues**: If you encounter import errors for the `rataura` package:
   - Make sure the `rataura` package directory is in the repository root
   - Check the logs for the output of the `ls -la /root/rataura` command to verify the package was copied correctly
   - Verify that `sys.path.insert(0, "/root")` is called before importing from `rataura`
   - Make sure you're using the correct import path: `from rataura.rataura.livekit_agent.agent import entrypoint, prewarm`
   - Check the logs for any Python import errors

6. **Worker Not Running**: If the LiveKit worker doesn't seem to be running:
   - Check the logs for the `keep_worker_running` function in the Modal dashboard
   - Try manually starting the worker using the `start_worker` endpoint
   - Make sure all required secrets are properly configured

### Getting Help

If you encounter any issues, you can:

- Check the Modal logs in the dashboard
- Join the [Modal Slack community](https://modal.com/slack)
- File an issue in the Rataura GitHub repository

## Advanced Configuration

For more advanced configuration options, refer to the [Modal documentation](https://modal.com/docs) and the [LiveKit Agents documentation](https://docs.livekit.io/agents/).
