# Rataura

A comprehensive EVE Online toolset featuring a Livekit conversational agent with Discord integration and strategic analysis tools for Faction Warfare.

## Project Components

This repository contains two main components:

1. **Rataura**: A Discord bot and Livekit agent that allows users to interact with EVE Online game data through natural language queries.
2. **EVE Wiggin**: A strategic analysis tool for EVE Online Faction Warfare that provides insights into system control, victory points, and strategic importance.

## Rataura: Conversational Agent

### Overview

Rataura is a Discord bot and Livekit agent that allows users to interact with EVE Online game data through natural language queries. The bot uses a large language model (LLM) with function calling capabilities to interpret user queries and fetch relevant data from the EVE Online ESI API.

### Features

- Discord integration using Discord.py
- Livekit 1.0 agent for chat interactions
- Natural language processing of user queries
- Access to EVE Online ESI API data
- Support for both public and authenticated ESI endpoints
- Conversational interface for exploring EVE Online game data

### ESI API Endpoints

The bot provides access to various EVE Online ESI API endpoints, including:

- **Alliance**: Information about alliances in the game
- **Character**: Character-specific information (skills, assets, etc.)
- **Corporation**: Corporation-specific information
- **Universe**: Game universe information (systems, regions, etc.)
- **Market**: Market data (orders, prices, etc.)
- **Dogma**: Game mechanics information
- And more

## EVE Wiggin: Faction Warfare Analysis Tool

### Overview

EVE Wiggin is a tool designed to analyze the status of faction warfare systems in the EVE Online universe. It provides insights into system control, victory points, and strategic importance to help players make informed decisions about their faction warfare activities.

### Features

- **Amarr/Minmatar Warzone Focus**: Detailed analysis of the Amarr/Minmatar warzone
- **Warzone Status Analysis**: Get an overview of which faction is winning based on system control
- **System Details**: Get detailed information about specific faction warfare systems
- **System Search**: Find systems by name and get their faction warfare details
- **Live Data**: Connects directly to EVE Online's ESI API for real-time information
- **System Adjacency Analysis**: Identifies frontline, command operations, and rearguard systems
- **Visualization**: Color-coded visualization of warzone systems and statistics
- **Sorting and Filtering**: Sort systems by name, security status, contest percentage, or region
- **Web Interface**: Browser-based dashboard for easy access and analysis

### Understanding Faction Warfare Systems

In EVE Online's faction warfare, systems have three adjacency types that determine how quickly they can be contested:

1. **Frontline Systems**: These systems can be contested at the fastest rate.
2. **Command Operations Systems**: These systems have a medium contestation rate.
3. **Rearguard Systems**: These systems have the slowest contestation rate.

The adjacency type of a system is determined by its position relative to enemy territory and can change as the warzone evolves.

## Installation

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura

# Install dependencies
pip install -r requirements.txt
```

### Rataura Installation

For the Rataura component only:

```bash
# Install Rataura with its dependencies
pip install -e ./rataura
```

### EVE Wiggin Installation

For the EVE Wiggin component only:

```bash
# Install EVE Wiggin with Flask async support
cd eve_wiggin
pip install -e ".[async]"
# Or alternatively:
pip install -e . "flask[async]>=2.0.0"
```

### Docker Setup for EVE Wiggin

```bash
# Build and run with docker-compose
cd eve_wiggin
docker-compose up --build
```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
# Discord settings
DISCORD_TOKEN=your_discord_token

# EVE Online ESI API settings
EVE_CLIENT_ID=your_eve_client_id
EVE_CLIENT_SECRET=your_eve_client_secret
EVE_CALLBACK_URL=your_callback_url
EVE_USER_AGENT=Rataura/0.1.0 (Discord Bot)

# LLM settings
LLM_API_KEY=your_llm_api_key
LLM_MODEL=gpt-4

# Livekit settings (optional)
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=your_livekit_url
```

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

### Running EVE Wiggin Web Interface

```bash
# Run the web application
cd eve_wiggin
python -m eve_wiggin.web

# Access the web interface at http://localhost:5000
```

### EVE Wiggin Command Line

```bash
# Run the module directly (default: show Amarr/Minmatar warzone)
python -m eve_wiggin

# Show details for a specific system
python -m eve_wiggin --system Huola

# Sort systems by contest percentage (highest first)
python -m eve_wiggin --sort contest

# Sort systems by region and name
python -m eve_wiggin --sort region

# Show Caldari/Gallente warzone instead
python -m eve_wiggin --warzone caldari_gallente

# Show full details for all systems
python -m eve_wiggin --full
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

### Code Formatting

```bash
black .
isort .
```

## Dependencies

This project uses:
- Pydantic v2 (requires the `pydantic-settings` package for the `BaseSettings` functionality)
- Livekit Agents 1.0 for conversational AI
- Discord.py for Discord integration
- Flask for the EVE Wiggin web interface
- NetworkX for graph analysis in EVE Wiggin

Make sure to install all dependencies from the requirements.txt file.

## Project Structure

```
rataura/
├── rataura/                # Main Rataura Discord bot and Livekit agent
│   └── livekit_agent/      # Livekit agent implementation
├── eve_wiggin/             # EVE Wiggin Faction Warfare analysis tool
│   ├── eve_wiggin/         # Core EVE Wiggin package
│   │   ├── api/            # API clients for EVE Online ESI
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── web/            # Web interface
│   └── tests/              # EVE Wiggin tests
├── requirements.txt        # Core dependencies
├── requirements-dev.txt    # Development dependencies
└── setup.py               # Package setup
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

