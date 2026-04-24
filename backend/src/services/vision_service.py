"""
Vision Service Implementation using GPT-5.4-nano Vision API.
Provides screenshot OCR and question extraction for coding interviews.
"""
import json
import re
from typing import Any, Dict, List

from src.config import Settings
from src.models import QuestionType, VisionAnalysisRequest, VisionAnalysisResponse
from src.services.azure_openai_service import AzureOpenAIService
from src.utils import AIServiceError, get_logger

logger = get_logger(__name__)


class VisionService:
    """
    Vision service for analyzing screenshots and extracting interview questions.
    Uses GPT-5.4-nano Vision API for intelligent OCR and question parsing.
    """

    def __init__(self, settings: Settings, openai_service: AzureOpenAIService):
        """
        Initialize vision service.

        Args:
            settings: Application settings
            openai_service: Azure OpenAI service for vision API
        """
        self.settings = settings
        self.openai_service = openai_service

        logger.info("Vision service initialized")

    async def analyze_screenshot(
        self,
        image_data: bytes,
        request: VisionAnalysisRequest,
    ) -> VisionAnalysisResponse:
        """
        Analyze a screenshot and extract interview question.

        Args:
            image_data: Screenshot image bytes
            request: Analysis request with options

        Returns:
            VisionAnalysisResponse with extracted question data

        Raises:
            AIServiceError: If analysis fails
        """
        try:
            logger.info(
                "Analyzing screenshot",
                image_size=len(image_data),
                include_code=request.include_code,
                question_type=request.question_type,
            )

            # Build analysis prompt
            prompt = self._build_analysis_prompt(request)

            # Call GPT-5.4-nano Vision API
            result = await self.openai_service.analyze_image(
                image_data=image_data,
                prompt=prompt,
            )

            # Parse the response
            response = self._parse_vision_response(
                result["content"],
                request.include_code,
            )

            logger.info(
                "Screenshot analysis completed",
                question_length=len(response.question),
                has_code=bool(response.code_snippet),
                constraints_count=len(response.constraints),
            )

            return response

        except Exception as e:
            logger.error("Screenshot analysis failed", error=str(e))
            raise AIServiceError(f"Vision analysis failed: {str(e)}")

    def _build_analysis_prompt(self, request: VisionAnalysisRequest) -> str:
        """
        Build the analysis prompt based on request options.

        Args:
            request: Vision analysis request

        Returns:
            Prompt string for GPT-5.4-nano Vision
        """
        base_prompt = """
You are an expert at analyzing coding interview screenshots.
Extract ALL information from this image and structure it as JSON.

Extract:
1. The main question/problem statement
2. Code snippets (if present)
3. Constraints (time limits, space limits, etc.)
4. Example inputs and outputs
5. Difficulty level (if shown)
6. Tags or categories (if shown)

Format your response as JSON:
{
  "question": "Full problem statement",
  "code_snippet": "Code if present, otherwise null",
  "constraints": ["constraint1", "constraint2", ...],
  "examples": [
    {"input": "...", "output": "...", "explanation": "..."}
  ],
  "difficulty": "Easy/Medium/Hard or null",
  "tags": ["array", "hash-map", etc.],
  "raw_text": "Complete extracted text"
}

Be thorough and extract ALL visible text.
"""

        if request.question_type == QuestionType.CODING:
            base_prompt += "\nThis is a coding/algorithm question. Pay special attention to code snippets and complexity requirements."
        elif request.question_type == QuestionType.SYSTEM_DESIGN:
            base_prompt += "\nThis is a system design question. Focus on requirements, scale, and architecture."
        elif request.question_type == QuestionType.BEHAVIORAL:
            base_prompt += "\nThis is a behavioral question. Extract the scenario and what's being assessed."

        if not request.include_code:
            base_prompt += "\nDo not extract code snippets - set code_snippet to null."

        return base_prompt

    def _parse_vision_response(
        self, content: str, include_code: bool
    ) -> VisionAnalysisResponse:
        """
        Parse GPT-5.4-nano Vision response into structured format.

        Args:
            content: Raw response from vision API
            include_code: Whether to include code snippets

        Returns:
            VisionAnalysisResponse with parsed data
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Fallback: treat entire content as question
                data = {
                    "question": content,
                    "code_snippet": None,
                    "constraints": [],
                    "examples": [],
                    "difficulty": None,
                    "tags": [],
                    "raw_text": content,
                }

            # Build response
            return VisionAnalysisResponse(
                question=data.get("question", content),
                code_snippet=data.get("code_snippet") if include_code else None,
                constraints=data.get("constraints", []),
                examples=data.get("examples", []),
                difficulty=data.get("difficulty"),
                tags=data.get("tags", []),
                raw_text=data.get("raw_text", content),
            )

        except Exception as e:
            logger.warning("Failed to parse vision response as JSON", error=str(e))

            # Fallback: return raw content as question
            return VisionAnalysisResponse(
                question=content,
                code_snippet=None,
                constraints=[],
                examples=[],
                difficulty=None,
                tags=[],
                raw_text=content,
            )

    async def extract_text_only(self, image_data: bytes) -> str:
        """
        Extract only text from image (simple OCR).

        Args:
            image_data: Image bytes

        Returns:
            Extracted text

        Raises:
            AIServiceError: If extraction fails
        """
        try:
            prompt = "Extract ALL text from this image. Return only the text, no formatting or explanation."

            result = await self.openai_service.analyze_image(
                image_data=image_data,
                prompt=prompt,
            )

            return result["content"]

        except Exception as e:
            logger.error("Text extraction failed", error=str(e))
            raise AIServiceError(f"Text extraction failed: {str(e)}")

    async def health_check(self) -> bool:
        """
        Check if vision service is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            # Vision service health depends on OpenAI service
            return await self.openai_service.health_check()
        except Exception as e:
            logger.error("Vision service health check failed", error=str(e))
            return False
