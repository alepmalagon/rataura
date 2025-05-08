# Rataura

A Python Livekit application for a Discord conversational agent that uses LLM function tools to access the EVE Online ESI API.

## Overview

Rataura is a Discord bot and Livekit agent that allows users to interact with EVE Online game data through natural language queries. The bot uses a large language model (LLM) with function calling capabilities to interpret user queries and fetch relevant data from the EVE Online ESI API.

This repository contains two main components:
1. **Rataura**: A conversational agent for Discord and Livekit that provides natural language access to EVE Online data
2. **EVE Wiggin**: A strategic analysis tool for EVE Online Faction Warfare

## Features

### Rataura Agent
- Discord integration using Discord.py
- Livekit 1.0 agent for chat interactions
- Natural language processing of user queries
- Access to EVE Online ESI API data
- Support for both public and authenticated ESI endpoints
- Conversational interface for exploring EVE Online game data

### EVE Wiggin Analysis Tool
- **Warzone Analysis**: Detailed analysis of Amarr/Minmatar and Caldari/Gallente warzones
- **System Adjacency Analysis**: Identifies frontline, command operations, and rearguard systems
- **Visualization**: Color-coded visualization of warzone systems and statistics
- **Web Interface**: Browser-based dashboard for easy access and analysis
- **Command Line Interface**: Quick access to faction warfare data

## ESI API Endpoints

The bot provides access to various EVE Online ESI API endpoints, including:

- **Alliance**: Information about alliances in the game
- **Character**: Character-specific information (skills, assets, etc.)
- **Corporation**: Corporation-specific information
- **Universe**: Game universe information (systems, regions, etc.)
- **Market**: Market data (orders, prices, etc.)
- **Dogma**: Game mechanics information
- **Faction Warfare**: Warzone control, victory points, and system status
- And more

## Installation

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura

# Install dependencies
pip install -r requirements.txt
```

### Installing EVE Wiggin Component

```bash
# Navigate to the EVE Wiggin directory
cd eve_wiggin

# Install the eve_wiggin package with Flask async support
pip install -e ".[async]"
# Or alternatively:
pip install -e . "flask[async]>=2.0.0"
```

### Docker Setup for EVE Wiggin

```bash
# Navigate to the EVE Wiggin directory
cd eve_wiggin

# Build and run with docker-compose
docker-compose up --build
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

### EVE Wiggin Command Line Interface

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

## Faction Warfare Systems Analysis

The EVE Wiggin component provides detailed analysis of faction warfare systems:

### System Adjacency Types

Systems in faction warfare have three adjacency types that determine how quickly they can be contested:

1. **Frontline Systems**: These systems can be contested at the fastest rate. Players can accumulate victory points quickly in these systems.

2. **Command Operations Systems**: These systems have a medium contestation rate. Victory points accumulate at a moderate pace.

3. **Rearguard Systems**: These systems have the slowest contestation rate. Victory points accumulate very slowly in these systems.

The adjacency type of a system is determined by its position relative to enemy territory and can change as the warzone evolves.

### Faction Warfare Systems Filtering

The repository includes scripts for filtering faction warfare systems:

- `filter_fw_systems.py`: Filters systems for each warzone
- `examine_filtered_pickles.py`: Verifies filtered data
- `update_web_visualizer.py`: Updates the web visualizer to use filtered data

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting (for EVE Wiggin)
cd eve_wiggin
black eve_wiggin
isort eve_wiggin
```

## Project Structure

```
rataura/
├── rataura/                  # Main Rataura agent package
│   ├── __init__.py
│   ├── __main__.py
│   ├── livekit_agent/        # Livekit agent implementation
│   └── ...
├── eve_wiggin/               # EVE Wiggin analysis tool
│   ├── eve_wiggin/
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── api/              # API clients for EVE Online
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   ├── visualization/    # Data visualization
│   │   └── web/              # Web interface
│   ├── tests/                # EVE Wiggin tests
│   ├── Dockerfile
│   └── docker-compose.yml
├── README.md                 # This file
├── README_FW_SYSTEMS.md      # Faction Warfare systems documentation
├── requirements.txt          # Project dependencies
├── requirements-dev.txt      # Development dependencies
└── setup.py                  # Package setup
```

## Dependencies

This project uses:
- Pydantic v2, which requires the `pydantic-settings` package for the `BaseSettings` functionality
- Livekit Agents 1.0 for conversational AI
- Discord.py for Discord integration
- Flask for the EVE Wiggin web interface
- Various EVE Online API clients

Make sure to install all dependencies from the requirements.txt file.

## Future Enhancements

### Planned for Rataura
- Support for additional LLM providers
- Enhanced conversation history management
- More sophisticated query understanding
- Integration with additional EVE Online data sources

### Planned for EVE Wiggin
- Interactive map with system connections
- Time series analysis to track system changes
- Prediction models for system control changes
- Alert system for key systems at risk
- Mobile-responsive web interface
- User accounts for personalized alerts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

