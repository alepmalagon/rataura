# EVE Wiggin

Strategic Analysis Tool for EVE Online Faction Warfare

## Overview

EVE Wiggin is a tool designed to analyze the status of faction warfare systems in the EVE Online universe. It provides insights into system control, victory points, and strategic importance to help players make informed decisions about their faction warfare activities.

## Features

- **Amarr/Minmatar Warzone Focus**: Detailed analysis of the Amarr/Minmatar warzone
- **Warzone Status Analysis**: Get an overview of which faction is winning based on system control
- **System Details**: Get detailed information about specific faction warfare systems
- **System Search**: Find systems by name and get their faction warfare details
- **Live Data**: Connects directly to EVE Online's ESI API for real-time information
- **System Adjacency Analysis**: Identifies frontline, command operations, and rearguard systems
- **Visualization**: Color-coded visualization of warzone systems and statistics
- **Sorting and Filtering**: Sort systems by name, security status, contest percentage, or region
- **Web Interface**: Browser-based dashboard for easy access and analysis

## Understanding Faction Warfare Systems

### System Contestation

In EVE Online's faction warfare, all systems can be contested regardless of their adjacency type. The ESI API provides a `contested` status for each system, which indicates whether a system is being actively fought over.

### Victory Points

Victory points represent progress toward capturing a system. All systems can accumulate victory points, including rearguards. When a system reaches its victory point threshold, it becomes vulnerable to capture.

### System Adjacency Types

Systems in faction warfare have three adjacency types that determine how quickly they can be contested:

1. **Frontline Systems**: These systems can be contested at the fastest rate. Players can accumulate victory points quickly in these systems.

2. **Command Operations Systems**: These systems have a medium contestation rate. Victory points accumulate at a moderate pace.

3. **Rearguard Systems**: These systems have the slowest contestation rate. Victory points accumulate very slowly in these systems.

The adjacency type of a system is determined by its position relative to enemy territory and can change as the warzone evolves.

## Installation

### Option 1: Development Setup

```bash
# Clone the repository
git clone https://github.com/alepmalagon/rataura.git
cd rataura/eve_wiggin

# Install the eve_wiggin package with Flask async support
pip install -e ".[async]"
# Or alternatively:
pip install -e . "flask[async]>=2.0.0"
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

### Web Interface

```bash
# Run the web application
python -m eve_wiggin.web

# Access the web interface at http://localhost:5000
```

The web interface provides a user-friendly dashboard for analyzing faction warfare data:

1. Select the warzone (Amarr/Minmatar or Caldari/Gallente)
2. Choose how to sort the systems (by name, security, contest percentage, or region)
3. Click the "Strategic Analysis" button to view the current state of the warzone
4. Search for specific systems to get detailed information

### Command Line

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

### Python API

```python
import asyncio
from eve_wiggin.api.fw_api import FWApi
from eve_wiggin.models.faction_warfare import Warzone

async def main():
    # Initialize the API
    fw_api = FWApi()
    
    # Get warzone status
    warzone_status = await fw_api.get_warzone_status()
    
    # Access Amarr/Minmatar warzone data
    amarr_minmatar = warzone_status["warzones"][Warzone.AMARR_MINMATAR]
    print(f"Amarr/Minmatar Warzone - Total Systems: {amarr_minmatar['total_systems']}")
    
    # Get details for a specific system in the Amarr/Minmatar warzone
    system_details = await fw_api.search_system("Huola")
    print(system_details)
    
    # Get all systems in the Amarr/Minmatar warzone
    warzone_systems = await fw_api.get_warzone_systems(Warzone.AMARR_MINMATAR)
    print(f"Total systems in warzone: {len(warzone_systems)}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Docker Deployment

The EVE Wiggin application can be easily deployed using Docker:

```bash
# Build the Docker image
docker build -t eve_wiggin .

# Run the container (web interface)
docker run -p 5000:5000 eve_wiggin

# Run the container (CLI version)
docker run eve_wiggin python -m eve_wiggin
```

Or using docker-compose:

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Project Structure

```
eve_wiggin/
├── eve_wiggin/
│   ├── __init__.py
│   ├── __main__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── esi_client.py
│   │   ├── mock_esi_client.py
│   │   └── fw_api.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── faction_warfare.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── fw_analyzer.py
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── console.py
│   └── web/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── web_visualizer.py
│       ├── templates/
│       │   └── index.html
│       └── static/
│           ├── css/
│           │   └── style.css
│           └── js/
│               └── main.js
├── tests/
│   ├── __init__.py
│   ├── test_fw_analyzer.py
│   ├── test_fw_api.py
│   └── test_visualization.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── setup.py
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

## Data Sources

EVE Wiggin connects to the EVE Online ESI API to fetch real-time data about faction warfare systems, including:

- System ownership and control
- Victory points and thresholds
- Contested status
- Faction statistics

The application focuses specifically on the Amarr/Minmatar warzone, providing detailed analysis of this conflict zone.

## Future Enhancements (Planned for Phase 2)

- **Interactive Map**: Visual representation of the warzone with system connections
- **Time Series Analysis**: Track system changes over time to identify trends
- **Prediction Models**: Forecast when systems are likely to change hands
- **Alert System**: Notify users when key systems are at risk
- **Mobile Responsiveness**: Optimize the web interface for mobile devices
- **User Accounts**: Save preferences and receive personalized alerts

## License

MIT
