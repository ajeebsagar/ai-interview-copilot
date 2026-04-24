"""
Global error handling middleware.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse

from src.utils import AIProviderError, AuthenticationError, RateLimitError, get_logger

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handler middleware.

    Catches all exceptions and returns appropriate JSON responses.
    """
    try:
        return await call_next(request)
    except AuthenticationError as e:
        logger.error("Authentication error", error=str(e), path=request.url.path)
        return JSONResponse(
            status_code=e.status_code,
            content={"error": "Authentication failed", "detail": e.message},
        )
    except RateLimitError as e:
        logger.error("Rate limit error", error=str(e), path=request.url.path)
        return JSONResponse(
            status_code=e.status_code,
            content={"error": "Rate limit exceeded", "detail": e.message},
        )
    except AIProviderError as e:
        logger.error("AI provider error", error=str(e), path=request.url.path)
        return JSONResponse(
            status_code=e.status_code,
            content={"error": "AI provider error", "detail": e.message},
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error("Unexpected error", error=str(e), path=request.url.path, traceback=error_traceback)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error", "detail": str(e)},
        )
