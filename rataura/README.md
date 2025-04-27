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
- Integration with zKillboard for killmail and ship fitting data

## Components

### Discord Bot

The Discord bot allows users to interact with the agent through Discord channels. It uses Discord.py to handle Discord events and messages.

### Livekit Agent

The Livekit agent is a standalone worker that includes the LLM tool functions for the ESI API. It allows users to chat with the agent in the Livekit Agent Playground.

### ESI API Client

The ESI API client provides access to the EVE Online ESI API. It handles authentication, rate limiting, and error handling.

### LLM Function Tools

The LLM function tools allow the agent to fetch specific game data based on user queries. These tools are used by both the Discord bot and the Livekit agent.

#### Available Function Tools

- **Alliance Information**: Get details about EVE Online alliances
- **Character Information**: Get details about EVE Online characters
- **Corporation Information**: Get details about EVE Online corporations
- **Item Information**: Get details about EVE Online items
- **Market Prices**: Get market prices for items in specific regions or systems
- **System Information**: Get details about solar systems
- **Region Information**: Get details about regions
- **Killmail Information**: Get recent killmails for characters, corporations, alliances, or ship types from zKillboard

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
GEMINI_MODEL=gemini-2.0-flash  # Optional, defaults to gemini-2.0-flash

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
GEMINI_MODEL=gemini-2.0-flash  # Optional, defaults to gemini-2.0-flash

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

### Example Queries

Here are some example queries you can ask the agent:

- "Tell me about the Minmatar Fleet Alliance"
- "Who is Ibn Khatab?"
- "What's the price of a Rifter in Jita?"
- "Where is the system of Hek?"
- "Tell me about The Forge region"
- "Show me recent losses for Ibn Khatab"
- "What ships has Black Omega Security lost recently?"
- "Show me recent Rifter kills"

### Chat Implementation Details

The Livekit agent uses the standard Livekit Agents 1.0 text handling mechanism:

1. The agent implements the `on_text` method to receive incoming chat messages from the `lk.chat` topic
2. Generates a response using the LLM with function calling
3. The response is automatically sent to the `lk.transcription` topic by the AgentSession

This bidirectional communication allows users to have a conversation with the agent in the Livekit Agent Playground.

## Troubleshooting

### Chat Messages Not Working

If the agent is not responding to chat messages:

1. Check the logs for any errors related to text streams
2. Make sure you're using the correct method name: `on_text` instead of `on_chat_message`
3. Verify that `text_enabled=True` is set in `RoomInputOptions` and `transcription_enabled=True` in `RoomOutputOptions`
4. Ensure that the agent is properly connected to the room
5. Check that you're using the correct Livekit Agents version (1.0.0rc1 or higher)

### ESI API Errors

If you encounter ESI API errors:

1. Check that the ESI API endpoints are correctly implemented
2. Verify that the search functionality is using the `/universe/ids/` endpoint instead of the deprecated `/search/` endpoint
3. Make sure you have proper error handling in place

### zKillboard API Errors

If you encounter zKillboard API errors:

1. Check that the zKillboard API URL is correctly formatted
2. Verify that you're using the correct parameters for the API
3. Make sure you have proper error handling in place
4. Be aware that zKillboard has rate limits that may affect your requests

## Dependencies

This project uses:
- Pydantic v2 with `pydantic-settings` package for configuration
- Google's Generative AI Python SDK for Gemini integration
- Livekit Agents 1.0 RC for the agent functionality
- Discord.py for the Discord bot integration
- aiohttp for making HTTP requests to external APIs

Make sure to install all dependencies from the requirements.txt file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
