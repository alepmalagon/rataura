# Rataura

A Python Livekit application for a Discord conversational agent that uses LLM function tools to access the EVE Online ESI API.

## Overview

Rataura is a Discord bot and Livekit agent that allows users to interact with EVE Online game data through natural language queries. The bot uses Google's Gemini model with function calling capabilities to interpret user queries and fetch relevant data from the EVE Online ESI API.

## Features

- Discord integration using Discord.py
- Livekit 1.0 agent for chat interactions
- Natural language processing of user queries using Google's Gemini model
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

# Gemini Configuration (required for both Discord bot and Livekit agent)
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp  # Optional, defaults to gemini-2.0-flash-exp

# Livekit Configuration (required only for Livekit agent)
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

### Minimum Required Environment Variables for Livekit Agent

If you only want to run the Livekit agent, you need at minimum:

```
# Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key
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

## Livekit Agent Usage

The Livekit agent is a text-only agent that responds to chat messages in the Livekit Agent Playground. To use it:

1. Run the agent with `python -m rataura.livekit_agent.run`
2. Connect to the agent using the Livekit Agent Playground
3. Send chat messages to interact with the agent

The agent will respond to your messages and use the EVE Online ESI API to fetch game data based on your queries.

## Dependencies

This project uses:
- Pydantic v2 with `pydantic-settings` package for configuration
- Google's Generative AI Python SDK for Gemini integration
- Livekit Agents 1.0 RC for the agent functionality
- Discord.py for the Discord bot integration

Make sure to install all dependencies from the requirements.txt file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
