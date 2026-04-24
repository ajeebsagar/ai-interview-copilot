"""
LockedIn AI - Main FastAPI Application.
Real-time interview copilot with audio, vision, and collaboration features.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router, ws_router
from src.config import get_settings
from src.middleware import error_handler_middleware
from src.utils import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = get_logger(__name__)

    logger.info(
        "Starting LockedIn AI",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    # Log service configurations
    logger.info(
        "Service configuration",
        whisper_model=settings.whisper_model,
        whisper_device=settings.whisper_device,
        azure_deployment=settings.azure_openai_deployment_name,
    )

    yield

    logger.info("Shutting down LockedIn AI")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        **LockedIn AI** - Real-time interview copilot

        Features:
        - 🎙️ Real-time audio transcription (Faster Whisper)
        - 🖼️ Screenshot OCR (GPT-5.4-nano Vision)
        - 👥 Duo mode collaboration (WebSocket)
        - 🧠 Context-aware AI assistance (GPT-5.4-nano)

        Created with ❤️ for interview success
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware - Allow Chrome extension origins
    # Note: Cannot use allow_credentials=True with allow_origins=["*"]
    # Either use specific origins with credentials, or wildcard without credentials
    origins_list = settings.allowed_origins_list
    use_credentials = "*" not in origins_list

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins_list,
        allow_credentials=use_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Error handling middleware
    app.middleware("http")(error_handler_middleware)

    # Include routers
    app.include_router(router, prefix="/api/v1", tags=["API"])
    app.include_router(ws_router, tags=["WebSocket"])

    return app


app = create_app()


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "LockedIn AI",
        "version": "1.0.0",
        "description": "Real-time interview copilot with AI assistance",
        "features": [
            "Audio transcription (Faster Whisper)",
            "Screenshot OCR (GPT-5.4-nano Vision)",
            "Duo mode collaboration",
            "Context-aware chat",
        ],
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
