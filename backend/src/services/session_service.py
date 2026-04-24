"""
Session Service for managing Duo mode collaborative sessions.
Handles WebSocket connections, session state, and message broadcasting.
"""
import asyncio
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from fastapi import WebSocket

from src.config import Settings
from src.models import (
    DuoMessage,
    MessageType,
    SessionCreateRequest,
    SessionCreateResponse,
    SessionInfoResponse,
    SessionJoinRequest,
    SessionJoinResponse,
    SessionStatus,
)
from src.utils import AIServiceError, get_logger

logger = get_logger(__name__)


class Session:
    """Represents a Duo mode session."""

    def __init__(
        self,
        session_id: str,
        invite_code: str,
        creator_id: str,
        timeout_seconds: int,
    ):
        self.session_id = session_id
        self.invite_code = invite_code
        self.creator_id = creator_id
        self.participants: Set[str] = {creator_id}
        self.connections: Dict[str, WebSocket] = {}
        self.messages: List[DuoMessage] = []
        self.created_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        self.status = SessionStatus.ACTIVE

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def add_participant(self, user_id: str):
        """Add a participant to the session."""
        self.participants.add(user_id)

    def remove_participant(self, user_id: str):
        """Remove a participant from the session."""
        self.participants.discard(user_id)
        if user_id in self.connections:
            del self.connections[user_id]

    def add_connection(self, user_id: str, websocket: WebSocket):
        """Add a WebSocket connection for a user."""
        self.connections[user_id] = websocket

    def remove_connection(self, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.connections:
            del self.connections[user_id]

    def add_message(self, message: DuoMessage):
        """Add a message to session history."""
        self.messages.append(message)


class SessionService:
    """
    Service for managing Duo mode sessions.
    Handles session lifecycle, participant management, and message broadcasting.
    """

    def __init__(self, settings: Settings):
        """
        Initialize session service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.sessions: Dict[str, Session] = {}  # session_id -> Session
        self.invite_codes: Dict[str, str] = {}  # invite_code -> session_id

        logger.info("Session service initialized")

        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_sessions())

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return secrets.token_urlsafe(16)

    def _generate_invite_code(self) -> str:
        """Generate a random invite code."""
        length = self.settings.session_invite_code_length
        characters = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))

    async def create_session(
        self, request: SessionCreateRequest
    ) -> SessionCreateResponse:
        """
        Create a new Duo session.

        Args:
            request: Session creation request

        Returns:
            SessionCreateResponse with session details

        Raises:
            AIServiceError: If creation fails
        """
        try:
            session_id = self._generate_session_id()
            invite_code = self._generate_invite_code()

            # Create session
            session = Session(
                session_id=session_id,
                invite_code=invite_code,
                creator_id=request.user_id,
                timeout_seconds=self.settings.session_timeout,
            )

            self.sessions[session_id] = session
            self.invite_codes[invite_code] = session_id

            logger.info(
                "Session created",
                session_id=session_id,
                invite_code=invite_code,
                creator_id=request.user_id,
            )

            return SessionCreateResponse(
                session_id=session_id,
                invite_code=invite_code,
                expires_at=session.expires_at,
            )

        except Exception as e:
            logger.error("Failed to create session", error=str(e))
            raise AIServiceError(f"Session creation failed: {str(e)}")

    async def join_session(
        self, session_id: str, request: SessionJoinRequest
    ) -> SessionJoinResponse:
        """
        Join an existing session.

        Args:
            session_id: Session ID to join
            request: Join request with invite code

        Returns:
            SessionJoinResponse with join details

        Raises:
            AIServiceError: If join fails
        """
        try:
            # Verify invite code
            if request.invite_code not in self.invite_codes:
                raise AIServiceError("Invalid invite code")

            actual_session_id = self.invite_codes[request.invite_code]
            if actual_session_id != session_id:
                raise AIServiceError("Session ID mismatch")

            session = self.sessions.get(session_id)
            if not session:
                raise AIServiceError("Session not found")

            if session.is_expired():
                raise AIServiceError("Session has expired")

            # Add participant
            session.add_participant(request.user_id)

            logger.info(
                "User joined session",
                session_id=session_id,
                user_id=request.user_id,
                total_participants=len(session.participants),
            )

            return SessionJoinResponse(
                session_id=session_id,
                participants=list(session.participants),
            )

        except AIServiceError:
            raise
        except Exception as e:
            logger.error("Failed to join session", error=str(e))
            raise AIServiceError(f"Join session failed: {str(e)}")

    async def get_session_info(self, session_id: str) -> SessionInfoResponse:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            SessionInfoResponse with session details

        Raises:
            AIServiceError: If session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            raise AIServiceError("Session not found")

        return SessionInfoResponse(
            session_id=session.session_id,
            status=SessionStatus.EXPIRED if session.is_expired() else session.status,
            participants=list(session.participants),
            created_at=session.created_at,
            expires_at=session.expires_at,
            message_count=len(session.messages),
        )

    async def connect_websocket(
        self, session_id: str, user_id: str, websocket: WebSocket
    ):
        """
        Connect a WebSocket to a session.

        Args:
            session_id: Session ID
            user_id: User ID
            websocket: WebSocket connection

        Raises:
            AIServiceError: If connection fails
        """
        session = self.sessions.get(session_id)
        if not session:
            raise AIServiceError("Session not found")

        if user_id not in session.participants:
            raise AIServiceError("User not in session")

        session.add_connection(user_id, websocket)

        logger.info(
            "WebSocket connected",
            session_id=session_id,
            user_id=user_id,
            active_connections=len(session.connections),
        )

    async def disconnect_websocket(self, session_id: str, user_id: str):
        """
        Disconnect a WebSocket from a session.

        Args:
            session_id: Session ID
            user_id: User ID
        """
        session = self.sessions.get(session_id)
        if session:
            session.remove_connection(user_id)

            logger.info(
                "WebSocket disconnected",
                session_id=session_id,
                user_id=user_id,
                active_connections=len(session.connections),
            )

    async def broadcast_message(self, message: DuoMessage):
        """
        Broadcast a message to all participants in a session.

        Args:
            message: DuoMessage to broadcast
        """
        session = self.sessions.get(message.session_id)
        if not session:
            logger.warning("Cannot broadcast - session not found", session_id=message.session_id)
            return

        # Add to message history
        session.add_message(message)

        # Broadcast to all connected participants
        disconnected = []
        for user_id, websocket in session.connections.items():
            try:
                await websocket.send_json(message.model_dump(mode="json"))
            except Exception as e:
                logger.warning(
                    "Failed to send message to user",
                    user_id=user_id,
                    error=str(e),
                )
                disconnected.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected:
            session.remove_connection(user_id)

        logger.info(
            "Message broadcasted",
            session_id=message.session_id,
            message_type=message.type,
            recipients=len(session.connections),
        )

    async def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                expired_sessions = [
                    session_id
                    for session_id, session in self.sessions.items()
                    if session.is_expired()
                ]

                for session_id in expired_sessions:
                    session = self.sessions[session_id]

                    # Remove from invite codes
                    if session.invite_code in self.invite_codes:
                        del self.invite_codes[session.invite_code]

                    # Remove session
                    del self.sessions[session_id]

                    logger.info("Expired session cleaned up", session_id=session_id)

                if expired_sessions:
                    logger.info(
                        "Cleanup completed",
                        expired_count=len(expired_sessions),
                        active_sessions=len(self.sessions),
                    )

            except Exception as e:
                logger.error("Error in session cleanup", error=str(e))

    async def health_check(self) -> bool:
        """
        Check if session service is healthy.

        Returns:
            True if healthy
        """
        return True
