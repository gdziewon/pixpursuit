"""
api/middleware.py

Defines middleware components for the web application. Middleware functions process
requests before they reach the actual route handlers and can modify responses before
they are sent to the client. This file includes middleware for tasks such as logging
requests, handling authentication, managing sessions, and performing request/response
transformations.
"""

from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from config.logging_config import setup_logging

logger = setup_logging(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
        Middleware for logging HTTP requests and responses.

        This middleware intercepts all incoming HTTP requests, logs the request details,
        and then passes the request through to the next middleware or endpoint. It also
        catches any exceptions thrown during the request handling, logs them, and returns
        an appropriate HTTP response.
    """
    async def dispatch(self, request: Request, call_next: callable) -> JSONResponse:
        """
            Process the incoming request, log it, and handle any exceptions.

            :param request: The incoming HTTP request.
            :param call_next: The next callable in the middleware chain.
            :return: The HTTP response to send back to the client.
        """
        try:
            # Process the request and log it
            response = await call_next(request)
            username = getattr(request.state, 'username', None)

            log_msg = f"Request: {request.method} {request.url.path}"
            if username:
                log_msg += f" - User: {username}"

            logger.info(log_msg)
            return response
        except HTTPException as http_exc:
            # Propagate HTTP exceptions without altering
            raise http_exc
        except Exception as e:
            # Log and respond to unhandled exceptions
            logger.error(f"Unhandled exception during request: {str(e)}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
