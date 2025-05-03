# EVE Wiggin

Strategic Analysis Tool for EVE Online Faction Warfare

## Overview

EVE Wiggin is a tool designed to analyze the status of faction warfare systems in the EVE Online universe. It provides insights into system control, victory points, and strategic importance to help players make informed decisions about their faction warfare activities.

## Features (Phase 1)

- **Warzone Status Analysis**: Get an overview of which faction is winning in each warzone based on system control
- **System Details**: Get detailed information about specific faction warfare systems
- **System Search**: Find systems by name and get their faction warfare details

## Installation

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura/eve_wiggin

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

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

