#!/usr/bin/env python3
"""
Analyze Adjacency Reasoning for EVE Wiggin.

This script runs the adjacency logger to display detailed reasoning for each system's
adjacency classification. It helps identify why only a few systems are getting their
adjacency correctly assigned.
"""

import asyncio
import logging
import os
import sys

# Add the parent directory to the path so we can import the eve_wiggin package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eve_wiggin.services.adjacency_logger import log_adjacency_reasoning

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Run the adjacency reasoning analysis
    print("Analyzing adjacency reasoning for EVE Wiggin systems...")
    print("This will help identify why only a few systems are getting their adjacency correctly assigned.")
    print("=" * 80)
    
    # Run the async function
    asyncio.run(log_adjacency_reasoning())
    
    print("=" * 80)
    print("Analysis complete. Check the logs above for detailed reasoning on each system's adjacency classification.")
    print("Look for warnings about missing frontlines or potential frontlines not marked as such.")

