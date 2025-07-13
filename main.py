import os
import uvicorn
import asyncio

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
    match transport:
        case "streamable-http" or "http":
            asyncio.run(
                # Run as HTTP server for remote connection (Cloud Run)
                mcp.run_async(transport="http", port=port, host="0.0.0.0")
            )
        case "sse":
            asyncio.run(
                # Run as SSE server for remote connection (Cloud Run)
                mcp.run_async(transport="sse", port=port, host="0.0.0.0")
            )
        case _:
            mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
