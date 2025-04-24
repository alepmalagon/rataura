# Rataura

A Python Livekit application for a Discord conversational agent that uses LLM function tools to access the EVE Online ESI API.

## Overview

Rataura is a Discord bot and Livekit agent that allows users to interact with EVE Online game data through natural language queries. The bot uses a large language model (LLM) with function calling capabilities to interpret user queries and fetch relevant data from the EVE Online ESI API.

## Features

- Discord integration using Discord.py
- Livekit 1.0 agent for chat interactions
- Natural language processing of user queries
- Access to EVE Online ESI API data
- Support for both public and authenticated ESI endpoints
- Function calling to fetch specific game data

## Components

### Discord Bot

The Discord bot allows users to interact with the agent through Discord channels. It uses Discord.py to handle Discord events and messages.

### Livekit Agent

The Livekit agent is a standalone worker that includes the LLM tool functions for the ESI API. It allows users to chat with the agent in the Livekit Agent Playground.

### ESI API Client

The ESI API client provides access to the EVE Online ESI API. It handles authentication, rate limiting, and error handling.

### LLM Function Tools

The LLM function tools allow the agent to fetch specific game data based on user queries. These tools are used by both the Discord bot and the Livekit agent.

## Installation

```bash
git clone https://github.com/yourusername/rataura.git
cd rataura
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Discord Bot Configuration (required only for Discord bot)
DISCORD_TOKEN=your_discord_token

# EVE Online ESI API Configuration (optional for basic Livekit agent)
EVE_CLIENT_ID=your_eve_client_id
EVE_CLIENT_SECRET=your_eve_client_secret
EVE_CALLBACK_URL=your_callback_url

# LLM Configuration (required for both Discord bot and Livekit agent)
LLM_PROVIDER=openai  # or "gemini" to use Google's Gemini model
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4  # Optional, defaults to gpt-4

# Gemini Configuration (only required if LLM_PROVIDER=gemini)
GEMINI_API_KEY=your_gemini_api_key  # Optional, will use LLM_API_KEY if not provided
GEMINI_MODEL=gemini-2.0-flash-exp  # Optional, defaults to gemini-2.0-flash-exp

# Livekit Configuration (required only for Livekit agent)
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

### Minimum Required Environment Variables for Livekit Agent

If you only want to run the Livekit agent, you need at minimum:

```
# LLM Configuration
LLM_PROVIDER=openai  # or "gemini" to use Google's Gemini model
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4  # Optional, defaults to gpt-4

# Gemini Configuration (only if using Gemini)
GEMINI_API_KEY=your_gemini_api_key  # Optional, will use LLM_API_KEY if not provided
GEMINI_MODEL=gemini-2.0-flash-exp  # Optional, defaults to gemini-2.0-flash-exp

# Livekit Configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

The Discord and EVE Online ESI API settings are optional for the Livekit agent, but required for the Discord bot.

## Usage

### Running the Discord Bot

```bash
python -m rataura
```

### Running the Livekit Agent

```bash
python -m rataura.livekit_agent.run
```

## Troubleshooting

### Livekit Agent Initialization Timeout

If you encounter an initialization timeout error like this:

```
livekit.agents - ERROR - initialization timed out, killing process
```

This can happen because the agent needs more time to initialize resources. The latest version includes:

1. Improved logging to help diagnose initialization issues
2. Prewarming of the ESI client to avoid delays during job initialization
3. Increased initialization timeout (30 seconds instead of the default)
4. Better error handling and validation of required settings

If you still encounter timeout issues, you can try:

1. Check your environment variables are correctly set
2. Ensure your network connection to Livekit servers is stable
3. Monitor the logs for specific error messages that might indicate the root cause

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

## Dependencies

This project uses Pydantic v2, which requires the `pydantic-settings` package for the `BaseSettings` functionality. Make sure to install all dependencies from the requirements.txt file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
