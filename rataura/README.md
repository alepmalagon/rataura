# Rataura

Rataura is a Discord bot and Livekit agent that serves as a conversational agent for EVE Online players. It allows users to interact with EVE Online game data through natural language queries.

## Features

- **Discord Integration**: Uses Discord.py for chat communication
- **Livekit Agent**: Provides a text-based conversational agent using Livekit 1.0 RC
- **EVE Online ESI API Integration**: Connects to EVE Online's ESI API to fetch game data
- **LLM-Powered Conversations**: Uses Google's Gemini language models to interpret user queries and provide natural responses
- **Function Calling**: Implements a set of function tools that the LLM can use to fetch specific game data
- **Integration with zKillboard**: Fetches killmail and ship fitting data from zKillboard

## Installation

1. Clone the repository:
```bash
git clone https://github.com/alepmalagon/rataura.git
cd rataura
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```
# LLM Configuration
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro

# Livekit Configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

## Running the Livekit Agent

To run the Livekit agent:

```bash
python -m rataura.livekit_agent.run
```

Then connect to the agent using the Livekit Agent Playground.

## Available Function Tools

The agent can provide information about:

- **Alliance Information**: Get details about EVE Online alliances
- **Character Information**: Get details about EVE Online characters
- **Corporation Information**: Get details about EVE Online corporations
- **Item Information**: Get details about EVE Online items
- **Market Prices**: Get market prices for items in specific regions or systems
- **System Information**: Get details about solar systems
- **Region Information**: Get details about regions
- **Killmail Information**: Get recent killmails for characters, corporations, alliances, or ship types from zKillboard

## Example Queries

Here are some example queries you can ask the agent:

- "Tell me about the Minmatar Fleet Alliance"
- "Who is Ibn Khatab?"
- "What's the price of a Rifter in Jita?"
- "Where is the system of Hek?"
- "Show me recent losses for Ibn Khatab"
- "What ships has Black Omega Security lost recently?"
- "Show me recent Rifter kills"

## Troubleshooting

### Livekit Agent Initialization Timeout

If you encounter an initialization timeout when starting the Livekit agent:

1. Check your environment variables are correctly set
2. Ensure your Livekit server is accessible
3. Check the logs for specific error messages

### zKillboard API Errors

If you encounter zKillboard API errors:

1. Check that the zKillboard API URL is correctly formatted
2. Ensure you're following zKillboard's API usage guidelines:
   - Do not hammer the server with API requests
   - Space out requests as much as possible
   - Send 'Accept-Encoding: gzip' as header
   - Send a detailed 'User-Agent' header
3. Be aware that zKillboard has rate limits that may affect your requests
4. If you receive a 403 Forbidden error, it may be due to rate limiting or IP restrictions

## License

This project is licensed under the MIT License - see the LICENSE file for details.
