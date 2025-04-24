# Rataura Livekit Agent

This module implements a Livekit 1.0 worker that includes the LLM tool functions for the EVE Online ESI API. The agent interacts with users via chat in the Livekit Agent Playground.

## Features

- Chat-based interaction with users
- Access to EVE Online ESI API through function calls
- Information about alliances, characters, corporations, items, market prices, solar systems, and regions
- Search functionality for EVE Online entities

## Requirements

- Python 3.8+
- Livekit Agents 1.0.0rc0
- OpenAI API key
- EVE Online ESI API credentials

## Environment Variables

Create a `.env` file with the following variables:

```
# EVE Online ESI API settings
EVE_CLIENT_ID=your_client_id
EVE_CLIENT_SECRET=your_client_secret
EVE_CALLBACK_URL=your_callback_url
EVE_USER_AGENT="Rataura/0.1.0 (Livekit Agent)"

# LLM settings
LLM_API_KEY=your_openai_api_key
LLM_MODEL=gpt-4

# Livekit settings
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

## Running the Agent

To run the agent:

```bash
python -m rataura.livekit_agent.run
```

## Using the Agent in Livekit Agent Playground

1. Go to the [Livekit Agent Playground](https://agents-playground.livekit.io/)
2. Connect to your Livekit server using your API key and secret
3. Start a conversation with the agent
4. Ask questions about EVE Online entities, such as:
   - "Tell me about the Amarr Empire"
   - "What's the current price of PLEX in Jita?"
   - "Give me information about the character 'CCP Ghost'"
   - "What solar systems are in the Delve region?"
