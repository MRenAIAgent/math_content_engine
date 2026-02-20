"""
Gemini (Google Vertex AI) LLM client implementation.

Uses Application Default Credentials (ADC) — no API key needed.
On Cloud Run: authenticates via service account automatically.
Locally: uses `gcloud auth application-default login`.
"""

import logging
from typing import Optional

from .base import BaseLLMClient, LLMResponse

logger = logging.getLogger(__name__)


class GeminiClient(BaseLLMClient):
    """LLM client for Google Gemini models via Vertex AI."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        api_key: str = "",  # Not used — ADC handles auth
    ):
        super().__init__(api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens)
        self.project_id = project_id
        self.location = location
        self._model_client = None

    def _init_vertexai(self):
        """One-time Vertex AI SDK initialization."""
        if not hasattr(self, "_vertexai_initialized"):
            import vertexai

            vertexai.init(project=self.project_id, location=self.location)
            self._vertexai_initialized = True
            logger.info(
                "Initialized Vertex AI project=%s location=%s",
                self.project_id, self.location,
            )

    def _get_model(self, system_instruction: Optional[str] = None):
        """Get or create a GenerativeModel, optionally with a system instruction.

        The Vertex AI SDK requires system_instruction to be set at model
        construction time, not at generate_content() call time.  When a
        system prompt is provided we create a fresh model instance.
        """
        from vertexai.generative_models import GenerativeModel

        self._init_vertexai()

        if system_instruction:
            # Create a new model with the system instruction baked in
            return GenerativeModel(self.model, system_instruction=system_instruction)

        # Re-use the cached default model (no system instruction)
        if self._model_client is None:
            self._model_client = GenerativeModel(self.model)
            logger.info("Initialized Gemini model=%s", self.model)
        return self._model_client

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        *,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a response using Gemini via Vertex AI.

        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction
            max_tokens: Override the default max_tokens if provided
            temperature: Override the default temperature if provided
            json_mode: Accepted for API compatibility; Gemini support via
                GenerationConfig.response_mime_type can be added later.
        """
        from vertexai.generative_models import GenerationConfig

        # json_mode accepted for API compatibility; Gemini support via
        # GenerationConfig.response_mime_type can be added later.

        model = self._get_model(system_instruction=system_prompt)

        gen_config = GenerationConfig(
            max_output_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
        )

        response = model.generate_content(
            prompt,
            generation_config=gen_config,
        )

        # Extract usage metadata
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            usage = {
                "input_tokens": getattr(um, "prompt_token_count", 0),
                "output_tokens": getattr(um, "candidates_token_count", 0),
                "total_tokens": getattr(um, "total_token_count", 0),
            }

        # Extract finish reason
        finish_reason = None
        if response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "finish_reason"):
                finish_reason = str(candidate.finish_reason)

        return LLMResponse(
            content=response.text,
            model=self.model,
            usage=usage,
            finish_reason=finish_reason,
        )

    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        error_context: Optional[str] = None,
    ) -> LLMResponse:
        """Generate a response with error context for code correction."""
        if error_context:
            retry_prompt = f"""{prompt}

---
PREVIOUS ATTEMPT FAILED WITH ERROR:
{error_context}

Please fix the code to resolve this error. Return ONLY the corrected Python code."""
        else:
            retry_prompt = prompt

        return self.generate(retry_prompt, system_prompt)
