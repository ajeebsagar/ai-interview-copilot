"""
REST API routes for LockedIn AI.
Provides endpoints for chat, audio transcription, vision analysis, and session management.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.config import Settings, get_settings
from src.middleware import verify_api_key
from src.models import (
    AudioTranscriptionResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    HealthResponse,
    MessageRole,
    QuestionType,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionInfoResponse,
    SessionJoinRequest,
    SessionJoinResponse,
    VisionAnalysisRequest,
    VisionAnalysisResponse,
)
from src.services import (
    AudioService,
    AzureOpenAIService,
    ContextService,
    SessionService,
    VisionService,
)
from src.utils import get_logger

logger = get_logger(__name__)

router = APIRouter()

# ============================================================================
# Dependency Injection
# ============================================================================


def get_openai_service(settings: Annotated[Settings, Depends(get_settings)]) -> AzureOpenAIService:
    """Get Azure OpenAI service instance."""
    return AzureOpenAIService(settings)


def get_audio_service(settings: Annotated[Settings, Depends(get_settings)]) -> AudioService:
    """Get Audio service instance."""
    return AudioService(settings)


def get_vision_service(
    settings: Annotated[Settings, Depends(get_settings)],
    openai_service: Annotated[AzureOpenAIService, Depends(get_openai_service)],
) -> VisionService:
    """Get Vision service instance."""
    return VisionService(settings, openai_service)


def get_session_service(settings: Annotated[Settings, Depends(get_settings)]) -> SessionService:
    """Get Session service instance (singleton)."""
    if not hasattr(get_session_service, "_instance"):
        get_session_service._instance = SessionService(settings)
    return get_session_service._instance


def get_context_service(settings: Annotated[Settings, Depends(get_settings)]) -> ContextService:
    """Get Context service instance (singleton)."""
    if not hasattr(get_context_service, "_instance"):
        get_context_service._instance = ContextService(settings)
    return get_context_service._instance


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health", response_model=HealthResponse)
async def health_check(
    openai_service: Annotated[AzureOpenAIService, Depends(get_openai_service)],
    audio_service: Annotated[AudioService, Depends(get_audio_service)],
):
    """
    Health check endpoint.
    Verifies all services are operational.
    """
    services_status = {
        "openai": "healthy" if await openai_service.health_check() else "unhealthy",
        "audio": "healthy" if await audio_service.health_check() else "unhealthy",
    }

    return HealthResponse(
        status="healthy" if all(s == "healthy" for s in services_status.values()) else "degraded",
        version="1.0.0",
        services=services_status,
    )


# ============================================================================
# Chat Endpoints
# ============================================================================


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    dependencies=[Depends(verify_api_key)],
)
async def chat_completions(
    request: ChatCompletionRequest,
    openai_service: Annotated[AzureOpenAIService, Depends(get_openai_service)],
    context_service: Annotated[ContextService, Depends(get_context_service)],
):
    """
    Create a chat completion with context awareness.

    If session_id is provided, conversation history is automatically included.
    """
    try:
        logger.info("Chat completion request received")
        logger.info(f"Request type: {type(request)}")
        logger.info(f"Request messages: {len(request.messages)}")
        logger.info(f"First message role type: {type(request.messages[0].role)}")
        logger.info(f"First message role: {request.messages[0].role}")
        # Get context if session_id provided
        if request.session_id:
            context_messages = await context_service.get_context(
                request.session_id,
                max_tokens=request.max_tokens // 2,  # Reserve half for context
            )

            # Merge context with new messages
            all_messages = context_messages + request.messages
            request.messages = all_messages

            logger.info(
                "Using context for chat completion",
                session_id=request.session_id,
                context_messages=len(context_messages),
            )

        # Get AI response
        response = await openai_service.chat_completion(request)

        # Add to context if session_id provided
        if request.session_id:
            # Add user message
            user_message = request.messages[-1]
            user_role = user_message.role.value if hasattr(user_message.role, "value") else user_message.role
            await context_service.add_message(
                request.session_id,
                user_role,
                user_message.content,
            )

            # Add assistant response
            await context_service.add_message(
                request.session_id,
                MessageRole.ASSISTANT.value if hasattr(MessageRole.ASSISTANT, "value") else "assistant",
                response.content,
            )

        return response

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error("Chat completion failed", error=str(e), traceback=error_trace)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ============================================================================
# Audio Endpoints
# ============================================================================


@router.post(
    "/audio/transcribe",
    response_model=AudioTranscriptionResponse,
    dependencies=[Depends(verify_api_key)],
)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = Form(default="en", description="Language code (en, es, fr, etc.)"),
    session_id: str = Form(default=None, description="Optional session ID"),
    audio_service: AudioService = Depends(get_audio_service),
):
    """
    Transcribe an audio file to text using Faster Whisper.

    Supports: WAV, MP3, M4A, FLAC, OGG, etc.
    """
    try:
        # Read audio file
        audio_bytes = await audio.read()

        logger.info(
            "Transcribing audio",
            filename=audio.filename,
            size_bytes=len(audio_bytes),
            language=language,
        )

        # Transcribe
        response = await audio_service.transcribe_audio_bytes(
            audio_bytes,
            language=language,
            audio_format=audio.filename.split(".")[-1] if audio.filename else "wav",
        )

        response.session_id = session_id

        return response

    except Exception as e:
        logger.error("Audio transcription failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Vision Endpoints
# ============================================================================


@router.post(
    "/vision/analyze",
    response_model=VisionAnalysisResponse,
    dependencies=[Depends(verify_api_key)],
)
async def analyze_screenshot(
    image: UploadFile = File(..., description="Screenshot image to analyze"),
    include_code: bool = Form(default=True, description="Extract code snippets"),
    question_type: str = Form(default=None, description="Question type hint"),
    vision_service: VisionService = Depends(get_vision_service),
):
    """
    Analyze a screenshot and extract interview question using GPT-5.4-nano Vision.

    Extracts:
    - Question text
    - Code snippets
    - Constraints
    - Examples
    - Difficulty
    - Tags
    """
    try:
        # Read image
        image_bytes = await image.read()

        logger.info(
            "Analyzing screenshot",
            filename=image.filename,
            size_bytes=len(image_bytes),
            include_code=include_code,
        )

        # Parse question type
        q_type = None
        if question_type:
            try:
                q_type = QuestionType(question_type)
            except ValueError:
                pass

        # Create request
        request = VisionAnalysisRequest(
            include_code=include_code,
            question_type=q_type,
        )

        # Analyze
        response = await vision_service.analyze_screenshot(image_bytes, request)

        return response

    except Exception as e:
        logger.error("Vision analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Session Endpoints (Duo Mode)
# ============================================================================


@router.post(
    "/sessions",
    response_model=SessionCreateResponse,
    dependencies=[Depends(verify_api_key)],
)
async def create_session(
    request: SessionCreateRequest,
    session_service: SessionService = Depends(get_session_service),
):
    """
    Create a new Duo mode session.

    Returns session_id and invite_code to share with partner.
    """
    try:
        response = await session_service.create_session(request)
        return response

    except Exception as e:
        logger.error("Session creation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/sessions/{session_id}/join",
    response_model=SessionJoinResponse,
    dependencies=[Depends(verify_api_key)],
)
async def join_session(
    session_id: str,
    request: SessionJoinRequest,
    session_service: SessionService = Depends(get_session_service),
):
    """
    Join an existing Duo mode session using invite code.
    """
    try:
        response = await session_service.join_session(session_id, request)
        return response

    except Exception as e:
        logger.error("Join session failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/sessions/{session_id}",
    response_model=SessionInfoResponse,
    dependencies=[Depends(verify_api_key)],
)
async def get_session(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    """
    Get information about a Duo mode session.
    """
    try:
        response = await session_service.get_session_info(session_id)
        return response

    except Exception as e:
        logger.error("Get session failed", error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
