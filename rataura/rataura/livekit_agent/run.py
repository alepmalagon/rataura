#!/usr/bin/env python
"""
Script to run the Rataura Livekit agent.
"""

import logging
from livekit.agents import WorkerOptions, cli
from rataura.livekit_agent.agent import entrypoint, prewarm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
