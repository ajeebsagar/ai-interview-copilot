"""
Pydantic models for request/response validation.
Extended for LockedIn AI with audio, vision, and session support.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Enums
# ============================================================================

class MessageRole(str, Enum):
    """Chat message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class QuestionType(str, Enum):
    """Types of interview questions."""
    CODING = "coding"
    SYSTEM_DESIGN = "system_design"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"


class SessionStatus(str, Enum):
    """Session status for Duo mode."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class MessageType(str, Enum):
    """WebSocket message types."""
    QUESTION = "question"
    ANSWER = "answer"
    SUGGESTION = "suggestion"
    JOIN = "join"
    LEAVE = "leave"
    TRANSCRIPTION = "transcription"
    ERROR = "error"


# ============================================================================
# Chat Models
# ============================================================================

class ChatMessage(BaseModel):
    """Single chat message."""
    role: MessageRole
    content: str


class ChatCompletionRequest(BaseModel):
    """Request for chat completion."""
    messages: List[ChatMessage]
    session_id: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=4000)
    stream: bool = False


class ChatCompletionResponse(BaseModel):
    """Response for chat completion."""
    content: str
    session_id: Optional[str] = None
    context_used: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Audio Models
# ============================================================================

class AudioTranscriptionRequest(BaseModel):
    """Request for audio transcription."""
    language: str = Field(default="en", description="Language code (en, es, fr, etc.)")
    session_id: Optional[str] = None


class AudioTranscriptionResponse(BaseModel):
    """Response for audio transcription."""
    transcription: str
    confidence: Optional[float] = None
    duration_seconds: Optional[float] = None
    session_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AudioStreamMessage(BaseModel):
    """WebSocket message for audio streaming."""
    type: MessageType = MessageType.TRANSCRIPTION
    transcription: str
    is_final: bool = False
    confidence: Optional[float] = None


# ============================================================================
# Vision Models
# ============================================================================

class VisionAnalysisRequest(BaseModel):
    """Request for vision analysis (screenshot OCR)."""
    include_code: bool = Field(default=True, description="Extract code snippets")
    question_type: Optional[QuestionType] = None


class VisionAnalysisResponse(BaseModel):
    """Response for vision analysis."""
    question: str
    code_snippet: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    difficulty: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    raw_text: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Session Models (Duo Mode)
# ============================================================================

class SessionCreateRequest(BaseModel):
    """Request to create a new session."""
    user_id: str
    session_name: Optional[str] = None


class SessionCreateResponse(BaseModel):
    """Response for session creation."""
    session_id: str
    invite_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime


class SessionJoinRequest(BaseModel):
    """Request to join an existing session."""
    invite_code: str
    user_id: str


class SessionJoinResponse(BaseModel):
    """Response for session join."""
    session_id: str
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    participants: List[str] = Field(default_factory=list)


class SessionInfoResponse(BaseModel):
    """Session information."""
    session_id: str
    status: SessionStatus
    participants: List[str]
    created_at: datetime
    expires_at: datetime
    message_count: int = 0


class DuoMessage(BaseModel):
    """Message in Duo mode."""
    type: MessageType
    content: str
    user_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Context Models
# ============================================================================

class ContextMessage(BaseModel):
    """Message stored in context."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextSummary(BaseModel):
    """Summary of conversation context."""
    session_id: str
    message_count: int
    token_count: int
    summary: Optional[str] = None
    key_topics: List[str] = Field(default_factory=list)


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    services: Dict[str, str] = Field(default_factory=dict)


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
