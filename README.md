# Rataura

A comprehensive suite of EVE Online tools including a Livekit conversational agent with function tools for accessing the EVE Online ESI API and EVE Wiggin, a strategic analysis tool for Faction Warfare.

## Project Components

This repository contains two main components:

1. **Rataura**: A conversational agent that uses LLM function tools to access the EVE Online ESI API.
   - Discord bot integration
   - Livekit agent for chat interactions
   - Natural language processing of user queries
   - Access to EVE Online ESI API data

2. **EVE Wiggin**: A strategic analysis tool for EVE Online Faction Warfare.
   - Detailed analysis of faction warfare systems
   - Warzone status visualization
   - System adjacency analysis
   - Web interface for easy access and analysis

## Rataura Features

- Discord integration using Discord.py
- Livekit 1.0 agent for chat interactions
- Natural language processing of user queries
- Access to EVE Online ESI API data
- Support for both public and authenticated ESI endpoints
- Conversational interface for exploring EVE Online game data

### ESI API Endpoints

The agent provides access to various EVE Online ESI API endpoints, including:

- **Alliance**: Information about alliances in the game
- **Character**: Character-specific information (skills, assets, etc.)
- **Corporation**: Corporation-specific information
- **Universe**: Game universe information (systems, regions, etc.)
- **Market**: Market data (orders, prices, etc.)
- **Dogma**: Game mechanics information
- And more

## EVE Wiggin Features

- **Amarr/Minmatar and Caldari/Gallente Warzone Focus**: Detailed analysis of both warzones
- **Warzone Status Analysis**: Get an overview of which faction is winning based on system control
- **System Details**: Get detailed information about specific faction warfare systems
- **System Adjacency Analysis**: Identifies frontline, command operations, and rearguard systems
- **Visualization**: Color-coded visualization of warzone systems and statistics
- **Web Interface**: Browser-based dashboard for easy access and analysis

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
# Navigate to the EVE Wiggin directory
cd eve_wiggin

# Run the web application
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

# Show Caldari/Gallente warzone instead
python -m eve_wiggin --warzone caldari_gallente
```

## Docker Deployment

Both components can be deployed using Docker:

### Rataura Livekit Agent

```bash
# Build and run with docker
docker build -t rataura -f Dockerfile.rataura .
docker run -p 8000:8000 rataura
```

### EVE Wiggin

```bash
# Navigate to the EVE Wiggin directory
cd eve_wiggin

# Build and run with docker-compose
docker-compose up --build
```

## Project Structure

```
rataura/
├── rataura/
│   ├── discord/       # Discord bot implementation
│   ├── esi/           # EVE Online ESI API client
│   │   └── endpoints/ # ESI API endpoint implementations
│   ├── livekit_agent/ # Livekit agent implementation
│   ├── llm/           # LLM integration and function tools
│   └── utils/         # Utility functions
├── eve_wiggin/
│   ├── api/           # EVE Online API client for faction warfare
│   ├── models/        # Data models for faction warfare
│   ├── services/      # Business logic for analyzing faction warfare
│   ├── visualization/ # Console and web visualization
│   └── web/           # Web interface for faction warfare analysis
└── tests/             # Test suites for both components
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

