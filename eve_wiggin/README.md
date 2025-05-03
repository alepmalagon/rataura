# EVE Wiggin

Strategic Analysis Tool for EVE Online Faction Warfare

## Overview

EVE Wiggin is a tool designed to analyze the status of faction warfare systems in the EVE Online universe. It provides insights into system control, victory points, and strategic importance to help players make informed decisions about their faction warfare activities.

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/alepmalagon/rataura.git
cd rataura
```

2. Install both packages in development mode:
```bash
# Install the main rataura package
pip install -e .

# Install the eve_wiggin package
cd eve_wiggin
pip install -e .
```

3. Run the application:
```bash
python -m eve_wiggin
```

### Using Docker

1. Clone the repository:
```bash
git clone https://github.com/alepmalagon/rataura.git
cd rataura
```

2. Build and run using docker-compose:
```bash
cd eve_wiggin
docker-compose up --build
```

## Features (Phase 1)

- Warzone status analysis: Get an overview of which faction is winning in each warzone
- System details: Get detailed information about specific faction warfare systems
- System search: Find systems by name and get their faction warfare details

## Usage

```python
import asyncio
from eve_wiggin.api.fw_api import FWApi

async def main():
    # Initialize the API
    fw_api = FWApi()
    
    # Get warzone status
    warzone_status = await fw_api.get_warzone_status()
    print(warzone_status)
    
    # Get details for a specific system
    system_details = await fw_api.search_system("Tama")
    print(system_details)

if __name__ == "__main__":
    asyncio.run(main())
```

## Project Structure

```
eve_wiggin/
├── eve_wiggin/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── esi_client.py  # ESI API client adapter
│   │   └── fw_api.py      # Faction Warfare API
│   ├── models/
│   │   ├── __init__.py
│   │   └── faction_warfare.py  # Data models for FW
│   ├── services/
│   │   ├── __init__.py
│   │   └── fw_analyzer.py  # FW data analysis service
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging.py  # Logging utilities
│   ├── __init__.py
│   ├── __main__.py  # Entry point
│   └── config.py  # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_fw_analyzer.py
│   └── test_fw_api.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements.txt
├── setup.py
└── pytest.ini
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black eve_wiggin
isort eve_wiggin
```

## Docker

To build and run the Docker container:

```bash
# Build the Docker image
docker build -t eve_wiggin .

# Run the container
docker run -it eve_wiggin
```

## License

MIT
