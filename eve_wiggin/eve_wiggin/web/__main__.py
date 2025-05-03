"""
Main entry point for the EVE Wiggin web application.
"""

import logging
import argparse
from eve_wiggin.web.app import run_app
from eve_wiggin.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for the web application.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="EVE Wiggin - Web Frontend")
    parser.add_argument("--host", default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()
    
    logger.info(f"Starting {settings.app_name} Web Frontend v{settings.app_version}")
    logger.info(f"Running on {args.host}:{args.port} (debug={args.debug})")
    
    # Run the Flask application
    run_app(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()

