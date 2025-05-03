# EVE Wiggin

Strategic Analysis Tool for EVE Online Faction Warfare

## Overview

EVE Wiggin is a tool designed to analyze the status of faction warfare systems in the EVE Online universe. It provides insights into system control, victory points, and strategic importance to help players make informed decisions about their faction warfare activities.

## Features (Phase 1)

- **Warzone Status Analysis**: Get an overview of which faction is winning in each warzone based on system control
- **System Details**: Get detailed information about specific faction warfare systems
- **System Search**: Find systems by name and get their faction warfare details

## Installation

### Option 1: Development Setup

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura

# Install the main rataura package first
pip install -e .

# Install the eve_wiggin package
cd eve_wiggin
pip install -e .
```

### Option 2: Docker Setup

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura/eve_wiggin

# Build and run with docker-compose
docker-compose up --build
```

## Usage

### Python API

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

### Command Line

```bash
# Run the module directly
python -m eve_wiggin
```

## Development

### Project Structure

```
eve_wiggin/
├── eve_wiggin/
│   ├── __init__.py
│   ├── __main__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── esi_client.py
│   │   └── fw_api.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── faction_warfare.py
│   └── services/
│       ├── __init__.py
│       └── fw_analyzer.py
├── tests/
│   ├── __init__.py
│   ├── test_fw_analyzer.py
│   └── test_fw_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── setup.py
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black eve_wiggin
isort eve_wiggin
```

## Troubleshooting

### Import Errors

If you encounter import errors like `ModuleNotFoundError: No module named 'rataura'`, make sure you have installed both packages in the correct order:

1. First install the main rataura package
2. Then install the eve_wiggin package

```bash
# From the root directory
pip install -e .

# Then from the eve_wiggin directory
cd eve_wiggin
pip install -e .
```

## License

MIT
