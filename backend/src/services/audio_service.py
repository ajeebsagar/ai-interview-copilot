"""
Audio Service Implementation using Faster Whisper.
Provides local, CPU-based speech-to-text transcription.
"""
import io
import tempfile
from pathlib import Path
from typing import Optional

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    WhisperModel = None

from src.config import Settings
from src.models import AudioTranscriptionRequest, AudioTranscriptionResponse
from src.utils import AIServiceError, get_logger

logger = get_logger(__name__)


class AudioService:
    """
    Audio transcription service using Faster Whisper.
    Runs locally on CPU - no external API calls required.
    """

    def __init__(self, settings: Settings):
        """
        Initialize Faster Whisper model.

        Args:
            settings: Application settings with Whisper configuration

        Available models (accuracy vs speed trade-off):
        - tiny: Fastest, least accurate (~1GB)
        - base: Good balance (recommended for most use cases)
        - small: Better accuracy, slower
        - medium: High accuracy, much slower
        - large: Best accuracy, very slow
        """
        self.settings = settings

        if not WHISPER_AVAILABLE:
            logger.warning("Faster Whisper not available - using mock mode for testing")
            self.model = None
            return

        logger.info(
            "Initializing Faster Whisper",
            model=settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )

        try:
            # Initialize Faster Whisper model
            self.model = WhisperModel(
                model_size_or_path=settings.whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )

            logger.info("Faster Whisper model loaded successfully")

        except Exception as e:
            logger.error("Failed to load Whisper model", error=str(e))
            logger.warning("Falling back to mock mode")
            self.model = None

    async def transcribe_audio_file(
        self,
        audio_file_path: str,
        language: str = "en",
    ) -> AudioTranscriptionResponse:
        """
        Transcribe audio from a file.

        Args:
            audio_file_path: Path to audio file (wav, mp3, etc.)
            language: Language code (en, es, fr, etc.)

        Returns:
            AudioTranscriptionResponse with transcription and metadata

        Raises:
            AIServiceError: If transcription fails
        """
        try:
            logger.info(
                "Transcribing audio file",
                file_path=audio_file_path,
                language=language,
            )

            # Mock mode for testing
            if self.model is None:
                logger.warning("Using mock transcription (Whisper not available)")
                return AudioTranscriptionResponse(
                    transcription="[MOCK] This is a test transcription. Faster Whisper is not installed.",
                    confidence=0.95,
                    duration_seconds=5.0,
                )

            # Transcribe using Faster Whisper
            segments, info = self.model.transcribe(
                audio_file_path,
                language=language if language != "auto" else None,
                vad_filter=True,  # Voice activity detection
                beam_size=5,
            )

            # Collect all segments
            full_transcription = ""
            total_duration = 0.0

            for segment in segments:
                full_transcription += segment.text + " "
                total_duration = max(total_duration, segment.end)

            full_transcription = full_transcription.strip()

            logger.info(
                "Audio transcription completed",
                transcription_length=len(full_transcription),
                duration_seconds=total_duration,
                detected_language=info.language,
                confidence=info.language_probability,
            )

            return AudioTranscriptionResponse(
                transcription=full_transcription,
                confidence=info.language_probability,
                duration_seconds=total_duration,
            )

        except Exception as e:
            logger.error("Audio transcription failed", error=str(e))
            raise AIServiceError(f"Transcription failed: {str(e)}")

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        language: str = "en",
        audio_format: str = "wav",
    ) -> AudioTranscriptionResponse:
        """
        Transcribe audio from bytes.

        Args:
            audio_bytes: Audio data as bytes
            language: Language code
            audio_format: Audio format (wav, mp3, etc.)

        Returns:
            AudioTranscriptionResponse with transcription

        Raises:
            AIServiceError: If transcription fails
        """
        try:
            logger.info(
                "Transcribing audio bytes",
                size_bytes=len(audio_bytes),
                language=language,
                format=audio_format,
            )

            # Write bytes to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=f".{audio_format}",
                delete=False
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            try:
                # Transcribe the temporary file
                response = await self.transcribe_audio_file(
                    temp_path,
                    language=language,
                )
                return response

            finally:
                # Clean up temporary file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error("Audio bytes transcription failed", error=str(e))
            raise AIServiceError(f"Transcription failed: {str(e)}")

    async def transcribe_audio_stream(
        self,
        audio_chunk: bytes,
        language: str = "en",
    ) -> Optional[str]:
        """
        Transcribe a chunk of streaming audio.

        Note: For true real-time streaming, you'd accumulate chunks
        and transcribe when you have enough data (e.g., 1-3 seconds).
        This is a simplified version that transcribes each chunk.

        Args:
            audio_chunk: Audio data chunk
            language: Language code

        Returns:
            Transcription text if successful, None otherwise

        Raises:
            AIServiceError: If transcription fails
        """
        try:
            # For streaming, we need at least some audio data
            if len(audio_chunk) < 1000:  # Minimum bytes threshold
                return None

            response = await self.transcribe_audio_bytes(
                audio_chunk,
                language=language,
                audio_format="wav",
            )

            return response.transcription

        except Exception as e:
            logger.error("Stream transcription failed", error=str(e))
            # Don't raise for streaming - just return None
            return None

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages.

        Returns:
            List of language codes
        """
        # Whisper supports 99 languages
        return [
            "en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja",
            "ko", "ar", "hi", "tr", "pl", "uk", "vi", "id", "th", "fa",
            # ... (full list available in Whisper docs)
        ]

    async def health_check(self) -> bool:
        """
        Check if audio service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Quick test to verify model is loaded
            return self.model is not None
        except Exception as e:
            logger.error("Audio service health check failed", error=str(e))
            return False
