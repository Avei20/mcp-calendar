import os
import uvicorn

from dotenv import load_dotenv, find_dotenv
from app.mcp_server import mcp
from app.core.config import get_validated_settings


def main():
    """Run the Google Calendar MCP Server."""
    # Load environment variables from .env file
    # load_dotenv()

    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "8081"))

    # Determine transport type (default to streamable-http for Cloud Run)
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")

    # Run the MCP server
    if transport == "streamable-http":
        # Run as HTTP server for remote connection (Cloud Run)
        mcp.run(transport="streamable-http", port=port)
    else:
        # Run as stdio server for local development
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
