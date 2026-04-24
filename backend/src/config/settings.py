"""
Configuration management using Pydantic Settings.
Extended for LockedIn AI with audio, vision, and session management.
"""
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation and type safety."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Azure OpenAI Configuration
    azure_openai_api_key: str = Field(..., description="Azure OpenAI API Key")
    azure_openai_endpoint: str = Field(..., description="Azure OpenAI Endpoint URL")
    azure_openai_api_version: str = Field(
        default="2024-10-21",
        description="Azure OpenAI API Version"
    )
    azure_openai_deployment_name: str = Field(
        default="gpt-5.4-nano",
        description="Azure OpenAI Deployment Name"
    )

    # Faster Whisper Configuration (Local Speech-to-Text)
    whisper_model: str = Field(
        default="base",
        description="Whisper model size: tiny, base, small, medium, large"
    )
    whisper_device: str = Field(default="cpu", description="Device: cpu or cuda")
    whisper_compute_type: str = Field(
        default="int8",
        description="Compute type: int8, int16, float16, float32"
    )

    # Azure Computer Vision (Optional - can use GPT-5.4-nano Vision instead)
    azure_vision_api_key: str = Field(default="", description="Azure Vision API Key")
    azure_vision_endpoint: str = Field(default="", description="Azure Vision Endpoint")

    # Application Configuration
    app_name: str = Field(default="LockedIn AI Backend")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)

    # Security
    api_key: str = Field(..., description="API Key for authentication")
    allowed_origins: str = Field(
        default="chrome-extension://*,http://localhost:3000,http://localhost:8000"
    )

    # Session Management
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    max_context_messages: int = Field(default=20, description="Max messages in context")
    session_invite_code_length: int = Field(default=8, description="Invite code length")

    # Redis Configuration (Optional)
    redis_url: str = Field(default="redis://localhost:6379", description="Redis URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_max_connections: int = Field(default=10, description="Max Redis connections")

    # Rate Limiting
    rate_limit_requests: int = Field(default=100)
    rate_limit_period: int = Field(default=60)

    # Audio Configuration
    audio_max_duration_seconds: int = Field(default=300, description="Max audio duration")
    audio_sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    audio_format: str = Field(default="wav", description="Audio format")

    # Vision Configuration
    vision_max_image_size_mb: int = Field(default=10, description="Max image size in MB")
    vision_supported_formats: str = Field(
        default="jpg,jpeg,png,gif,webp",
        description="Supported image formats"
    )

    @field_validator("azure_openai_endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Remove trailing slash if present (Azure SDK adds paths automatically)."""
        if v.endswith("/"):
            return v.rstrip("/")
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins into a list."""
        origins = [origin.strip() for origin in self.allowed_origins.split(",")]
        # Handle chrome-extension://* wildcard
        return origins

    @property
    def vision_supported_formats_list(self) -> List[str]:
        """Parse supported image formats into a list."""
        return [fmt.strip() for fmt in self.vision_supported_formats.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"

    @property
    def use_redis(self) -> bool:
        """Check if Redis should be used for session storage."""
        return self.redis_url.startswith("redis://")


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Follows Dependency Injection pattern.
    """
    return Settings()
