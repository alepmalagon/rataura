# Rataura

A Python Livekit application for a Discord conversational agent that uses LLM function tools to access the EVE Online ESI API.

## Overview

Rataura is a Discord bot and Livekit agent that allows users to interact with EVE Online game data through natural language queries. The bot uses a large language model (LLM) with function calling capabilities to interpret user queries and fetch relevant data from the EVE Online ESI API.

The project consists of two main components:
1. **Discord Bot**: A Discord integration that allows users to interact with the agent through Discord channels
2. **Livekit Agent**: A conversational agent built with Livekit 1.0 that processes natural language queries and returns EVE Online data

## Features

- Discord integration using Discord.py
- Livekit 1.0 agent for chat interactions
- Natural language processing of user queries
- Access to EVE Online ESI API data
- Support for both public and authenticated ESI endpoints
- Conversational interface for exploring EVE Online game data
- Faction Warfare systems visualization and filtering
- Killmail information retrieval and analysis

## Project Structure

```
rataura/
├── .env.example           # Example environment variables file
├── LICENSE                # MIT License
├── Makefile               # Build automation
├── README.md              # Main documentation
├── README_FW_SYSTEMS.md   # Documentation for Faction Warfare systems filtering
├── eve_wiggin/            # EVE Online ESI API client library
├── rataura/               # Main application package
│   ├── rataura/           # Core application code
│   │   ├── livekit_agent/ # Livekit agent implementation
│   │   └── ...
│   └── tests/             # Test suite
├── get_killmail_info.py   # Script for retrieving killmail information
├── update_web_visualizer.py # Script for updating the web visualizer
├── requirements.txt       # Production dependencies
└── requirements-dev.txt   # Development dependencies
```

## EVE Online ESI API Integration

The bot provides access to various EVE Online ESI API endpoints, including:

- **Alliance**: Information about alliances in the game
- **Character**: Character-specific information (skills, assets, etc.)
- **Corporation**: Corporation-specific information
- **Universe**: Game universe information (systems, regions, etc.)
- **Market**: Market data (orders, prices, etc.)
- **Dogma**: Game mechanics information
- **Faction Warfare**: Faction warfare statistics and system control
- **Killmails**: Information about player kills and losses
- And more

### Faction Warfare Systems Filtering

Rataura includes tools for filtering and visualizing Faction Warfare systems. These tools help players understand the current state of faction warfare and plan their activities accordingly. For more details, see [README_FW_SYSTEMS.md](README_FW_SYSTEMS.md).

## Installation

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
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
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4  # Optional, defaults to gpt-4

# Livekit Configuration (required only for Livekit agent)
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

An example configuration file is provided in `.env.example`.

### Minimum Required Environment Variables for Livekit Agent

If you only want to run the Livekit agent, you need at minimum:

```
# LLM Configuration
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4  # Optional, defaults to gpt-4

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

### Faction Warfare System Filtering

```bash
# Filter Faction Warfare systems
python filter_fw_systems.py

# Examine filtered pickle files
python examine_filtered_pickles.py

# Update web visualizer
python update_web_visualizer.py
```

### Killmail Information

```bash
# Retrieve and analyze killmail information
python get_killmail_info.py
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 rataura eve_wiggin

# Run type checking
mypy rataura eve_wiggin
```

## Dependencies

This project uses:

- **Livekit Agents 1.0**: For building conversational agents
- **Discord.py**: For Discord integration
- **Pydantic v2**: For data validation and settings management
  - Requires the `pydantic-settings` package for the `BaseSettings` functionality
- **OpenAI and Google Generative AI**: For LLM integration
- **Requests and aiohttp**: For API communication
- **Python-dotenv**: For environment variable management
- **Loguru**: For improved logging

Make sure to install all dependencies from the requirements.txt file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

