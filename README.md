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
- Conversational interface for exploring EVE Online game data

## ESI API Endpoints

The bot provides access to various EVE Online ESI API endpoints, including:

- **Alliance**: Information about alliances in the game
- **Character**: Character-specific information (skills, assets, etc.)
- **Corporation**: Corporation-specific information
- **Universe**: Game universe information (systems, regions, etc.)
- **Market**: Market data (orders, prices, etc.)
- **Dogma**: Game mechanics information
- And more

## Installation

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token

# EVE Online ESI API Configuration
EVE_CLIENT_ID=your_eve_client_id
EVE_CLIENT_SECRET=your_eve_client_secret
EVE_CALLBACK_URL=your_callback_url

# LLM Configuration
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4  # Optional, defaults to gpt-4

# Livekit Configuration (for Livekit agent)
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

## Usage

### Running the Discord Bot

```bash
python -m rataura
```

### Running the Livekit Agent

```bash
python -m rataura.livekit_agent.run
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Dependencies

This project uses Pydantic v2, which requires the `pydantic-settings` package for the `BaseSettings` functionality. Make sure to install all dependencies from the requirements.txt file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
