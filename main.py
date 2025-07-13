import os
import uvicorn
import asyncio

from dotenv import load_dotenv, find_dotenv
from app.mcp_server import mcp
from app.core.config import get_validated_settings

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import PlainTextResponse

# Mount MCP server at /mcp using FastAPI
mcp_app = mcp.http_app(path='/calendar')
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)


def main():
    """Run the Google Calendar MCP Server as a FastAPI app."""
    # Load environment variables from .env file if needed
    # load_dotenv()

    port = int(os.getenv("PORT", "8081"))
    # Run FastAPI app with uvicorn
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)


# Add OAuth callback route using FastMCP custom_route decorator
@mcp.custom_route("/oauth/callback", methods=["GET", "POST"])
async def oauth_callback(request: Request):
    # Extract code from query params (GET) or form data (POST)
    code = request.query_params.get("code") or (await request.form()).get("code")
    user_id = request.query_params.get("user_id") or "default"
    if not code:
        return PlainTextResponse("Missing authorization code", status_code=400)
    try:
        with get_db() as db:
            token_data = exchange_code_for_token(code=code, db=db, user_id=user_id)
            return PlainTextResponse(f"OAuth callback handled. Token stored for user {user_id}.")
    except Exception as e:
        return PlainTextResponse(f"OAuth callback failed: {str(e)}", status_code=500)

if __name__ == "__main__":
    main()
