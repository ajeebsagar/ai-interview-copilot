"""
Azure OpenAI Service Implementation for LockedIn AI.
Includes chat completion and vision API support.
"""
import base64
import json
from typing import Any, AsyncIterator, Dict, List

from openai import APIError
from openai import AuthenticationError as OpenAIAuthError
from openai import AsyncAzureOpenAI
from openai import RateLimitError as OpenAIRateLimitError

from src.config import Settings
from src.models import ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from src.utils import AIServiceError, AuthenticationError, get_logger

logger = get_logger(__name__)


class AzureOpenAIService:
    """
    Azure OpenAI service with chat and vision capabilities.
    Supports GPT-5.4-nano for both text and image understanding.
    """

    def __init__(self, settings: Settings):
        """
        Initialize Azure OpenAI service.

        Args:
            settings: Application settings with Azure credentials
        """
        self.settings = settings
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.deployment_name = settings.azure_openai_deployment_name

        logger.info(
            "Azure OpenAI service initialized",
            deployment=self.deployment_name,
            endpoint=settings.azure_openai_endpoint,
        )

    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """
        Generate a chat completion.

        Args:
            request: Chat request with messages and parameters

        Returns:
            ChatCompletionResponse with generated completion

        Raises:
            AuthenticationError: If authentication fails
            AIServiceError: For other API errors
        """
        try:
            logger.info(
                "Creating chat completion",
                message_count=len(request.messages),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                session_id=request.session_id,
            )

            # Convert Pydantic models to dicts
            messages = [
                {
                    "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                    "content": msg.content
                }
                for msg in request.messages
            ]

            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=False,
            )

            content = response.choices[0].message.content
            logger.info(
                "Chat completion created successfully",
                completion_id=response.id,
                content_length=len(content) if content else 0,
            )

            return ChatCompletionResponse(
                content=content or "",
                session_id=request.session_id,
                context_used=len(request.messages),
            )

        except OpenAIAuthError as e:
            logger.error("Authentication failed", error=str(e))
            raise AuthenticationError(str(e))

        except OpenAIRateLimitError as e:
            logger.error("Rate limit exceeded", error=str(e))
            raise AIServiceError(f"Rate limit exceeded: {str(e)}")

        except APIError as e:
            logger.error("Azure OpenAI API error", error=str(e))
            raise AIServiceError(f"Azure OpenAI API error: {str(e)}")

        except Exception as e:
            logger.error("Unexpected error in chat completion", error=str(e))
            raise AIServiceError(f"Unexpected error: {str(e)}")

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[str]:
        """
        Generate a streaming chat completion.

        Args:
            request: Chat request with messages and parameters

        Yields:
            Text chunks from the completion

        Raises:
            AuthenticationError: If authentication fails
            AIServiceError: For other API errors
        """
        try:
            logger.info(
                "Creating streaming chat completion",
                message_count=len(request.messages),
                session_id=request.session_id,
            )

            # Convert Pydantic models to dicts
            messages = [
                {
                    "role": msg.role.value if hasattr(msg.role, "value") else msg.role,
                    "content": msg.content
                }
                for msg in request.messages
            ]

            stream = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content

            logger.info("Streaming chat completion completed successfully")

        except OpenAIAuthError as e:
            logger.error("Authentication failed", error=str(e))
            raise AuthenticationError(str(e))

        except OpenAIRateLimitError as e:
            logger.error("Rate limit exceeded", error=str(e))
            raise AIServiceError(f"Rate limit exceeded: {str(e)}")

        except APIError as e:
            logger.error("Azure OpenAI API error", error=str(e))
            raise AIServiceError(f"Azure OpenAI API error: {str(e)}")

        except Exception as e:
            logger.error("Unexpected error in streaming", error=str(e))
            raise AIServiceError(f"Unexpected error: {str(e)}")

    async def analyze_image(
        self, image_data: bytes, prompt: str = "Extract all text and code from this image."
    ) -> Dict[str, Any]:
        """
        Analyze an image using GPT-5.4-nano Vision API.

        Args:
            image_data: Image bytes
            prompt: Analysis prompt

        Returns:
            Dict with analysis results

        Raises:
            AIServiceError: If analysis fails
        """
        try:
            logger.info("Analyzing image with GPT-5.4-nano Vision", prompt_length=len(prompt))

            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode("utf-8")

            # Create vision message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ]

            response = await self.client.chat.completions.create(
                model=self.deployment_name,  # GPT-5.4-nano supports vision
                messages=messages,
                max_tokens=2000,
            )

            content = response.choices[0].message.content
            logger.info(
                "Image analysis completed",
                response_length=len(content) if content else 0,
            )

            return {"content": content or "", "success": True}

        except Exception as e:
            logger.error("Image analysis failed", error=str(e))
            raise AIServiceError(f"Image analysis failed: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if Azure OpenAI service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
            )
            return response.id is not None

        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return False
