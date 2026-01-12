"""
Base class for LLM clients.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Response from an LLM API call."""
    content: str
    model: str
    usage: dict
    finish_reason: Optional[str] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 4096):
        """
        Initialize the LLM client.

        Args:
            api_key: API key for authentication
            model: Model identifier to use
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt to send
            system_prompt: Optional system prompt for context

        Returns:
            LLMResponse with generated content
        """
        pass

    @abstractmethod
    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        error_context: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate a response with error context for retries.

        Args:
            prompt: Original user prompt
            system_prompt: Optional system prompt
            error_context: Error message from previous attempt

        Returns:
            LLMResponse with corrected content
        """
        pass
