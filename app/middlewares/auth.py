from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import McpError
from mcp.types import ErrorData

class TokenAuthenticationMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        # Extract token from request body
        token = None
        if context.message and isinstance(context.message, dict):
            token = context.message.get("token")

        if not token:
            raise McpError(ErrorData(code=-32000, message="No Token Provided, Please Autheticate"))

        # Validate the Google OAuth token
        from app.mcp_server import validate_google_token
        if not validate_google_token(token):
            raise McpError(ErrorData(code=-32000, message="Invalid Google OAuth token"))

        return await call_next(context)
