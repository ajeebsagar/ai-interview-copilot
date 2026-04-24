"""
WebSocket endpoints for real-time features.
Supports Duo mode collaboration and audio streaming.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query

from src.config import Settings, get_settings
from src.models import DuoMessage, MessageType
from src.services import SessionService
from src.utils import get_logger

logger = get_logger(__name__)

ws_router = APIRouter()


# ============================================================================
# Dependency Injection
# ============================================================================


def get_session_service(settings: Annotated[Settings, Depends(get_settings)]) -> SessionService:
    """Get Session service instance (singleton)."""
    if not hasattr(get_session_service, "_instance"):
        get_session_service._instance = SessionService(settings)
    return get_session_service._instance


# ============================================================================
# WebSocket Endpoints
# ============================================================================


@ws_router.websocket("/ws/duo/{session_id}")
async def websocket_duo_mode(
    websocket: WebSocket,
    session_id: str,
    user_id: str = Query(..., description="User ID"),
    session_service: SessionService = Depends(get_session_service),
):
    """
    WebSocket endpoint for Duo mode real-time collaboration.

    Messages format:
    {
        "type": "question" | "answer" | "suggestion" | "join" | "leave",
        "content": "message content",
        "user_id": "sender_user_id",
        "session_id": "session_id"
    }
    """
    await websocket.accept()

    try:
        # Connect to session
        await session_service.connect_websocket(session_id, user_id, websocket)

        logger.info(
            "WebSocket connected to Duo session",
            session_id=session_id,
            user_id=user_id,
        )

        # Send join message to all participants
        join_message = DuoMessage(
            type=MessageType.JOIN,
            content=f"User {user_id} joined the session",
            user_id=user_id,
            session_id=session_id,
        )
        await session_service.broadcast_message(join_message)

        # Listen for messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Create DuoMessage
            message = DuoMessage(
                type=MessageType(data.get("type", "question")),
                content=data.get("content", ""),
                user_id=user_id,
                session_id=session_id,
            )

            # Broadcast to all participants
            await session_service.broadcast_message(message)

    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected from Duo session",
            session_id=session_id,
            user_id=user_id,
        )

        # Disconnect from session
        await session_service.disconnect_websocket(session_id, user_id)

        # Send leave message to remaining participants
        leave_message = DuoMessage(
            type=MessageType.LEAVE,
            content=f"User {user_id} left the session",
            user_id=user_id,
            session_id=session_id,
        )
        await session_service.broadcast_message(leave_message)

    except Exception as e:
        logger.error(
            "Error in Duo mode WebSocket",
            session_id=session_id,
            user_id=user_id,
            error=str(e),
        )
        await websocket.close(code=1011, reason=str(e))


@ws_router.websocket("/ws/audio")
async def websocket_audio_stream(
    websocket: WebSocket,
):
    """
    WebSocket endpoint for real-time audio streaming and transcription.

    Client sends: Binary audio chunks
    Server responds: {"transcription": "text", "is_final": true/false, "confidence": 0.95}
    """
    await websocket.accept()

    logger.info("WebSocket connected for audio streaming")

    try:
        # Note: Full implementation would use AudioService.transcribe_audio_stream()
        # For now, this is a placeholder that echoes back acknowledgment

        while True:
            # Receive audio chunk
            audio_data = await websocket.receive_bytes()

            logger.debug(
                "Received audio chunk",
                size_bytes=len(audio_data),
            )

            # TODO: Implement real-time transcription
            # For MVP, we'll use file upload transcription instead
            # Full streaming would require:
            # 1. Audio buffer management
            # 2. VAD (Voice Activity Detection) to detect speech chunks
            # 3. Incremental transcription with Faster Whisper
            # 4. Send partial results back to client

            # Send acknowledgment
            await websocket.send_json({
                "status": "received",
                "size": len(audio_data),
                "message": "Use POST /api/v1/audio/transcribe for transcription"
            })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected from audio streaming")

    except Exception as e:
        logger.error("Error in audio WebSocket", error=str(e))
        await websocket.close(code=1011, reason=str(e))


@ws_router.websocket("/ws/chat/{session_id}")
async def websocket_chat_stream(
    websocket: WebSocket,
    session_id: str,
):
    """
    WebSocket endpoint for streaming AI chat responses.

    Client sends: {"message": "question", "context": [...]}
    Server streams: {"chunk": "response text", "done": false}
    """
    await websocket.accept()

    logger.info(
        "WebSocket connected for chat streaming",
        session_id=session_id,
    )

    try:
        # Note: Full implementation would use OpenAIService.chat_completion_stream()
        # For MVP, clients can use standard POST /chat/completions endpoint

        while True:
            data = await websocket.receive_json()

            logger.info(
                "Received chat request via WebSocket",
                session_id=session_id,
                message_length=len(data.get("message", "")),
            )

            # Send response
            await websocket.send_json({
                "status": "received",
                "message": "Use POST /api/v1/chat/completions with stream=true for streaming"
            })

    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected from chat streaming",
            session_id=session_id,
        )

    except Exception as e:
        logger.error("Error in chat WebSocket", error=str(e), session_id=session_id)
        await websocket.close(code=1011, reason=str(e))
