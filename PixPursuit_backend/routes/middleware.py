from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from config.logging_config import setup_logging

logger = setup_logging(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: callable) -> JSONResponse:
        try:
            response = await call_next(request)
            username = getattr(request.state, 'username', None)

            log_msg = f"Request: {request.method} {request.url.path}"
            if username:
                log_msg += f" - User: {username}"

            logger.info(log_msg)
            return response
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Unhandled exception during request: {str(e)}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
