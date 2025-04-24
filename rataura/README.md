# Rataura

Rataura is a conversational agent for EVE Online players. It allows users to interact with EVE Online game data through natural language queries.

## Features

- **Discord Bot**: Interact with EVE Online data through Discord chat
- **Livekit Agent**: Chat with the agent in the Livekit Agent Playground
- **EVE Online ESI API Integration**: Access to game data through the ESI API
- **LLM-Powered Conversations**: Natural language understanding and generation

## Components

### Discord Bot

The Discord bot allows users to interact with EVE Online data through Discord chat. It uses Discord.py and Livekit 1.0 RC for voice/chat communication.

### Livekit Agent

The Livekit agent is a standalone worker that includes the LLM tool functions for the ESI API. It allows users to chat with the agent in the Livekit Agent Playground.

See the [Livekit Agent README](./rataura/livekit_agent/README.md) for more information.

### EVE Online ESI API Client

The ESI API client provides access to EVE Online game data, including:

- Alliances, characters, and corporations
- Item details and market prices
- Solar systems and regions
- Game mechanics and universe information

### LLM Function Tools

The LLM function tools allow the agent to fetch specific game data based on user queries. These tools are used by both the Discord bot and the Livekit agent.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/alepmalagon/rataura.git
cd rataura
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys and configuration (see the example in the Livekit Agent README).

## Usage

### Running the Discord Bot

```bash
python -m rataura
```

### Running the Livekit Agent

```bash
python -m rataura.livekit_agent.run
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
